from rest_framework import routers
# from rest_framework_nested.routers import NestedSimpleRouter
from images.api import ImagesViewSet
from persona.api import PersonaViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'generate_image', ImagesViewSet)
router.register(r'describe', PersonaViewSet)