from django.db import models
import os

# Create your models here.
def video_upload_to(instance, filename):
    filename, ext = os.path.splitext(filename)
    return os.path.join('vid', filename + ext)

class Videos(models.Model):
    video_file = models.FileField(upload_to=video_upload_to)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return os.path.basename(self.video_file.name)

class ParentFolder(models.Model):
    title = models.CharField(max_length=255)
    def __str__(self):
        return self.title

class Subclips(models.Model):
    subclip_file = models.FileField(upload_to='subvid/')
    duration = models.FloatField()
    parent_clip = models.ForeignKey(ParentFolder, on_delete=models.CASCADE, related_name='subclips')

    def __str__(self):
        return self.subclip_file.name

class ConcatVideo(models.Model):
    clip = models.FileField(upload_to='concatvid/')
    date = models.DateTimeField(auto_now_add=True)