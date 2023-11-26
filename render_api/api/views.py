from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from .models import Videos, Subclips
from .serializers import VideoUploadSerializer, SubclipSerializer, LogoVideoSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from .editmodel import AutoCutting, InsertLogo, resolution_changer
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


class ResolutionChanger(APIView):
    def post(self, request, format= None):
        serializer= VideoUploadSerializer(data= request.data)
        if request.method == "POST":
            if serializer.is_valid():
                video = serializer.validated_data['video']
                resolution_changer(video)
                
                return Response({'Message':'Done!'}, status=status.HTTP_200_OK)
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
