from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import VideoUploadView,SubclipsViewSet

router = DefaultRouter()
router.register('subclips', SubclipsViewSet)

urlpatterns = [
    path('upload-video-success/', VideoUploadView.as_view(), name='video-upload'),
    path('upload-video/', views.UploadVideo),
    path('', include(router.urls)),
    path('insert-logo-index/', views.InsertLogoIndex),
    path('insert-logo/', views.InsertingLogo.as_view(), name='insert-logo'),
    path('concatenate-video-index/', views.ConcatenateVideoIndex),
    path('concatenate-video-success/', views.ConcatenateVideo.as_view()),
]

