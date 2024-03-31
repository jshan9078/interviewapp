const speech = require('@google-cloud/speech');
const record = require('node-record-lpcm16');
const { Writable } = require('stream');

process.env.GOOGLE_APPLICATION_CREDENTIALS = 'InterviewHelper.json';

const client = new speech.SpeechClient();

const config = {
    encoding: 'LINEAR16',
    sampleRateHertz: 16000,
    languageCode: 'en-US',
    enableAutomaticPunctuation: true,
    enableSpeakerDiarization: true,
    diarizationSpeakerCount: 1,
};

const streamingConfig = {
    config,
    interimResults: true,
};

let previousTranscription = '';

class MicrophoneStream extends Writable {
    constructor(options) {
        super(options);
        this.streamingRecognize = client.streamingRecognize(streamingConfig)
            .on('error', console.error)
            .on('data', (data) => {
                if (data.results[0] && data.results[0].isFinal) {
                    console.log(`Transcription: ${data.results[0].alternatives[0].transcript}`);
                }
            });
    }

    _write(chunk, encoding, callback) {
        this.streamingRecognize.write(chunk);
        callback();
    }

    _final(callback) {
        this.streamingRecognize.end();
        callback();
    }
}


console.log('Listening, press Ctrl+C to stop.');

record.start({
    sampleRateHertz: config.sampleRateHertz,
    threshold: 0,
    verbose: false,
    recordProgram: 'rec',
    silence: '10.0',
}).on('error', console.error)
    .pipe(new MicrophoneStream());
