# Voice Analyzer

Voice Analyzer is a Django-based web application that transcribes speech input, translates other languages text into English, analyzes word and phrase frequency, and detects user speech similarity. This project focuses on delivering accurate transcription and translation for a variety of languages, with a strong emphasis on punctuation accuracy and fluency.

## Features

- **Audio Transcription**: Converts speech input into text in the native language of the audio.
- **Language Detection**: Automatically detects the language of the input audio.
- **Translation**: Translates the transcribed text into English. If the input audio is in English, the transcript and translation will display the same content.
- **Word and Phrase Frequency Analysis**: Provides insights into the most frequently used words and phrases.
- **Speech Similarity Detection**: Compares user speech for similarity metrics.
- **Support for Multiple Input Methods**:
  - Audio file uploads.
  - Real-time microphone recording.

## Technologies Used

- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **APIs**:
  - Google Cloud Translate (for translation)
  - Advanced Speech Recognition Systems (e.g., Google Cloud Speech-to-Text and Whisper for transcription)
  - Google Cloud SQL (for PostgreSQL)

## Setup Instructions

### Prerequisites
- Python 3.8 or above
- Django 4.0 or above
- PostgreSQL
- Google Cloud API credentials for Translate and Speech-to-Text services

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/voice-analyzer.git
   cd voice-analyzer
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Secure your credetials in '.env' :
    DATABASE_URL= <your cloud database url>
    GS_BUCKET_NAME= <your cloud bucket name>
    SECRET_KEY= <your django secret key> (in settings.py)
    USE_CLOUD_SQL_AUTH_PROXY=True

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Set up Google Cloud API credentials:
   - Download the credentials JSON file from Google Cloud Console.
   - Set the environment variable:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
     ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. Open the application in your browser:
   ```bash
    http://127.0.0.1:8000
   ```

## Usage

### Uploading Audio Files
- Use the "Upload Audio" feature to submit an audio file for transcription and analysis.

### Real-time Microphone Recording
- Click on the "Record" button to start and stop recording.
- After recording, click "Analyze" to process the audio.

### Output Display
- The native transcription is displayed next, followed by the translated text in English.
- Click on the "History" button to see the user's history
- Click on the "Analysis Report" button which contains frequency of words , phrases and similarity detection between users.

## Future Enhancements

- Improve transcription accuracy for diverse accents and dialects.
- Add support for additional languages.
- Enhance the user interface for better accessibility and usability.
- Incorporate more advanced audio processing techniques for noise reduction and clarity.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgments

- Google Cloud APIs for their robust translation and transcription services.
- OpenAI Whisper for advanced transcription capabilities.
- The Django and Python communities for their extensive support and documentation.

---

For any questions or suggestions, feel free to open an issue or contact me at antoinetteclara.mac@gmail.com.

