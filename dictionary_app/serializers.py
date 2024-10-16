from rest_framework import serializers
from .models import License, Phonetic, Meaning, Definition, DictionaryEntry
import re

special_characters_pattern = r'^[!@#$%^&*()_+\-=\[\]{};\'\\:"|,<.>/?`~]+$'



class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = ['id', 'name', 'url']

class PhoneticSerializer(serializers.ModelSerializer):
    license = LicenseSerializer(required=False)  
    text = serializers.URLField(required=False, allow_null=True)
    audio = serializers.URLField(required=False, allow_blank=True)
    source_url = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = Phonetic
        fields = ['id', 'text', 'audio', 'source_url', 'license']

class DefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Definition
        fields = ['id', 'definition', 'synonyms', 'antonyms', 'example'] 

class MeaningSerializer(serializers.ModelSerializer):
    definitions = DefinitionSerializer(many=True)  
    class Meta:
        model = Meaning
        fields = ['id', 'partOfSpeech', 'synonyms', 'antonyms', 'definitions']  

class DictionaryEntrySerializer(serializers.ModelSerializer):
    phonetics = PhoneticSerializer(many=True, required=False)  # Make phonetics optional
    meanings = MeaningSerializer(many=True)
    license = LicenseSerializer(required=False)
    
    class Meta:
        model = DictionaryEntry
        fields = ['id', 'word', 'phonetics', 'meanings', 'license', 'source_urls']

    def validate_word(self, value):
        print(f"Validating word: {value}") 
        if len(value) < 3:
            raise serializers.ValidationError('Word must be at least 3 characters long.')
        if value.isdigit():
            raise serializers.ValidationError('Word cannot contain only numbers.')
        if re.fullmatch(special_characters_pattern, value):
            raise serializers.ValidationError('Word cannot contain only special characters.')
        return value


    def create(self, validated_data):
        phonetics_data = validated_data.pop('phonetics', [])  # Default to an empty list if not provided
        meanings_data = validated_data.pop('meanings', [])
        license_data = validated_data.pop('license', None)

        # Create or get the License (if provided)
        if license_data:
            license_instance, created = License.objects.get_or_create(**license_data)
        else:
            license_instance = None

        # Create the DictionaryEntry
        dictionary_entry = DictionaryEntry.objects.create(license=license_instance, **validated_data)

        # Create Phonetics
        phonetic_instances = []
        for phonetic_data in phonetics_data:
            phonetic_license_data = phonetic_data.pop('license', None)
            if phonetic_license_data:
                phonetic_license, created = License.objects.get_or_create(**phonetic_license_data)
            else:
                phonetic_license = None
            phonetic_instance = Phonetic.objects.create(license=phonetic_license, **phonetic_data)
            phonetic_instances.append(phonetic_instance)

        # After creating all phonetic instances, add them to the dictionary_entry
        dictionary_entry.phonetics.set(phonetic_instances)

        # Create Meanings and Definitions
        for meaning_data in meanings_data:
            definitions_data = meaning_data.pop('definitions', [])
            meaning_instance = Meaning.objects.create(**meaning_data)
            dictionary_entry.meanings.add(meaning_instance)  # Add meaning to the dictionary_entry
            for definition_data in definitions_data:
                Definition.objects.create(meaning=meaning_instance, **definition_data)

        return dictionary_entry

    def update(self, instance, validated_data):
        phonetics_data = validated_data.pop('phonetics', None)  # Default to None if not provided
        meanings_data = validated_data.pop('meanings', None)
        license_data = validated_data.pop('license', None)

        # Update the instance with the provided data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update License if provided
        if license_data:
            instance.license, created = License.objects.get_or_create(**license_data)

        # Update phonetics if provided
        if phonetics_data is not None:
            instance.phonetics.all().delete()  # Remove existing phonetics
            phonetic_instances = []
            for phonetic_data in phonetics_data:
                phonetic_license_data = phonetic_data.pop('license', None)
                if phonetic_license_data:
                    phonetic_license, created = License.objects.get_or_create(**phonetic_license_data)
                else:
                    phonetic_license = None
                phonetic_instance = Phonetic.objects.create(license=phonetic_license, **phonetic_data)
                phonetic_instances.append(phonetic_instance)
            instance.phonetics.set(phonetic_instances)  # Add new phonetics

        # Update meanings if provided
        if meanings_data is not None:
            instance.meanings.all().delete()  # Remove existing meanings
            for meaning_data in meanings_data:
                definitions_data = meaning_data.pop('definitions', [])
                meaning_instance = Meaning.objects.create(**meaning_data)
                instance.meanings.add(meaning_instance)  # Add meaning to the dictionary_entry
                for definition_data in definitions_data:
                    Definition.objects.create(meaning=meaning_instance, **definition_data)

        instance.save()  # Save the instance
        return instance