# Generated by Django 5.0.3 on 2024-10-11 16:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ponp3web', '0011_genomic_transcript'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transcript',
            old_name='trancript_variation',
            new_name='transcript_variation',
        ),
    ]
