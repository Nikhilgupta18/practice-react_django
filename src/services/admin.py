from django.contrib import admin
from .models import SopPrice, Service, LORPrice, FreeConsultation, UnivShortlising, GreConsultation, ToeflConsultation,\
    HistoryDraft, CompleteApplication, CreateAdmissionPlan, Resume, Payment, ServiceUser, Statement, PaidMaterial, \
    PrincetonAccounts, KaplanAccounts, PrincetonGMATAccounts

# Register your models here.
admin.site.register(Service)
admin.site.register(SopPrice)
admin.site.register(LORPrice)
admin.site.register(FreeConsultation)
admin.site.register(UnivShortlising)
admin.site.register(GreConsultation)
admin.site.register(HistoryDraft)
admin.site.register(CompleteApplication)
admin.site.register(CreateAdmissionPlan)
admin.site.register(Resume)
admin.site.register(Payment)
admin.site.register(ToeflConsultation)
admin.site.register(ServiceUser)
admin.site.register(Statement)
admin.site.register(PaidMaterial)
admin.site.register(PrincetonAccounts)
admin.site.register(KaplanAccounts)
admin.site.register(PrincetonGMATAccounts)

