import requests
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Word
from .serializers import WordSerializer
from Dictionary.utils.custom_response import api_response
import logging

logger = logging.getLogger(__name__) # creating a logger object


# Creating a word
class CreateWordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = WordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_response(
                success=True,
                message="Word created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
            
        logger.error(f"Validation error: {serializer.errors}") # logging the error message in the console
        return api_response(
            success=False,
            message="An error occurred while creating the word. Please check your input.",
            status_code=status.HTTP_400_BAD_REQUEST
        )
  
 # Getting all the words   
class WordListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        words = Word.objects.all()
        serializer = WordSerializer(words, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) # returning the response


# Logic for performing the other operations

class DeleteWordView(APIView):
    def delete(self, request, id):
            word = get_object_or_404(Word, id=id)
            word.delete()
            return Response(
                 {"message": "Word has been deleted successfully."}, 
                 status=status.HTTP_204_NO_CONTENT
            )

#Words cannot be found
class WordSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q')  # Get the search query from the URL parameters
        if not query:
            return api_response(
                success=False,
                message="No search query provided.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            word = Word.objects.get(word=query)
            serializer = WordSerializer(word)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Word.DoesNotExist:
            logger.warning(f"Word '{query}' not found in the database.")   # Log the warning

            # Call external API for the word meaning
            api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{query}"  # Replace with your actual API URL
            try:
                response = requests.get(api_url)
                response.raise_for_status()  # Raise an error for bad responses

                 # Process the response from the external API
                api_data = response.json()
                if isinstance(api_data, list) and len(api_data) > 0 and 'meanings' in api_data[0]:  # Check structure
                    return Response(api_data[0]['meanings'], status=status.HTTP_200_OK)
                else:
                    return api_response(
                        success=False,
                        message="We couldn't find any definitions for the word you entered. Please try again later or search online for more information.",
                        status_code=status.HTTP_404_NOT_FOUND
                    )
            except requests.RequestException as e:
                logger.error(f"Error fetching from external API: {e}")
                return api_response(
                    success=False,
                    message="We couldn't find any definitions for the word you entered. Please try again later or search online for more information.",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )