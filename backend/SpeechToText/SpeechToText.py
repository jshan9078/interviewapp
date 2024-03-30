import os
from google.cloud import speech_v1p1beta1 as speech
import pyaudio
from six.moves import queue

# 配置Google Cloud认证
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "SpeechToText.json"

# 音频录制的配置
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class MicrophoneStream(object):
    """用于从麦克风实时获取数据的类"""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """每次回调都将音频数据放入缓冲区"""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)

def listen_print_loop(responses):
    """迭代响应并打印它们，包括说话人标签"""
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        if result.alternatives[0].words:
            speaker_tag = result.alternatives[0].words[0].speaker_tag
            if result.is_final:
                print(f"Speaker {speaker_tag}: {transcript}")
        else:
            if result.is_final:
                print(f"Transcript (Speaker unknown): {transcript}")

def main():
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code='en-US',
        enable_automatic_punctuation=True,
        enable_speaker_diarization=True,
        diarization_speaker_count=1,
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        listen_print_loop(responses)

if __name__ == '__main__':
    main()
