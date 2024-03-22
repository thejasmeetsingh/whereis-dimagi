from rest_framework import generics

from api.filters import LocationFilter
from api.models import Employee, Location
from api.serializers import EmployeeSerializer, LocationSerializer


class EmployeeList(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class LocationList(generics.ListAPIView):
    queryset = Location.objects.select_related("employee")
    serializer_class = LocationSerializer
    search_fields = ("employee__email",)
    filter_class = LocationFilter
