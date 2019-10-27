from django.db import models
from account.models import Country
from django.contrib import admin


grad_streams_list = [
    'Engineering',
    'Law',
    'Medicine',
    'Business',
]

grad_streams = (
    ('Engineering', 'Engineering'),
    ('Law', 'Law'),
    ('Medicine', 'Medicine'),
    ('Business', 'Business'),
)


class GRE(models.Model):
    verbal  = models.IntegerField(default=None, null=True, blank=True)
    quant   = models.IntegerField(default=None, null=True, blank=True)
    awa     = models.FloatField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.verbal)


class MCAT(models.Model):
    old_total                   = models.IntegerField(default=None, null=True, blank=True)
    new_total                   = models.IntegerField(default=None, null=True, blank=True)
    chemical_physical           = models.IntegerField(default=None, null=True, blank=True)
    critical_analysis           = models.IntegerField(default=None, null=True, blank=True)
    biologic_biochemical        = models.IntegerField(default=None, null=True, blank=True)
    psycho_social_biological    = models.IntegerField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.new_total)


class University(models.Model):
    name                    = models.TextField(default=None)
    info_link               = models.TextField(default=None, null=True)
    rank                    = models.IntegerField(default=None, null=True, blank=True)
    country                 = models.ForeignKey(Country, on_delete=models.CASCADE)
    total_students          = models.IntegerField(default=None, null=True, blank=True)
    total_int_students      = models.IntegerField(default=None, null=True, blank=True)
    address                 = models.TextField(default=None, null=True, blank=True)
    website                 = models.TextField(default=None, null=True, blank=True, max_length=500)
    schools                 = models.TextField(default=None, null=True, blank=True)
    uni_type                = models.TextField(default=None, null=True, blank=True)
    grad_school_link        = models.TextField(default=None, null=True, blank=True, max_length=500)
    undergrad_link          = models.TextField(default=None, null=True, blank=True, max_length=500)
    business_link           = models.TextField(default=None, null=True, blank=True, max_length=500)
    med_link                = models.TextField(default=None, null=True, blank=True, max_length=500)
    law_link                = models.TextField(default=None, null=True, blank=True, max_length=500)
    engg_link               = models.TextField(default=None, null=True, blank=True, max_length=500)
    slug                    = models.SlugField(default=None, null=True, blank=True, max_length=500)
    logo                    = models.TextField(default=None, null=True, blank=True, max_length=500)

    def __str__(self):
        return self.name


class UniversityAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('rank',)


class BusinessGrad(models.Model):
    university              = models.OneToOneField(University, on_delete=models.CASCADE)
    enrollment              = models.IntegerField(default=None, null=True, blank=True)
    international           = models.FloatField(default=None, null=True, blank=True)
    male                    = models.FloatField(default=None, null=True, blank=True)
    female                  = models.FloatField(default=None, null=True, blank=True)
    acceptance_rate_masters = models.FloatField(default=None, null=True, blank=True)  #
    acceptance_rate_phd     = models.FloatField(default=None, null=True, blank=True)  #
    us_application_fee      = models.IntegerField(default=None, null=True, blank=True)  #
    int_application_fee     = models.IntegerField(default=None, null=True, blank=True)  #
    tuition                 = models.FloatField(default=None, null=True, blank=True)
    us_deadline             = models.DateTimeField(default=None, null=True, blank=True)
    int_deadline            = models.DateTimeField(default=None, null=True, blank=True)
    rolling                 = models.BooleanField(default=False)
    gpa                     = models.FloatField(default=None, null=True, blank=True)
    min_toefl_score         = models.IntegerField(default=None, null=True, blank=True)
    mean_toefl_score        = models.IntegerField(default=None, null=True, blank=True)
    min_ielts_score         = models.FloatField(default=None, null=True, blank=True)
    fin_aid_director_name   = models.TextField(default=None, null=True, blank=True)
    fin_aid_director_phone  = models.TextField(default=None, null=True, blank=True)
    fellowships             = models.IntegerField(default=None, null=True, blank=True)
    teaching_assistantships = models.IntegerField(default=None, null=True, blank=True)
    research_assistantships = models.IntegerField(default=None, null=True, blank=True)
    # look for room and board
    living_expenses         = models.IntegerField(default=None, null=True, blank=True)

    # unique to business
    employed                = models.FloatField(default=None, null=True, blank=True)
    employed_3_months       = models.FloatField(default=None, null=True, blank=True)
    avg_work_ex_months      = models.IntegerField(default=None, null=True, blank=True)
    gmat                    = models.IntegerField(default=None, null=True, blank=True)
    gre                     = models.OneToOneField(GRE, on_delete=models.CASCADE)  #
    avg_salary              = models.IntegerField(default=None, null=True, blank=True)

    def __str__(self):
        return self.university.name


class BusinessGradAdmin(admin.ModelAdmin):
    search_fields = ('university__name',)
    ordering = ('university__rank',)


