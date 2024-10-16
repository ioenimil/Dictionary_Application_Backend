from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DictionaryEntry
from .serializers import DictionaryEntrySerializer
import requests
import logging
from Dictionary.utils.custom_response import APIResponseHandler
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


# Creating a word
class CreateWordView(APIView):
    external_api_url = "https://api.dictionaryapi.dev/api/v2/entries/en"  
    
    permission_classes = [IsAuthenticated]
    

    def check_external_api(self, word):
        response = requests.get(f"{self.external_api_url}/{word}")
        if response.status_code == 200:
            return True
        return False 

    def post(self, request):
        word = request.data.get('word')
        
        if self.check_external_api(word):
            return Response({"error": "Word already exists in the external dictionary."},
                            status=status.HTTP_400_BAD_REQUEST)

        if DictionaryEntry.objects.filter(word=word).exists():
            return Response({"error": "Word already exists in the database."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = DictionaryEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
 # Getting all the words   
class WordListView(APIView):
    def get(self, request):
        dictionary_entries = DictionaryEntry.objects.prefetch_related('meanings__definitions', 'phonetics').all()
        if not dictionary_entries.exists():
            return Response({"message": "No words found."}, status=status.HTTP_200_OK)
        serializer = DictionaryEntrySerializer(dictionary_entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Logic for performing the other operations
class DeleteWordView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        dictionary_entry = get_object_or_404(DictionaryEntry, id=id)
        dictionary_entry.delete()

        return Response(
            {"message": "Word has been deleted successfully."}, 
            status=status.HTTP_204_NO_CONTENT
        )


# Communicating with the External Dictionary API
class WordSearchView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        query = request.query_params.get('q')
        if not query:
            return APIResponseHandler.api_response(
                success=False,
                message="No search query provided.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        query = query.lower()
        logger.info(f"Searching for word: {query}")

        # Check if word is in the local database
        dictionary_entry = DictionaryEntry.objects.filter(word=query).first()
        if dictionary_entry:
            serializer = DictionaryEntrySerializer(dictionary_entry)
            return Response([serializer.data], status=status.HTTP_200_OK)

        api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{query}"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            api_data = response.json()

            if not api_data or not isinstance(api_data, list):
                return APIResponseHandler.api_response(
                    success=False,
                    message="Word not found in the external API. Sorry pal, we couldn't find definitions for the word you were looking for. You can try the search again later or head to the web instead.",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            entry = api_data[0] if api_data else None
            if not entry:
                return APIResponseHandler.api_response(
                    success=False,
                    message="No Definitions Found.",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            phonetics = [
                {
                    'text': phonetic.get('text', ''),
                    'audio': phonetic.get('audio', ''),
                    'sourceUrl': phonetic.get('sourceUrl', None),
                    'license': {
                        'name': phonetic.get('license', {}).get('name', 'BY-SA 4.0'),
                        'url': phonetic.get('license', {}).get('url', 'https://creativecommons.org/licenses/by-sa/4.0')
                    } if phonetic.get('license') else {
                        'name': 'BY-SA 4.0',
                        'url': 'https://creativecommons.org/licenses/by-sa/4.0'
                    }
                }
                for phonetic in entry.get('phonetics', [])
            ] or [{'text': '', 'audio': '', 'sourceUrl': None}]

            # Populate meanings and definitions
            meanings = []
            for meaning in entry.get('meanings', []):
                definitions = [
                    {
                        'definition': definition.get('definition', ''),
                        'synonyms': definition.get('synonyms', []),
                        'antonyms': definition.get('antonyms', []),
                        'example': definition.get('example', None)
                    }
                    for definition in meaning.get('definitions', [])
                ] or [{'definition': '', 'synonyms': [], 'antonyms': [], 'example': None}]

                meanings.append({
                    'partOfSpeech': meaning.get('partOfSpeech', ''),
                    'definitions': definitions,
                    'synonyms': meaning.get('synonyms', []),
                    'antonyms': meaning.get('antonyms', [])
                })

            api_response_data = {
                'word': query,
                'phonetics': phonetics,
                'meanings': meanings or [{'partOfSpeech': '', 'definitions': [{'definition': '', 'synonyms': [], 'antonyms': [], 'example': None}]}],
                'license': entry.get('license', {'name': 'CC BY-SA 3.0', 'url': 'https://creativecommons.org/licenses/by-sa/3.0'}),
                'sourceUrls': entry.get('sourceUrls', [f'https://en.wiktionary.org/wiki/{query}'])
            }

            if not meanings:
                dictionary_entry = DictionaryEntry.objects.filter(word=query).first()
                if dictionary_entry:
                    serializer = WordSerializer(dictionary_entry)
                    return Response([serializer.data], status=status.HTTP_200_OK)

            return Response([api_response_data], status=status.HTTP_200_OK)

        except requests.exceptions.HTTPError as e:
            logger.error(f"External API request failed: {e}")
            return APIResponseHandler.api_response(
                success=False,
                message="Sorry pal, we couldn't find definitions for the word you were looking for. You can try the search again later or head to the web instead.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except requests.RequestException as e:
            logger.error(f"External API request failed: {e}")
            return APIResponseHandler.api_response(
                success=False,
                message="Error occurred while fetching definitions.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Updating a word
class EditWordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        dictionary_entry = get_object_or_404(DictionaryEntry, id=id)
        serializer = DictionaryEntrySerializer(dictionary_entry, data=request.data, partial=True)
        if serializer.is_valid():

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)