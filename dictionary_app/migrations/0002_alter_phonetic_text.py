# Generated by Django 5.0 on 2024-10-16 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonetic',
            name='text',
            field=models.URLField(blank=True, null=True),
        ),
    ]