from rest_framework.serializers import ModelSerializer

from api.models import Employee, Location


class EmployeeSerializer(ModelSerializer):
    class Meta:
        model = Employee
        fields = ("id", "email", "badge")


class LocationSerializer(ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Location
        fields = ("id", "employee", "name", "latitude", "longitude", "link")
