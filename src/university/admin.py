from django.contrib import admin
from .models import GRE, University, BusinessGrad, EngineeringGrad, MedicineGrad, LawGrad
from .models import UniversityAdmin, BusinessGradAdmin, EngineeringGradAdmin, MedicineGradAdmin, LawGradAdmin


admin.site.register(GRE)
admin.site.register(University, UniversityAdmin)
admin.site.register(BusinessGrad, BusinessGradAdmin)
admin.site.register(EngineeringGrad, LawGradAdmin)
admin.site.register(MedicineGrad, MedicineGradAdmin)
admin.site.register(LawGrad)
