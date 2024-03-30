const record = require('node-record-lpcm16');

const options = {
    sampleRateHertz: 16000,
    threshold: 0,
    verbose: false,
    recordProgram: 'rec', // or 'arecord' depending on your system
    silence: '10.0',
};

const stream = record.start(options);

stream.on('data', (data) => {
    console.log('Received data', data.length);
}).on('error', console.error);
