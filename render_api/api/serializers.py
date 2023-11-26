from rest_framework import serializers
from .models import Videos, Subclips

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videos
        fields = ['video_file']

class VideoUploadSerializer(serializers.Serializer):
    video = serializers.FileField()

class LogoVideoSerializer(serializers.Serializer):
    video = serializers.FileField()
    logo = serializers.ImageField()


class SubclipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subclips
        fields = '__all__'