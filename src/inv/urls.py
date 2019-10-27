from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from .views import Index, PrivacyPolicy, TermsOfUse, TestingPage, ContactUsView, SearchUni, UniversitySearchPage
from .views import SearchUniversity, handler404, handler500, AdmitsRejects, GetSubscribers, WhatsappGroup, AllLinks
from account.views import ProfilePage
from .views import ViewPremiumMembers, ServiceUserDone, FilterUnis, PaidMaterialView, Compress, Fix
from django.views.generic.base import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('posts/', TemplateView.as_view(template_name='react.html')),
    path('', Index.as_view()),
    path('account/', include('account.urls')),
    path('university/', include('university.urls')),
    path('service/', include('services.urls')),
    path('forums/', include('forums.urls')),
    path('article/', include('article.urls')),
    path('api/', include('api.urls')),
    path('all_links/', AllLinks.as_view(), name='all_links'),
    path('unipredict/', FilterUnis.as_view(), name='filter_unis'),
    path('study_material/', PaidMaterialView.as_view(), name='paid_material_view'),

    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('privacy-policy/', PrivacyPolicy.as_view(), name='privacy-policy'),
    path('get_subscribers/', GetSubscribers.as_view(), name='get_subscribers'),
    path('whatsapp_group/', WhatsappGroup.as_view(), name='whatsapp_group'),
    path('view_premium_members/', ViewPremiumMembers.as_view(), name='view_premium_members'),
    path('terms-of-use/', TermsOfUse.as_view(), name='terms-of-use'),
    path('admits_rejects/', AdmitsRejects.as_view(), name='admits_rejects'),
    path('contact-us-index/', ContactUsView.as_view(), name='contact-form-index'),
    path('search-uni/', SearchUni.as_view(), name='search-uni'),
    path('search-university/', SearchUniversity.as_view(), name='search-university'),
    path('service_user_done/<str:service_user_id>/', ServiceUserDone.as_view(), name='service_user_done'),
    path('search/<str:country>/', UniversitySearchPage.as_view(), name='uni_search_page'),
    path('profile/<str:username>/', ProfilePage.as_view(), name='profile_page'),

]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    urlpatterns = [
                      path('testing-page/', TestingPage.as_view(), name='testing-page'),
                      re_path(r'^__debug__/', include(debug_toolbar.urls)),
                      path('compress/', Compress.as_view(), name='compress'),
                      path('fix/', Fix.as_view(), name='fix'),

                  ] + urlpatterns


handler404 = handler404
handler500 = handler500
