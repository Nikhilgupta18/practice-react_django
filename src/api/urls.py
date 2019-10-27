from django.urls import path
from .views import AllServicesAPI, ServiceHandlerAPI


urlpatterns = [

    path('service/all_services/', AllServicesAPI.as_view(), name='all_services_api'),
    path('service/<str:link>/', ServiceHandlerAPI.as_view(), name='servicehandler_api'),



]


