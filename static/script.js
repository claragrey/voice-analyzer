document.addEventListener('DOMContentLoaded', () => {
    const audioUpload = document.getElementById('audioUpload');
    const recordButton = document.getElementById('recordButton');
    const stopButton = document.getElementById('stopButton');
    const analyzeButtonFile = document.getElementById('analyzeButtonFile');
    const analyzeButtonMic = document.getElementById('analyzeButtonMic');
    const transcriptDiv = document.getElementById('transcript');
    const translatedTextDiv = document.getElementById('translatedText');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    let mediaRecorder;
    let audioChunks = [];
    let audioBlob = null;

    // Prevent default form submission
    const fileUploadForm = document.getElementById('fileUploadForm');
    if (fileUploadForm) {
        fileUploadForm.onsubmit = (event) => {
            event.preventDefault(); // Stop the form from redirecting
            const formData = new FormData(fileUploadForm); // Create FormData object with form data
            analyzeAudio(formData); // Pass to analyzeAudio function
        };
    }

    // Handle file upload
    audioUpload.addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function () {
                audioBlob = new Blob([reader.result], { type: 'audio/wav' });
                analyzeButtonFile.style.display = 'block'; // Show the analyze button for file uploads
            };
            reader.readAsArrayBuffer(file);
        }
    });

    // Start recording
    recordButton.addEventListener('click', () => {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
                mediaRecorder.start();
                recordButton.disabled = true; // Disable record button
                stopButton.disabled = false; // Enable stop button
                transcriptDiv.textContent = "Recording...";
            })
            .catch(error => console.error('Error accessing microphone:', error));
    });

    // Stop recording
    stopButton.addEventListener('click', () => {
        if (mediaRecorder) {
            mediaRecorder.stop();
            stopButton.disabled = true; // Disable stop button
            recordButton.disabled = false; // Enable record button
            mediaRecorder.onstop = () => {
                audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                audioChunks = [];
                analyzeButtonMic.style.display = 'block'; // Show analyze button after recording
                transcriptDiv.textContent = "Recording stopped. Ready to analyze.";
            };
        }
    });

    // Analyze file upload
    analyzeButtonFile.addEventListener('click', async () => {
        if (audioBlob && !analyzeButtonFile.disabled) {
            analyzeButtonFile.disabled = true; // Disable button to prevent duplicate requests
            const formData = new FormData();
            formData.append('audio_file', audioBlob, 'uploaded_audio.wav');
            await analyzeAudio(formData);
            analyzeButtonFile.disabled = false; // Re-enable button after processing
        }
    });

    // Analyze microphone recording
    analyzeButtonMic.addEventListener('click', async () => {
        if (audioBlob && !analyzeButtonMic.disabled) {
            analyzeButtonMic.disabled = true; // Disable button to prevent duplicate requests
            const formData = new FormData();
            formData.append('audio_file', audioBlob, 'recording.webm');
            await analyzeAudio(formData);
            analyzeButtonMic.disabled = false; // Re-enable button after processing
        }
    });

    // Variables for loading indicators
    const loadingIndicator = document.createElement('p');
    loadingIndicator.textContent = "Processing audio, please wait...";
    loadingIndicator.style.color = "blue";

    // Function to analyze audio
    async function analyzeAudio(formData) {
        // Show loading indicator
        transcriptDiv.textContent = ""; // Clear previous text
        translatedTextDiv.textContent = "";
        transcriptDiv.appendChild(loadingIndicator);
        try {
            const response = await fetch('/transcribe/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: response.statusText }));
                throw new Error(`HTTP error ${response.status}: ${errorData.error}`);
            }

            const data = await response.json();
            // Update the UI with transcription and translation results
            transcriptDiv.textContent = `Transcript: ${data.transcript}`;
            translatedTextDiv.textContent = `Translation: ${data.translated_text}`;
        } catch (error) {
            console.error('Analysis failed:', error);
            transcriptDiv.textContent = "Error processing the audio.";
            translatedTextDiv.textContent = "";
        }
    }
});


// document.getElementById('fileUploadForm').onsubmit = (event) => {
//     const timezoneOffset = new Date().getTimezoneOffset(); // Timezone offset in minutes
//     document.getElementById('timezoneOffset').value = timezoneOffset; // Add it to the form
// };