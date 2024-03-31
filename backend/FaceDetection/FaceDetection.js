const NodeWebcam = require("node-webcam");
const vision = require('@google-cloud/vision');
const fs = require('fs');
process.env.GOOGLE_APPLICATION_CREDENTIALS = 'InterviewHelper.json';
const client = new vision.ImageAnnotatorClient();

// Default options for node-webcam
const opts = {
    width: 1280,
    height: 720,
    quality: 100,
    delay: 0,
    saveShots: true,
    output: "jpeg",
    callbackReturn: "location"
};

const Webcam = NodeWebcam.create(opts);

function detectNegativeEmotions(imagePath) {
    const image = fs.readFileSync(imagePath).toString('base64');

    client.faceDetection({ image: { content: image } })
        .then(responses => {
            const faces = responses[0].faceAnnotations;
            console.log('Faces detected:', faces.length);
            faces.forEach((face, index) => {
                console.log(`Face #${index + 1}:`);
                if (face.angerLikelihood !== 'VERY_UNLIKELY') {
                    console.log(`Anger: ${face.angerLikelihood}`);
                }
                if (face.sorrowLikelihood !== 'VERY_UNLIKELY') {
                    console.log(`Sorrow: ${face.sorrowLikelihood}`);
                }
            });
        })
        .catch(err => {
            console.error('ERROR:', err);
        });
}

setInterval(() => {
    const timestamp = Date.now();
    const imagePath = `image_${timestamp}.jpg`;

    Webcam.capture(imagePath, function(err) {
        if (err) {
            console.error(err);
        } else {
            detectNegativeEmotions(imagePath);
            // Optionally delete the image after processing
            fs.unlinkSync(imagePath);
        }
    });
}, 5000); // Process an image every 5000 milliseconds
