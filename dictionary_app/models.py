from django.db import models
from accounts.models import User

class License(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True) 
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name if self.name else "Unnamed License"

class Phonetic(models.Model):
    text = models.URLField(blank=True, default='')
    audio = models.URLField(blank=True, null=True)
    source_url = models.URLField(blank=True, null=True)  
    license = models.ForeignKey(License, on_delete=models.SET_NULL, null=True, related_name='phonetics') 

    def __str__(self):
        return self.text

class Meaning(models.Model):
    PART_OF_SPEECH_CHOICES = [
        ('noun', 'Noun'),
        ('verb', 'Verb'),
        ('adjective', 'Adjective'),
        ('adverb', 'Adverb'),
        ('pronoun', 'Pronoun'),
        ('preposition', 'Preposition'),
        ('conjunction', 'Conjunction'),
        ('interjection', 'Interjection'),
        ('article', 'Article'),
        ('determiner', 'Determiner'),
        ('numeral', 'Numeral'),
        ('particle', 'Particle'),
        ('exclamation', 'Exclamation'),
        ('auxiliary', 'Auxiliary'),
        ('modal', 'Modal'),
        ('gerund', 'Gerund'),
        ('infinitive', 'Infinitive'),
        ('participle', 'Participle'),
        ('clause', 'Clause'),
        ('phrase', 'Phrase'),
    ]

    partOfSpeech = models.CharField(max_length=30, choices=PART_OF_SPEECH_CHOICES)
    synonyms = models.JSONField(default=list, blank=True)
    antonyms = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.part_of_speech

class Definition(models.Model):
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE, related_name='definitions')
    definition = models.TextField()
    synonyms = models.JSONField(default=list, blank=True)
    antonyms = models.JSONField(default=list, blank=True)
    example = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.definition[:50] 

class DictionaryEntry(models.Model):
    word = models.CharField(max_length=100, unique=True)  # Ensure word uniqueness
    phonetics = models.ManyToManyField(Phonetic, related_name='dictionary_entries')
    meanings = models.ManyToManyField(Meaning, related_name='dictionary_entries')
    license = models.ForeignKey(License, on_delete=models.SET_NULL, null=True, related_name='dictionary_entries')  # Allow null
    source_urls = models.JSONField(default=list, blank=True)  # Allow blank and null
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dictionary_entries') 

    def __str__(self):
        return self.word
