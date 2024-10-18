from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import (
    BusinessViewSet, ServiceViewSet, CustomerViewSet,
    AppointmentViewSet, ScheduleViewSet, StaffViewSet,
    UserRegistrationView, UserLoginView
)

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'staff', StaffViewSet)

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^businesses/?$', BusinessViewSet.as_view({'get': 'list', 'post': 'create'}), name='business-list'),
    re_path(r'^businesses/(?P<pk>[^/.]+)/?$', BusinessViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='business-detail'),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
]