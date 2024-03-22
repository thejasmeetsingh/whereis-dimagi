from django.urls import path

from api.views import EmployeeList, LocationList

urlpatterns = [
    path('employee/', EmployeeList.as_view()),
    path('location/', LocationList.as_view())
]
