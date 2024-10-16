from rest_framework import serializers
from .models import License, Phonetic, Meaning, Definition, DictionaryEntry

class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = ['id', 'name', 'url']

class PhoneticSerializer(serializers.ModelSerializer):
    license = LicenseSerializer(required=False)  

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
    phonetics = PhoneticSerializer(many=True)
    meanings = MeaningSerializer(many=True)
    license = LicenseSerializer(required=False)
    

    class Meta:
        model = DictionaryEntry
        fields = ['id', 'word', 'phonetics', 'meanings', 'license', 'source_urls']

    def create(self, validated_data):
        phonetics_data = validated_data.pop('phonetics')
        meanings_data = validated_data.pop('meanings')
        license_data = validated_data.pop('license', None)
        
        if license_data:
            license_instance, created = License.objects.get_or_create(**license_data)
        else:
            license_instance = None
        dictionary_entry = DictionaryEntry.objects.create(license=license_instance, **validated_data)

        phonetic_instances = []
        for phonetic_data in phonetics_data:
            phonetic_license_data = phonetic_data.pop('license', None)
            if phonetic_license_data:
                phonetic_license, created = License.objects.get_or_create(**phonetic_license_data)
            else:
                phonetic_license = None
            phonetic_instance = Phonetic.objects.create(license=phonetic_license, **phonetic_data)
            phonetic_instances.append(phonetic_instance)

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
        phonetics_data = validated_data.pop('phonetics', None)
        meanings_data = validated_data.pop('meanings', None)
        license_data = validated_data.pop('license', None)

        # Update the DictionaryEntry fields
        instance.word = validated_data.get('word', instance.word)
        instance.source_urls = validated_data.get('source_urls', instance.source_urls)
        
        # Update or create License (if provided)
        if license_data:
            license_instance, created = License.objects.get_or_create(**license_data)
            instance.license = license_instance

        instance.save()

        if phonetics_data:
            instance.phonetics.clear()  # Clear existing phonetics for the entry
            for phonetic_data in phonetics_data:
                phonetic_license_data = phonetic_data.pop('license', None)
                if phonetic_license_data:
                    phonetic_license, _ = License.objects.get_or_create(**phonetic_license_data)
                else:
                    phonetic_license = None
                phonetic_instance = Phonetic.objects.create(license=phonetic_license, **phonetic_data)
                instance.phonetics.add(phonetic_instance)  # Add the phonetic to the dictionary_entry

        if meanings_data:
            instance.meanings.clear() 
            for meaning_data in meanings_data:
                definitions_data = meaning_data.pop('definitions', [])
                meaning_instance = Meaning.objects.create(**meaning_data)
                instance.meanings.add(meaning_instance)  # Add meaning to the dictionary_entry
                for definition_data in definitions_data:
                    Definition.objects.create(meaning=meaning_instance, **definition_data)

        return instance
