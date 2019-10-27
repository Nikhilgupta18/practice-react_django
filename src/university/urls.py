from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from .views import PopulateUniData, UniversityView, Test, GetUniNames, GetTargetUniversity


urlpatterns = [

    # path('populate_uni_data/', PopulateUniData.as_view(), name='populate'),
    path('get_uni_names/', GetUniNames.as_view(), name='get_uni_names'),
    path('get_target_uni/', GetTargetUniversity.as_view(), name='get_target_uni'),
    path('<str:uni_name>/', UniversityView.as_view(), name='university-view'),  # Make sure this is in the end, otherwise other views will be confused for this one


]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                    path('test/', Test.as_view(), name='testtttt'),

                  ] + urlpatterns
