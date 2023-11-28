from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from .models import Videos, Subclips
from .serializers import VideoUploadSerializer, SubclipSerializer, LogoVideoSerializer, ConcatSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from .editmodel import AutoCutting, InsertLogo, VideoConcatenator
import os
from django.conf import settings
# Create your views here.

class VideoUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, format=None):
        serializer = VideoUploadSerializer(data=request.data)

        if request.method == 'POST':
            clipduration = float(request.POST.get('clipduration'))

            if serializer.is_valid():

                video = serializer.validated_data['video']
                Videos.objects.create(video_file=video)
                AutoCutting(file_clip=video, dur_input=clipduration)

            return Response({'message': 'Video has been splitted successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InsertingLogo(APIView):
    def post(self, request, format=None):
        serializer = LogoVideoSerializer(data=request.data)

        if request.method == "POST":
            if serializer.is_valid():
                video = serializer.validated_data['video']
                logo = serializer.validated_data['logo']

                InsertLogo(video, logo)

                return Response({"Message": 'Done!'}, status=status.HTTP_200_OK)

        return Response({"Message": "Error!"}, status=status.HTTP_400_BAD_REQUEST)


class ConcatenateVideo(APIView):
    def post(self, request, format= None):
        serializer= ConcatSerializer(data= request.data)
        # if request.method == "POST":
        #     if serializer.is_valid():
        #         videos = request.FILES.getlist('videos')
                
        #         if not videos or len(videos) < 2:
        #             return Response({'message': 'Please upload at least two videos.'}, status=status.HTTP_400_BAD_REQUEST)

        #         try:
        #             concatenated_video = VideoConcatenator(videos)
        #             return Response({'message': 'Videos concatenated successfully.'}, status=status.HTTP_200_OK)

        #         except Exception as e:
        #             return Response({'message': f'Error concatenating videos: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # return Response({"Message": "Error!"}, status=status.HTTP_400_BAD_REQUEST)

        print(serializer)
        return Response({"Message": "Error!"}, status=status.HTTP_400_BAD_REQUEST)

class SubclipViewSet(viewsets.ModelViewSet):
    queryset = Subclips.objects.all()
    serializer_class = SubclipSerializer

    def list(self, request, folder_name):
        # Get the subclips for the specified folder_name
        folder_path = os.path.join('media', 'subvid', folder_name)
        subclips = Subclips.objects.filter(parent_clip__title=folder_name)
        
        if not subclips.exists():
            return Response({'message': 'No subclips found for the specified folder name.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SubclipSerializer(subclips, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SubclipsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subclips.objects.all()
    serializer_class = SubclipSerializer


def UploadVideo(request):
    return render(request, 'index.html')

def InsertLogoIndex(request):
    return render(request, 'insert-logo.html')

def ConcatenateVideoIndex(request):
    return render(request, 'concatenate-video-index.html')