# Generated by Django 5.1.4 on 2024-12-13 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer1', '0004_transcription_similarity_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='transcription',
            name='detected_language',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
