from django.contrib import admin

from rangefilter.filters import DateTimeRangeFilter

from api.models import Employee, Location


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("email",)
    fields = ("email", "get_badge", "get_location_count")
    readonly_fields = ("email", "get_badge", "get_location_count")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_badge(self, obj):
        return obj.get_badge_display()

    def get_location_count(self, obj):
        return obj.employee_locations.count()


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "employee")
    search_fields = ("employee",)
    list_filter = (("created_at", DateTimeRangeFilter),)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
