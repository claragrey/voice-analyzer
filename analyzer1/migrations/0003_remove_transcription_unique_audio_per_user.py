# Generated by Django 5.1.4 on 2024-12-07 12:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer1', '0002_transcription_top_phrases_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='transcription',
            name='unique_audio_per_user',
        ),
    ]
