from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from .views import ServiceHandler, SopAmount, LorAmount, FreeConsult, UniversityShortlisting, GreConsult, ToeflConsult, \
    HisDraft, AllServices,ResumeHelp ,CompleteApp, CreateAdmission, Purchase, PublishTestimonial

from django.views.generic import TemplateView


urlpatterns = [
    path('premium/<str:service_name>', ServiceHandler.as_view(), name="services"),
    path('publish-testimonial/<str:service_name>/', PublishTestimonial.as_view(), name="publish_testimonial"),
    path('amount-sop/', SopAmount.as_view(), name="sop-price"),
    path('amount-lor/', LorAmount.as_view(), name="lor-price"),
    path('univ-shortlist/', UniversityShortlisting.as_view(), name="univ-shortlisting"),
    path('gre-consult/', GreConsult.as_view(), name="gre-consultation"),
    path('toefl-consult/', ToeflConsult.as_view(), name="toefl-consultation"),
    path('history-draft/', HisDraft.as_view(), name="history-draft"),
    path('complete-application/', CompleteApp.as_view(), name="complete-application"),
    path('create-admission-plan/', CreateAdmission.as_view(), name="create-admission-plan"),
    path('help-resume/', ResumeHelp.as_view(), name="help-resume"),
    path('free-consultation/', FreeConsult.as_view(), name="free-consultation"),
    path('purchase/', Purchase.as_view(), name="purchase"),
    path('', TemplateView.as_view(template_name='react.html'), name="all-services"),


]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [

                    ] + urlpatterns
