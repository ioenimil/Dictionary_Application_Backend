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
    
    def update(self, instance, validated_data):
    # Update the main Word instance
        instance.word = validated_data.get('word', instance.word)
        instance.save()

        # Handle the nested 'meanings' field (related PartOfSpeech instances)
        meanings_data = validated_data.get('meanings')

        if meanings_data:
            # Clear existing meanings
            instance.meanings.all().delete()

            # Add the updated meanings
            for pos_data in meanings_data:
                PartOfSpeech.objects.create(
                    word=instance,  # Reference the Word instance
                    part_of_speech=pos_data.get('part_of_speech'),
                    definition=pos_data.get('definition'),
                    examples=pos_data.get('examples', []),  # Default to an empty list if not provided
                    synonyms=pos_data.get('synonyms', []),
                    antonyms=pos_data.get('antonyms', [])
                )

        return instance


