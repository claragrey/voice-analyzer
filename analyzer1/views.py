import datetime
import json
import logging
import os  # Added for path handling
from .models import Transcription
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import SignUpForm
from pydub.exceptions import CouldntDecodeError
from pydub import AudioSegment
import tempfile
from collections import Counter
from django.db.models import F
from datetime import datetime
from django.utils.timezone import make_aware
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.http import HttpRequest, HttpResponse
import whisper  # For Whisper transcription
from google.cloud import translate_v2 as translate  # Google Translation API
import torch
import warnings
import nltk
from nltk.corpus import stopwords
from collections import Counter

warnings.filterwarnings("ignore", category=UserWarning, module="whisper.transcribe")

logger = logging.getLogger(__name__)

# # Set up paths for FFmpeg and FFprobe
# current_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of views.py
# ffmpeg_path = os.path.join(current_dir, '..', 'ffmpeg-7.1-essentials_build', 'bin', 'ffmpeg')
# ffprobe_path = os.path.join(current_dir, '..', 'ffmpeg-7.1-essentials_build', 'bin', 'ffprobe')

ffmpeg_path = 'ffmpeg'
ffprobe_path = 'ffprobe'

# Configure Pydub to use the specified FFmpeg paths
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# Initialize Whisper model once (to avoid reloading in every request)
whisper_model = whisper.load_model("large")  # Adjust model size based on your system's resources
torch.save(whisper_model.state_dict(), "whisper_large.pt")
whisper_model.load_state_dict(torch.load("whisper_large.pt"))

# Ensure the stopwords are downloaded
nltk.download('stopwords')

# Google Translation client
translate_client = translate.Client()

# User login view
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('index')
        else:
            messages.error(request, "The username or password is incorrect!")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

# Signup view
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Account created successfully!")
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

# Home page
def index(request):
    return render(request, 'index.html')

# Transcribe audio - Login required
@login_required
def transcribe(request):
    logger.info("Transcribe view called")
    if request.method == 'POST':
        try:
            logger.info("POST request received")
            transcript = ""
            translated_text = ""
            detected_language = ""

            # Check if 'audio_file' is present in the request
            if 'audio_file' in request.FILES:
                audio_file = request.FILES['audio_file']
                logger.info(f"Processing audio file: {audio_file.name}")

                # Save the uploaded file temporarily for processing
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                    temp_audio_file.write(audio_file.read())
                    temp_audio_path = temp_audio_file.name
                    temp_audio_file.close()  # Close the file after writing
                        # Convert audio to WAV format if necessary
                    try:
                        audio = AudioSegment.from_file(temp_audio_path)
                        converted_audio_path = temp_audio_path.replace(".wav", "_converted.wav")
                        audio.export(converted_audio_path, format="wav")
                        logger.info("Audio successfully converted to WAV format.")
                    except CouldntDecodeError as e:
                        logger.error(f"Error decoding audio: {e}")
                        return JsonResponse({'error': 'Invalid audio format or corrupted audio file'}, status=400)
                    
                    try:
                        # Use Whisper for transcription
                        result = whisper_model.transcribe(temp_audio_path)
                        transcript = result['text'].strip()
                        detected_language = result['language']
                        logger.info(f"Transcription successful: {transcript} (Language: {detected_language})")

                    except Exception as e:
                        logger.exception(f"Error during transcription: {e}")
                        return JsonResponse({'error': 'Failed to process transcription'}, status=500)

                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_audio_path):
                            os.remove(temp_audio_path)

            else:
                logger.error("No audio file provided in the request")
                return JsonResponse({'error': 'No audio file provided'}, status=400)

            # Perform translation if transcription exists
            if transcript:
                try:
                    if detected_language == "en":
                        translated_text = transcript  # No translation needed for English
                    else:
                        translation = translate_client.translate(
                            transcript,
                            target_language="en",
                            source_language=detected_language
                        )
                        translated_text = translation['translatedText']
                        logger.info(f"Translation successful: {translated_text}")
                except Exception as e:
                    logger.exception(f"Translation failed: {e}")
                    translated_text = "Translation failed"

            # Save the transcription to the database
            transcription = Transcription(
                user=request.user,
                transcript=transcript,
                translated_text=translated_text,
                detected_language=detected_language,
                target_language="en",
                audio_file=audio_file
            )
            try:
                transcription.save()
                logger.info("Transcription saved successfully")
                return JsonResponse({
                    'transcript': transcript,
                    'language': detected_language,
                    'translated_text': translated_text
                })
            except Exception as e:
                logger.exception(f"Error saving transcription: {e}")
                return JsonResponse({'error': f'Error saving transcription: {e}'}, status=500)

        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return JsonResponse({'error': f'An unexpected error occurred: {e}'}, status=500)

    else:
        logger.error("Invalid HTTP method")
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)
    
# History view - Login required
@login_required
def history(request):
    transcriptions = Transcription.objects.filter(user=request.user)
    return render(request, 'history.html', {
        'transcriptions': transcriptions,
        'username': request.user.username,
        'user_id': request.user.id,
    })


