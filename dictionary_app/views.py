from django.shortcuts import render
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


class EditWordView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, id):
        try:
            word = Word.objects.get(id=id)
        except Word.DoesNotExist:
            return api_response(
                success=False,
                message="Word not found",
                status_code=status.HTTP_404_NOT_FOUND)
        if word:
            serializer = WordSerializer(word, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return api_response(
                    success=True,
                    message="Word updated successfully",
                    data=serializer.data,
                    status_code=status.HTTP_200_OK
                )
            logger.error(f"Validation error: {serializer.errors}")  # logging the error message in the console
            return api_response(
                success=False,
                message="An error occurred while updating the word. Please check your input.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

# Logic for performing the other operations