from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from .models import Business, Service, Customer, Appointment, Schedule, CustomUser
from .serializers import (
    BusinessSerializer, ServiceSerializer, CustomerSerializer,
    AppointmentSerializer, ScheduleSerializer, StaffSerializer,
    UserRegistrationSerializer, UserLoginSerializer
)
from .permissions import IsBusinessAdminOrSystemAdmin, IsStaffOrBusinessAdminOrSystemAdmin

class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsBusinessAdminOrSystemAdmin]

    def get_queryset(self):
        return Business.objects.filter(id=self.request.user.business.id)

    def create(self, request, *args, **kwargs):
        # Remove any trailing newline characters from the data
        for key in request.data.keys():
            if isinstance(request.data[key], str):
                request.data[key] = request.data[key].strip()
        
        return super().create(request, *args, **kwargs)

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsBusinessAdminOrSystemAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'price', 'duration']

    def get_queryset(self):
        return Service.objects.filter(business=self.request.user.business)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsStaffOrBusinessAdminOrSystemAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['phone']
    search_fields = ['user__first_name', 'user__last_name', 'phone', 'user__email']
    ordering_fields = ['user__last_name', 'user__first_name', 'date_of_birth']

    def get_queryset(self):
        return Customer.objects.filter(user__business=self.request.user.business)

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsStaffOrBusinessAdminOrSystemAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['service', 'staff', 'status']
    search_fields = ['customer__user__first_name', 'customer__user__last_name', 'staff__first_name', 'staff__last_name', 'service__name']
    ordering_fields = ['start_time', 'status', 'service__name']

    def get_queryset(self):
        return Appointment.objects.filter(business=self.request.user.business)

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsStaffOrBusinessAdminOrSystemAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['staff', 'date']
    ordering_fields = ['date', 'start_time']

    def get_queryset(self):
        return Schedule.objects.filter(business=self.request.user.business)

class StaffViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(user_type='STAFF')
    serializer_class = StaffSerializer
    permission_classes = [IsBusinessAdminOrSystemAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['first_name', 'last_name', 'email']

    def get_queryset(self):
        return CustomUser.objects.filter(user_type='STAFF', business=self.request.user.business)

class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserRegistrationSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserRegistrationSerializer(user).data,
                'token': token.key
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)