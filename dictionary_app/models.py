from django.db import models
import uuid

# Create your models here.
class Word(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False) 
    word = models.CharField(max_length=50)
    part_of_speech = models.CharField(max_length=50)
    definition = models.TextField()
    example = models.TextField()
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.word