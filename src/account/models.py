from django.db import models
from django.contrib import admin
from django.contrib.auth import get_user_model
from account.storage import OverwriteStorage
from services.models import Payment
from django.utils.timezone import now
# from university.models import University


User = get_user_model()

how_did_you_hear_about_us_list = [
    'YouTube',
    'Instagram',
    'Google',
    'Facebook',
    'Referral',
    'Campus Ambassador',
    'Other',
]

how_did_you_hear_about_us_tuple = (
    ('YouTube', 'YouTube'),
    ('Instagram', 'Instagram'),
    ('Google', 'Google'),
    ('Facebook', 'Facebook'),
    ('Referral', 'Referral'),
    ('Campus Ambassador', 'Campus Ambassador'),
    ('Other', 'Other'),
)

area_of_study_tuple = (
    ('Engineering', 'Engineering'),
    ('Business', 'Business'),
    ('Law', 'Law'),
    ('Medicine', 'Medicine'),
)

article_status = (
    ('in_review', 'in_review'),
    ('published', 'published')
)


class Country(models.Model):
    """ Model for a db of reviews' data """

    sortname            = models.CharField(max_length=5)
    name                = models.TextField()
    phone_code          = models.IntegerField()
    # flag_filename       = models.TextField(default=1)
    # timestamp           = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.name)


class CountryAdmin(admin.ModelAdmin):
    search_fields = ('name', 'sortname', 'phone_code', )


class State(models.Model):

    name          = models.TextField()
    country       = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


class Student(models.Model):
    """ Model for a db of Client' data """

    def profile_picture_name(instance, filename):
        new_path = str(instance.user_id) + '.' + str(filename.split('.')[-1])
        instance.path = new_path
        # new_path = "lawyers_profile_pics/" + new_path
        return new_path

    user                        = models.OneToOneField(User, on_delete=models.CASCADE)
    country                     = models.ForeignKey(Country, on_delete=models.CASCADE)
    state                       = models.ForeignKey(State, on_delete=models.CASCADE)
    path                        = models.ImageField(upload_to="profile_pics/", default='default_user.jpg')
    mobile                      = models.BigIntegerField()
    how_did_you_hear_about_us   = models.TextField(choices=how_did_you_hear_about_us_tuple, default=1)
    promo_msg_sent              = models.BooleanField(default=False)
    payments                    = models.ManyToManyField(Payment, related_name="payments", null=True, blank=True)
    graduate                    = models.BooleanField(default=True)
    dob                         = models.DateTimeField(null=True, blank=True, default=None)
    complete_profile            = models.BooleanField(default=False)
    about                       = models.TextField(default=None, blank=True, null=True)
    website                     = models.SlugField(default=None, blank=True, null=True, max_length=200)
    plan_valid_till             = models.DateTimeField(default=now())
    no_of_questions_asked       = models.IntegerField(default=0)
    publisher                   = models.BooleanField(default=False)
    study_material_page_opens   = models.IntegerField(default=0)
    study_material_email_threshold = models.IntegerField(default = 3)
    no_of_referrals             = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class StudentAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'user__email', 'mobile', )


class UndergradUniversity(models.Model):
    name                    = models.TextField(default=None)
    country                 = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class UndergradUniversityAdmin(admin.ModelAdmin):
    search_fields = ('name', 'country__name',)


class Major(models.Model):
    name                    = models.TextField(default=None)

    def __str__(self):
        return self.name


class MajorAdmin(admin.ModelAdmin):
    search_fields = ('name', )


class GREScore(models.Model):
    verbal  = models.IntegerField(default=None, null=True, blank=True)
    quant   = models.IntegerField(default=None, null=True, blank=True)
    awa     = models.FloatField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.verbal) + "V, " + str(self.quant) + "Q, " + str(self.awa) + " AWA"


