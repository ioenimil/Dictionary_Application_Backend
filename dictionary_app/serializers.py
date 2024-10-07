# serializers.py for data validation and transformation

from rest_framework import serializers
from .models import Word

# serializer class for Word model
class WordSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Word
        fields = (
            "id",
            'word', 
            'definition', 
            'example',
            'part_of_speech',
            'added_on',
            'updated_on'
        )
        
        read_only_fields = ['added_on', 'updated_on']
        

    