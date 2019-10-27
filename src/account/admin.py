from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Student, Country, CountryAdmin, StudentAdmin, UndergradUniversity, UndergradUniversityAdmin
from .models import GradProfile, Major, IELTSScore, TOEFLScore, MCATScore, Decisions, LatestWhatsappGroup, GradProfileAdmin, GREScore, Referral


User = get_user_model()
admin.site.register(Student, StudentAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(UndergradUniversity, UndergradUniversityAdmin)
admin.site.register(GradProfile, GradProfileAdmin)
admin.site.register(Major)
admin.site.register(IELTSScore)
admin.site.register(TOEFLScore)
admin.site.register(MCATScore)
admin.site.register(Decisions)
admin.site.register(LatestWhatsappGroup)
admin.site.register(GREScore)
admin.site.register(Referral)