class MCATScore(models.Model):
    total                       = models.IntegerField(default=None, null=True, blank=True)
    chemical_physical           = models.IntegerField(default=None, null=True, blank=True)
    critical_analysis           = models.IntegerField(default=None, null=True, blank=True)
    biologic_biochemical        = models.IntegerField(default=None, null=True, blank=True)
    psycho_social_biological    = models.IntegerField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.total)


class TOEFLScore(models.Model):
    total           = models.IntegerField(default=None, null=True, blank=True)
    speaking        = models.IntegerField(default=None, null=True, blank=True)
    listening       = models.IntegerField(default=None, null=True, blank=True)
    writing         = models.IntegerField(default=None, null=True, blank=True)
    reading         = models.IntegerField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.reading) + "R, " + str(self.listening) + "L, " + str(self.speaking) + "S, " + str(self.writing) + "W"


class IELTSScore(models.Model):
    speaking        = models.FloatField(default=None, null=True, blank=True)
    listening       = models.FloatField(default=None, null=True, blank=True)
    writing         = models.FloatField(default=None, null=True, blank=True)
    reading         = models.FloatField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.reading) + "R, " + str(self.listening) + "L, " + str(self.speaking) + "S, " + str(self.writing) + "W"


class Internship(models.Model):
    company_name        = models.TextField(default=None, null=True, blank=True)
    duration_months     = models.TextField(default=None, null=True, blank=True)
    position            = models.TextField(default=None, null=True, blank=True)
    details             = models.TextField(default=None, null=True, blank=True)

    def __str__(self):
        return self.company_name


class Work(models.Model):
    company_name        = models.TextField(default=None, null=True, blank=True)
    duration_months     = models.TextField(default=None, null=True, blank=True)
    position            = models.TextField(default=None, null=True, blank=True)
    details             = models.TextField(default=None, null=True, blank=True)

    def __str__(self):
        return self.company_name


class Project(models.Model):
    name                = models.TextField(default=None, null=True, blank=True)
    website             = models.TextField(default=None, null=True, blank=True)
    details             = models.TextField(default=None, null=True, blank=True)

    def __str__(self):
        return self.name


class GradProfile(models.Model):

    def resume_name(instance, filename):
        new_path = str(instance.user_id) + '.' + str(filename.split('.')[-1])
        instance.path = new_path
        return new_path

    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    backlogs        = models.IntegerField(default=0, null=True, blank=True)
    area_of_study   = models.TextField(default=None, null=True, blank=True, choices=area_of_study_tuple)
    undergrad_uni   = models.ForeignKey(UndergradUniversity, on_delete=models.CASCADE)
    has_taken_gre   = models.BooleanField(default=False, null=True, blank=True)  # only used for business grads
    gre             = models.ForeignKey(GREScore, on_delete=models.CASCADE, null=True, blank=True)
    mcat            = models.ForeignKey(MCATScore, on_delete=models.CASCADE, null=True, blank=True)
    gmat            = models.IntegerField(default=None, null=True, blank=True)
    lsat            = models.IntegerField(default=None, null=True, blank=True)
    has_taken_toefl = models.BooleanField(default=False, null=True, blank=True)
    toefl           = models.ForeignKey(TOEFLScore, on_delete=models.CASCADE, null=True, blank=True)
    ielts           = models.ForeignKey(IELTSScore, on_delete=models.CASCADE, null=True, blank=True)
    cgpa            = models.FloatField(default=None, null=True, blank=True)
    cgpa_out_of     = models.IntegerField(default=None, null=True, blank=True)  # out of may be 4, 5, 10 or 100
    major           = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='major')  # like I.T., CSE, Mechanical, etc.
    target_major    = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='target_major')  # like I.T., CSE, Mechanical, etc.
    work_ex_months  = models.IntegerField(default=None, null=True, blank=True)
    research_papers = models.IntegerField(default=None, null=True, blank=True)
    resume          = models.FileField(upload_to='resume/', default=None, null=True, blank=True)

    # interested term
    int_term = models.TextField(default=None, blank=True, null=True)
    int_year = models.IntegerField(default=2020, blank=True, null=True)
    target_university = models.ForeignKey('university.University', on_delete=models.CASCADE, null=True, blank=True)

