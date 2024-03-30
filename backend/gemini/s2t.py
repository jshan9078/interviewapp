from google.cloud import speech
import pyaudio
import os
import threading

isrecording = True
file = None  # 定义一个全局变量file

def recognizestream():
    global isrecording
    global file  # 使用全局变量file
    os.environ["GOOGLEAPPLICATION_CREDENTIALS"] = "speechtotext.json"
    client = speech.SpeechClient()

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    stream.start_stream()

    def generator():
        global is_recording
        while is_recording:
            data = stream.read(1024, exception_on_overflow=False)
            if not data:
                break
            yield speech.StreamingRecognizeRequest(audio_content=data)

    requests = generator()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US',
    )
    streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)

    responses = client.streaming_recognize(config=streaming_config, requests=requests)
    for response in responses:
        for result in response.results:
            if result.is_final:  # 只处理最终结果
                transcript = result.alternatives[0].transcript
                print(transcript)
                file.write(transcript + '\n')

def main():
    global is_recording
    global file  # 使用全局变量file

    file = open('transcription.txt', 'w')  # 在主线程中打开文件

    thread = threading.Thread(target=recognizestream)
    thread.start()

    input("Press Enter to stop recording...\n")
    is_recording = False
    thread.join()

    file.close()  # 在所有操作完成后关闭文件

if __name__ == "__main__":
    main()