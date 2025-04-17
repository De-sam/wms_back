from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LocationViewSet, SectionViewSet, SeatViewSet

router = DefaultRouter()
router.register(r'locations', LocationViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'seats', SeatViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
