from django.db import models
from django.contrib.auth.models import User

class Transcription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='audio_files/')  # For uploaded audio
    transcript = models.TextField()  # Transcribed text
    translated_text = models.TextField(blank=True, null=True)  # Optional translation
    detected_language = models.CharField(blank=True, null=True, max_length=50)  # Add this field
    target_language = models.CharField(max_length=50, null=True, blank=True, default='en')  # Add default or allow null
    timestamp = models.DateTimeField(auto_now_add=True)
    translation = models.TextField(null=True, blank=True)
    # Optionally store frequency of words or other features
    word_frequency = models.JSONField(blank=True, null=True)  # Store word frequency data (as JSON)
    top_phrases = models.JSONField(blank=True, null=True)  # Store top phrases data (as JSON)
    similarity_data = models.JSONField(blank=True, null=True)  # Store similarity detection data (as JSON)
    # class Meta:
    #     # Optional: Ensure the combination of user and audio_file is unique (if needed)
    #     constraints = [
    #         models.UniqueConstraint(fields=['user', 'audio_file'], name='unique_audio_per_user')
    #     ]

    def __str__(self):
        return f"Transcription for {self.user.username} on {self.timestamp}"
