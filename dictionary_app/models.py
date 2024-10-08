from django.db import models
import uuid

# Create your models here.
class Word(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False) 
    word = models.CharField(max_length=50)

    def __str__(self):
        return self.word
    
class PartOfSpeech(models.Model):
    POS_CHOICES = [
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

    name = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='meanings')
    part_of_speech = models.CharField(max_length=30, choices=POS_CHOICES)
    definition = models.TextField()
    examples = models.JSONField(blank=True, null=True, default=list)  
    synonyms = models.JSONField(blank=True, null=True, default=list)  
    antonyms = models.JSONField(blank=True, null=True, default=list)

    def __str__(self):
        return f"{self.name.word} ({self.part_of_speech})"