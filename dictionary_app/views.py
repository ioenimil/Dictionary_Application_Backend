import requests
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Word
from .serializers import WordSerializer
from drf_yasg.utils import swagger_auto_schema
from Dictionary.utils.custom_response import APIResponseHandler
import logging

logger = logging.getLogger(__name__) # creating a logger object


# Creating a word
class CreateWordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logger.info(f"Authenticated user: {request.user}")
        serializer = WordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return APIResponseHandler.api_response(
                success=True,
                message="Word created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
            
        logger.error(f"Validation error: {serializer.errors}") # logging the error message in the console
        return APIResponseHandler.api_response(
            success=False,
            message="An error occurred while creating the word. Please check your input.",
            status_code=status.HTTP_400_BAD_REQUEST
        )
  
 # Getting all the words   
class WordListView(APIView):


    def get(self, request):
        words = Word.objects.all()
        serializer = WordSerializer(words, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) # returning the response


# Logic for performing the other operations

class DeleteWordView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id):
            word = get_object_or_404(Word, id=id)
            word.delete()
            return Response(
                 {"message": "Word has been deleted successfully."}, 
                 status=status.HTTP_204_NO_CONTENT
            )

#Words cannot be found
class WordSearchView(APIView):
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
        word = Word.objects.filter(word=query).first()
        if word:
            serializer = WordSerializer(word)
            return Response([serializer.data], status=status.HTTP_200_OK)
        # External API request if word is not found in the local database
        api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{query}"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            api_data = response.json()
            if not api_data or not isinstance(api_data, list):
                return APIResponseHandler.api_response(
                    success=False,
                    message="Word not found in the external API. Sorry pal, we couldn't find definitions for the word you were looking for. You can try the search again at later time or head to the web instead.",
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
            return Response([api_response_data], status=status.HTTP_200_OK)
        except requests.exceptions.HTTPError as e:
            logger.error(f"External API request failed: {e}")
            return APIResponseHandler.api_response(
                success=False,
                message="Sorry pal, we couldn't find definitions for the word you were looking for. You can try the search again at later time or head to the web instead.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except requests.RequestException as e:
            logger.error(f"External API request failed: {e}")
            return APIResponseHandler.api_response(
                success=False,
                message="Error occurred while fetching definitions.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class EditWordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=WordSerializer)

    def put(self, request, id):
        try:
            word = Word.objects.get(id=id)
        except Word.DoesNotExist:
            return APIResponseHandler.api_response(
                success=False,
                message="Word not found",
                status_code=status.HTTP_404_NOT_FOUND)
        if word:
            serializer = WordSerializer(word, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return APIResponseHandler.api_response(
                    success=True,
                    message="Word updated successfully",
                    data=serializer.data,
                    status_code=status.HTTP_200_OK
                )
            logger.error(f"Validation error: {serializer.errors}")  # logging the error message in the console
            return APIResponseHandler.api_response(
                success=False,
                message="An error occurred while updating the word. Please check your input.",
                status_code=status.HTTP_400_BAD_REQUEST
            )