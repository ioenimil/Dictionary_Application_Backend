from rest_framework import serializers
from .models import Word, PartOfSpeech

class PartOfSpeechSerializer(serializers.ModelSerializer):
    examples = serializers.ListField(
        child=serializers.CharField(max_length=200),
        allow_empty=True
    )
    class Meta:
        model = PartOfSpeech
        fields = ('id', 
                  'part_of_speech', 
                  'definition', 
                  'examples', 
                  'synonyms', 
                  'antonyms') 

class WordSerializer(serializers.ModelSerializer):
    meanings = PartOfSpeechSerializer(many=True)
    creator = serializers.SerializerMethodField()

    class Meta:
        model = Word
        fields = ['creator', 'id', 'word', 'meanings']
    
    def get_creator(self, obj):
        return obj.user.get_name
    
    def create(self, validated_data):
        meanings_data = validated_data.pop('meanings')
        word = Word.objects.create(**validated_data)
        for pos_data in meanings_data:
            PartOfSpeech.objects.create(name=word, **pos_data)
        return word
