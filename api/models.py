import uuid
from django.db import models

from api.choices import BadgeChoices


class BaseModel(models.Model):
    """
    A base model which will be inherited by all the other models present in this module
    """

    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        db_index=True,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Employee(BaseModel):
    """
    An employee model to store employee details with their location
    and some metadata.
    """

    email = models.EmailField(unique=True)
    badge = models.CharField(max_length=3, choices=BadgeChoices.get_values())


class Location(BaseModel):
    """
    This model will store one or many location of an employee
    """

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="employee_locations"
    )
    name = models.CharField(max_length=100)

    # Location coordinates can be null if we did'nt get the correct location name
    # Or we won't able to fetch location coordinates with respect to GeoNames
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    # This will store google map link, Only if the location coordinates are present
    # For e.g: https://www.google.com/maps/lat,lng
    link = models.URLField(null=True)

    # This field is for storing raw response from  geo name API
    # If we get any error in response while fetching location then,
    # We can check the raw response to debug
    geo_name_api_response = models.JSONField(default=dict)

    class Meta:
        ordering = ("-created_at",)