class EngineeringGrad(models.Model):
    university              = models.OneToOneField(University, on_delete=models.CASCADE)  #
    enrollment              = models.IntegerField(default=None, null=True, blank=True)  #
    us_application_fee      = models.IntegerField(default=None, null=True, blank=True)  #
    int_application_fee     = models.IntegerField(default=None, null=True, blank=True)  #
    international           = models.FloatField(default=None, null=True, blank=True)  #
    male                    = models.FloatField(default=None, null=True, blank=True)  #
    female                  = models.FloatField(default=None, null=True, blank=True)  #
    acceptance_rate_masters = models.FloatField(default=None, null=True, blank=True)  #
    acceptance_rate_phd     = models.FloatField(default=None, null=True, blank=True)  #
    tuition                 = models.FloatField(default=None, null=True, blank=True)  #
    us_deadline             = models.DateTimeField(default=None, null=True, blank=True)  #
    int_deadline            = models.DateTimeField(default=None, null=True, blank=True)  #
    rolling                 = models.BooleanField(default=False)  #
    gpa                     = models.FloatField(default=None, null=True, blank=True)  #
    min_toefl_score         = models.IntegerField(default=None, null=True, blank=True)  #
    mean_toefl_score        = models.IntegerField(default=None, null=True, blank=True)  #
    min_ielts_score         = models.FloatField(default=None, null=True, blank=True)  #
    fin_aid_director_name   = models.TextField(default=None, null=True, blank=True)  #
    fin_aid_director_phone  = models.TextField(default=None, null=True, blank=True)  #
    fellowships             = models.IntegerField(default=None, null=True, blank=True)
    teaching_assistantships = models.IntegerField(default=None, null=True, blank=True)  #
    research_assistantships = models.IntegerField(default=None, null=True, blank=True)  #
    # look for room and board
    living_expenses         = models.IntegerField(default=None, null=True, blank=True)  #

    # unique to engineering
    gre                     = models.OneToOneField(GRE, on_delete=models.CASCADE, null=True, blank=True)  #

    def __str__(self):
        return self.university.name


class EngineeringGradAdmin(admin.ModelAdmin):
    search_fields = ('university__name',)
    ordering = ('university__rank',)


class MedicineGrad(models.Model):
    university              = models.OneToOneField(University, on_delete=models.CASCADE)
    enrollment              = models.IntegerField(default=None, null=True, blank=True)
    international           = models.FloatField(default=None, null=True, blank=True)
    us_application_fee      = models.IntegerField(default=None, null=True, blank=True)  #
    int_application_fee     = models.IntegerField(default=None, null=True, blank=True)  #
    acceptance_rate_masters = models.FloatField(default=None, null=True, blank=True)  #
    acceptance_rate_phd     = models.FloatField(default=None, null=True, blank=True)  #
    male                    = models.FloatField(default=None, null=True, blank=True)
    female                  = models.FloatField(default=None, null=True, blank=True)
    tuition                 = models.FloatField(default=None, null=True, blank=True)
    us_deadline             = models.DateTimeField(default=None, null=True, blank=True)
    int_deadline            = models.DateTimeField(default=None, null=True, blank=True)
    rolling                 = models.BooleanField(default=False)
    gpa                     = models.FloatField(default=None, null=True, blank=True)  #
    fin_aid_director_name   = models.TextField(default=None, null=True, blank=True)
    fin_aid_director_phone  = models.TextField(default=None, null=True, blank=True)
    students_receiving_aid  = models.FloatField(default=None, null=True, blank=True)

    # look for room and board
    living_expenses         = models.IntegerField(default=None, null=True, blank=True)

    # unique to medicine
    mcat                    = models.OneToOneField(MCAT, on_delete=models.CASCADE)

    def __str__(self):
        return self.university.name


class MedicineGradAdmin(admin.ModelAdmin):
    search_fields = ('university__name',)
    ordering = ('university__rank',)


class LawGrad(models.Model):
    university              = models.OneToOneField(University, on_delete=models.CASCADE)
    enrollment              = models.IntegerField(default=None, null=True, blank=True)
    international           = models.FloatField(default=None, null=True, blank=True)
    us_application_fee      = models.IntegerField(default=None, null=True, blank=True)  #
    int_application_fee     = models.IntegerField(default=None, null=True, blank=True)  #
    male                    = models.FloatField(default=None, null=True, blank=True)
    female                  = models.FloatField(default=None, null=True, blank=True)
    acceptance_rate         = models.FloatField(default=None, null=True, blank=True)
    tuition                 = models.FloatField(default=None, null=True, blank=True)
    us_deadline             = models.DateTimeField(default=None, null=True, blank=True)
    int_deadline            = models.DateTimeField(default=None, null=True, blank=True)
    rolling                 = models.BooleanField(default=False)
    int_rolling             = models.BooleanField(default=False)
    employed                = models.FloatField(default=None, null=True, blank=True)
    fin_aid_director_name   = models.TextField(default=None, null=True, blank=True)
    fin_aid_director_phone  = models.TextField(default=None, null=True, blank=True)
    students_receiving_aid  = models.FloatField(default=None, null=True, blank=True)
    gpa                     = models.FloatField(default=None, null=True, blank=True)  #

    # look for room and board
    living_expenses         = models.IntegerField(default=None, null=True, blank=True)

    # unique to law
    # look for median lsat
    employed                = models.FloatField(default=None, null=True, blank=True)
    bar_passage_rate        = models.FloatField(default=None, null=True, blank=True)
    median_grant            = models.IntegerField(default=None, null=True, blank=True)
    lsat_score              = models.IntegerField(default=None, null=True, blank=True)
    median_public_salary    = models.IntegerField(default=None, null=True, blank=True)
    median_private_salary   = models.IntegerField(default=None, null=True, blank=True)

    def __str__(self):
        return self.university.name


class LawGradAdmin(admin.ModelAdmin):
    search_fields = ('university__name',)
    ordering = ('university__rank',)

