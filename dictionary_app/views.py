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
        query = request.query_params.get('q')  # Get the search query from the URL parameters
        if not query:
            return APIResponseHandler.api_response(
                success=False,
                message="No search query provided.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"Searching for word: {query}")

        word = Word.objects.filter(word=query).first()
        if word:
            serializer = WordSerializer(word)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # If the word is not found in the database, call the external API
        api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{query}"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            api_data = response.json()
            logger.info(f"External API response: {api_data}")

            # Check if we received valid data
            if isinstance(api_data, list) and len(api_data) > 0:
                meanings = api_data[0].get('meanings', [])
                phonetics = api_data[0].get('phonetics', [])

                # Collect phonetic information and audio URLs
                phonetic_data = []
                for phonetic in phonetics:
                    phonetic_info = {
                        'text': phonetic.get('text'),
                        'audio': phonetic.get('audio'),
                    }
                    phonetic_data.append(phonetic_info)

                # Prepare the response data
                response_data = {
                    'word': query, 
                    'phonetics': phonetic_data,
                    'meanings': meanings,
                }

                return Response(response_data, status=status.HTTP_200_OK)

            else:
                return APIResponseHandler.api_response(
                    success=False,
                    message="We couldn't find any definitions for the word you entered.",
                    status_code=status.HTTP_404_NOT_FOUND
                )

        except requests.RequestException as e:
            logger.error(f"Error fetching from external API: {e}")
            return APIResponseHandler.api_response(
                success=False,
                message="We couldn't find any definitions for the word you entered.",
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