from django_filters import rest_framework as filters

from api.models import Location


class LocationFilter(filters.FilterSet):
    datetime = filters.DateRangeFilter()

    class Meta:
        model = Location
        fields = ("datetime",)
