# Generated by Django 5.0.3 on 2024-08-09 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ponp3web', '0002_delete_csv_files'),
    ]

    operations = [
        migrations.CreateModel(
            name='Counter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('val', models.IntegerField(default=0)),
            ],
        ),
    ]
