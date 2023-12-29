from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import SubclipsViewSet

router = DefaultRouter()
router.register('subclips', SubclipsViewSet)

urlpatterns = [
    path('cutting-video-success/', views.CuttingVideo.as_view(), name='video-upload'),
    path('cutting-video-index/', views.UploadVideo),
    path('', include(router.urls)),
    path('insert-logo-index/', views.InsertLogoIndex),
    path('insert-logo/', views.InsertingLogo.as_view(), name='insert-logo'),
    path('concatenate-video-index/', views.ConcatenateVideoIndex),
    path('concatenate-video-success/', views.ConcatenateVideo.as_view(), name= 'concatenate-video'),
    path('bluring-video-index/', views.BluringVideoIndex),
    path('bluring-video-success/', views.BluringVideoAPI.as_view(), name='bluring-video'),
    path('speed-changer-index/', views.SpeedChangerIndex),
    path('speed-changer-success/', views.SpeedChangerAPI.as_view()),
]

