from django.shortcuts import render
from django.shortcuts import render, redirect

from services.models import Service
from rest_framework.views import APIView
from django.http import JsonResponse


# Create your views here.


class AllServicesAPI(APIView):
    def get(self, request, *args, **kwargs):
        services = list(Service.objects.values())
        return JsonResponse({'services': services})


class ServiceHandlerAPI(APIView):
    def post(self, request, *args, **kwargs):
        # link = kwargs.get('link')
        # user = request.GET.get('user')
        service = list(Service.objects.values())
        return JsonResponse({'service': service})



# class CurrentUserView(APIView):
#     def get(self, request):
#         serializer = UserSerializer(request.user)
#         return JsonResponse(serializer.data)
