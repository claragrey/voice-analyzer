# from django import forms
# from .models import Transcription

# class AudioUploadForm(forms.ModelForm):
#     class Meta:
#         model = Transcription
#         fields = ['audio_file']

# analyzer/forms.py
from django import forms
from django.contrib.auth.models import User

# Custom signup form based on User model
class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def clean_password_confirmation(self):
        password = self.cleaned_data.get('password')
        password_confirmation = self.cleaned_data.get('password_confirmation')

        if password != password_confirmation:
            raise forms.ValidationError("Passwords do not match!")
        return password_confirmation

# class AudioUploadForm(forms.Form):
#     audio_file = forms.FileField(required=False) #Not required because recording is also an option
    def clean_audio_file(self):
        audio_file = self.cleaned_data.get('audio_file')
        if audio_file:
            # Check file extension
            if not audio_file.name.endswith(('.wav', '.mp3', '.ogg')):
                raise forms.ValidationError("Only .wav, .mp3, or .ogg files are allowed.")
            # Check file size
            if audio_file.size > 10 * 1024 * 1024:  # Limit size to 10 MB
                raise forms.ValidationError("The file size exceeds the 10 MB limit.")
        return audio_file

class AudioRecordForm(forms.Form):
    pass #No fields needed for this form. We will handle it in javascript.