@login_required
def analysis_report(request):
    current_user = request.user

    # Get transcription history for the current user
    user_transcriptions = Transcription.objects.filter(user=current_user)
    all_transcriptions = Transcription.objects.exclude(user=current_user)

    # Get a list of English stop words
    stop_words = set(stopwords.words('english'))

    # Function to filter out stop words from a list of words
    def filter_stop_words(words):
        return [word for word in words if word.lower() not in stop_words]

    # Calculate word frequency for the current user
    user_word_counts = Counter()
    for transcription in user_transcriptions:
        translated_text = transcription.translated_text  # Assuming this field contains the English translation
        if translated_text:  # Ensure translated text is not None
            words = translated_text.split()
            filtered_words = filter_stop_words(words)
            user_word_counts.update(filtered_words)

    # Find the most frequently used word for the current user
    if user_word_counts:
        user_most_frequent_word, user_frequency = user_word_counts.most_common(1)[0]
    else:
        user_most_frequent_word, user_frequency = None, 0

    if user_word_counts:
        try:
            user_transcriptions.update(word_frequency=dict(user_word_counts))
        except Exception as e:
            print(f"Error updating word frequency for the user: {e}")

    # Calculate word frequency for other users using translated text
    other_users_frequency = []
    if user_most_frequent_word:
        for other_user in all_transcriptions.values('user', 'user__username').distinct():
            other_user_transcriptions = Transcription.objects.filter(user=other_user['user'])
            other_word_counts = Counter()
            for transcription in other_user_transcriptions:
                translated_text = transcription.translated_text  # Use the translated field
                if translated_text:  # Ensure translated text is not None
                    words = translated_text.split()
                    filtered_words = filter_stop_words(words)
                    other_word_counts.update(filtered_words)
            
            # Save the other user's word frequency data in the `word_frequency` field
            try:
                other_user_transcriptions.update(word_frequency=dict(other_word_counts))
            except Exception as e:
                print(f"Error updating word frequency for other users: {e}")

            other_frequency = other_word_counts.get(user_most_frequent_word, 0)
            other_users_frequency.append({
                'username': other_user['user__username'],
                'user_id': other_user['user'],
                'frequency': other_frequency
            })

    # Calculate top 3 unique phrases for the user
    unique_transcripts = set([transcription.transcript for transcription in user_transcriptions])
    all_transcripts = " ".join(unique_transcripts)
    phrases = re.split(r'[.?!]', all_transcripts)  # Split into phrases
    phrases = [phrase.strip().lower() for phrase in phrases if phrase.strip()]  # Clean up phrases
    phrase_counter = Counter(phrases)
    top_phrases = phrase_counter.most_common(3)

    # Prepare unique phrases data with transcription, translation, and timestamp
    unique_phrases_data = []
    for phrase, _ in top_phrases:
        # Find the translation for this phrase (assuming transcription has a translation field)
        matching_transcription = user_transcriptions.filter(transcript__icontains=phrase).first()
        translation = matching_transcription.translation if matching_transcription else "No translation available"
        
        unique_phrases_data.append({
            "phrase": phrase,
            "translation": translation,
            "timestamp": make_aware(datetime.now())  # Add current timestamp
        })

    formatted_top_phrases = [
        {"phrase": phrase, "frequency": count} for phrase, count in top_phrases
    ]

    # Store Top 3 Unique Phrases in the database
    user_transcriptions.update(top_phrases=json.dumps(formatted_top_phrases))


    
    # Get transcription data for all users
    all_users_transcriptions = Transcription.objects.values('user', 'user__username').annotate(
        combined_transcription=F('transcript')
    )

    # Create a mapping of users to their combined transcriptions
    user_speech = {}
    for record in all_users_transcriptions:
        user_id = record['user']
        username = record['user__username']
        transcript = record['combined_transcription']

        if user_id not in user_speech:
            user_speech[user_id] = {'username': username, 'transcripts': []}
        user_speech[user_id]['transcripts'].append(transcript)

    # Combine all transcriptions for each user into one string
    for user_id in user_speech:
        user_speech[user_id]['text'] = " ".join(user_speech[user_id]['transcripts']).lower()

    # Separate current user data and other users' data
    current_user_text = user_speech.pop(current_user.id, None)
    if not current_user_text:
        return render(request, 'analysis_report.html', {
            'error': "No transcription data available for the current user."
        })

    # Prepare data for TF-IDF
    user_ids = list(user_speech.keys())
    all_texts = [current_user_text['text']] + [user_speech[user_id]['text'] for user_id in user_ids]

    # Calculate TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Calculate cosine similarity
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

    # Match similarity scores with user IDs
    similar_users = [
        {
            'user_id': user_ids[idx],
            'username': user_speech[user_ids[idx]]['username'],
            'similarity_score': similarity_scores[idx],
            'description': f"Speech similarity score: {similarity_scores[idx]:.2f}"
        }
        for idx in range(len(user_ids))
    ]

    # Sort users by similarity score
    similar_users = sorted(similar_users, key=lambda x: x['similarity_score'], reverse=True)[:5]

    user_transcriptions.update(similarity_data=json.dumps(similar_users))

    # Pass data to the template
    context = {
        'current_user': {
            'username': current_user.username,
            'user_id': current_user.id,
            'most_frequent_word': user_most_frequent_word,
            'frequency': user_frequency,
        },
        'other_users_frequency': other_users_frequency,
        'unique_phrases_data': unique_phrases_data,
        'similar_users': similar_users,
    }

    return render(request, 'analysis_report.html', context)



# timezone_offset = int(request.POST.get('timezone_offset', '0'))  # Offset in minutes
#         utc_now = datetime.utcnow()
#         user_local_time = utc_now - datetime.timedelta(minutes=timezone_offset)