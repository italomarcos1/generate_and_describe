from django.urls import path
from .views import describe_persona
from .views import generate_image

urlpatterns = [
    path('describe_persona/', describe_persona),
    path('generate_image/', generate_image),
]