#### DO NOT TAKE THIS AT REGISTRATION ####
    projects        = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    achievements    = models.TextField(default=None, null=True, blank=True)
    internships     = models.ManyToManyField(Internship, related_name="grad_internships", null=True, blank=True, default=None)
    work_exp        = models.ManyToManyField(Work, related_name="work", null=True, blank=True, default=None)

    def __str__(self):
        return self.user.username


class GradProfileAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'user__email', 'user__student__mobile',)


class SATScore(models.Model):

    total           = models.IntegerField(default=None, null=True, blank=True)
    math            = models.IntegerField(default=None, null=True, blank=True)
    reading_writing = models.IntegerField(default=None, null=True, blank=True)

    def __str__(self):
        return self.total


class UndergradProfile(models.Model):

    def resume_name(instance, filename):
        new_path = str(instance.user_id) + '.' + str(filename.split('.')[-1])
        instance.path = new_path
        return new_path

    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    area_of_study   = models.TextField(default=None, null=True, blank=True, choices=area_of_study_tuple)
    sat             = models.ForeignKey(SATScore, on_delete=models.CASCADE)
    lsat            = models.IntegerField(default=None, null=True, blank=True)
    toefl           = models.ForeignKey(TOEFLScore, on_delete=models.CASCADE)
    ielts           = models.ForeignKey(IELTSScore, on_delete=models.CASCADE)
    cgpa            = models.FloatField(default=None, null=True, blank=True)
    cgpa_out_of     = models.IntegerField(default=None, null=True, blank=True)  # out of may be 4, 5, 10 or 100
    school_name     = models.TextField(default=None, null=True, blank=True)
    projects        = models.ForeignKey(Project, on_delete=models.CASCADE)
    achievements    = models.TextField(default=None, null=True, blank=True)
    internships     = models.ManyToManyField(Internship, related_name="ug_internships")
    resume          = models.FileField(upload_to='resume/', storage=OverwriteStorage(), default=None, null=True, blank=True)

    def __str__(self):
        return self.user.username


class OtpDB(models.Model):

    user                    = models.OneToOneField(User, on_delete=models.CASCADE)
    otp                     = models.CharField(max_length=10)
    mobile_otp              = models.TextField(max_length=5, default=1)
    verified                = models.BooleanField(default=False)
    confirm_mobile          = models.BooleanField(default=False)
    timestamp               = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # mobile_otp_send_time    = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name


class ContactUs(models.Model):

    user                = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    name                = models.TextField(default='', null=True, blank=True)
    email               = models.TextField(default=None, null=True, blank=True)
    subject             = models.TextField(default=None, null=True, blank=True)
    message             = models.TextField(default=None, null=True, blank=True)
    timestamp           = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.user) + " " + str(self.timestamp)


class Decisions(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    university      = models.ForeignKey('university.University', default=None, null=True, blank=True, on_delete=models.CASCADE)
    major           = models.ForeignKey(Major, on_delete=models.CASCADE)  # like I.T., CSE, Mechanical, etc.
    decision_type   = models.TextField(default=None, blank=True, null=True)  # applied, admit, reject
    final           = models.BooleanField(default=False, null=True, blank=True)
    application_date = models.DateTimeField(default=now())
    decision_date   = models.DateTimeField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.user)


class LatestWhatsappGroup(models.Model):
    link = models.TextField(null=True, blank=True, default=None)

    def __str__(self):
        return str(self.link)


class Referral(models.Model):

    user            = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='user')  # new user who signed up
    referred_by     = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='referrer')  # old user who referred new user
    confirm         = models.BooleanField(default=False)
    timestamp       = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.user) + " referred by " + str(self.referred_by)

