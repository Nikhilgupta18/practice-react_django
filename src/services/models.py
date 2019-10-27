from django.db import models
from django.contrib.auth import get_user_model


consult_list = (
    ('Google Hangouts', 'Google Hangouts'),
    ('Call', 'Call'),
    )

transaction_tuple = (
    ('Credit', 'Credit'),
    ('Debit', 'Debit'),

)

transaction_list = [
    'Credit',
    'Debit',
]


User = get_user_model()
# Create your models here.


class Service(models.Model):

    heading                 = models.TextField(default=None, null=True, blank=True)
    intro                   = models.TextField(default=None, null=True, blank=True)
    details                 = models.TextField(default=None, null=True, blank=True)
    spl_details             = models.TextField(default=None, null=True, blank=True)
    link                    = models.SlugField(default=None, null=True, blank=True)
    faicon                  = models.TextField(default=None, null=True, blank=True)
    yt_link                 = models.TextField(default=None, null=True, blank=True)
    is_available            = models.BooleanField(default=True, null=True, blank=True)

    def __str__(self):
        return self.heading


class Testimonial(models.Model):

    service     = models.ForeignKey(Service, on_delete=models.CASCADE)
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    path        = models.ImageField(upload_to="testimonials/", default=None, null=True, blank=True)
    rating      = models.IntegerField(default=None, null=True, blank=True)
    headline    = models.CharField(max_length=100, default=None, null=True, blank=True)
    details     = models.TextField(default=None, null=True, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    anonymous   = models.BooleanField(default=False)

    def __str__(self):
        return self.headline


class SopPrice(models.Model):

    customizations              = models.IntegerField(default=None, null=True, blank=True)
    price_usd                   = models.IntegerField(default=None, null=True, blank=True)
    price_inr                   = models.IntegerField(default=None, null=True, blank=True)
    link_inr                    = models.SlugField(default=None, null=True, blank=True)
    link_usd                    = models.SlugField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.customizations)


class LORPrice(models.Model):

    customizations          = models.IntegerField(default=None, null=True, blank=True)
    price_usd               = models.IntegerField(default=None, null=True, blank=True)
    price_inr               = models.IntegerField(default=None, null=True, blank=True)
    link_inr                = models.SlugField(default=None, null=True, blank=True)
    link_usd                = models.SlugField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.customizations)


class UnivShortlising(models.Model):

    service                     = models.TextField(default=None, null=True, blank=True)
    price_inr                   = models.IntegerField(default=None, null=True, blank=True)
    price_usd                   = models.IntegerField(default=None, null=True, blank=True)
    link_inr                    = models.SlugField(default=None, null=True, blank=True)
    link_usd                    = models.SlugField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.service)


class GreConsultation(models.Model):

    service                     = models.TextField(default=None, null=True, blank=True)
    price_inr                   = models.IntegerField(default=None, null=True, blank=True)
    price_usd                   = models.IntegerField(default=None, null=True, blank=True)
    link_inr                    = models.SlugField(default=None, null=True, blank=True)
    link_usd                    = models.SlugField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.service)


class ToeflConsultation(models.Model):

    service                     = models.TextField(default=None, null=True, blank=True)
    price_inr                   = models.IntegerField(default=None, null=True, blank=True)
    price_usd                   = models.IntegerField(default=None, null=True, blank=True)
    link_inr                    = models.SlugField(default=None, null=True, blank=True)
    link_usd                    = models.SlugField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.service)


class HistoryDraft(models.Model):

    service                     = models.TextField(default=None, null=True, blank=True)
    price_inr                   = models.IntegerField(default=None, null=True, blank=True)
    price_usd                   = models.IntegerField(default=None, null=True, blank=True)
    link_inr                    = models.SlugField(default=None, null=True, blank=True)
    link_usd                    = models.SlugField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.service)


class CompleteApplication(models.Model):

    service                     = models.TextField(default=None, null=True, blank=True)
    price_inr                   = models.IntegerField(default=None, null=True, blank=True)
    price_usd                   = models.IntegerField(default=None, null=True, blank=True)
    link_inr                    = models.SlugField(default=None, null=True, blank=True)
    link_usd                    = models.SlugField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.service)


class CreateAdmissionPlan(models.Model):

    service                     = models.TextField(default=None, null=True, blank=True)
    price_inr                   = models.IntegerField(default=None, null=True, blank=True)
    price_usd                   = models.IntegerField(default=None, null=True, blank=True)
    link_inr                    = models.SlugField(default=None, null=True, blank=True)
    link_usd                    = models.SlugField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.service)


class Resume(models.Model):

    service                     = models.TextField(default=None, null=True, blank=True)
    price_inr                   = models.IntegerField(default=None, null=True, blank=True)
    price_usd                   = models.IntegerField(default=None, null=True, blank=True)
    link_inr                    = models.SlugField(default=None, null=True, blank=True)
    link_usd                    = models.SlugField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.service)


class FreeConsultation(models.Model):

    user               = models.ForeignKey(User, on_delete=models.CASCADE)
    number             = models.BigIntegerField(default=None, null=True, blank=True)
    service            = models.TextField(default=None, null=True, blank=True)
    date               = models.DateField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.user)


class Payment(models.Model):

    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id          = models.TextField(default=None, null=True, blank=True)
    service_name        = models.TextField(Service, null=True, blank=True)
    status              = models.TextField(default=None, null=True, blank=True)
    currency            = models.TextField(default="INR")
    amount              = models.FloatField(default=0.0)
    timestamp           = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id + " -> " + str(self.status) + " " + str(self.amount)


class ServiceUser(models.Model):

    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    service_name        = models.TextField(default=None, null=True, blank=True)
    customizations      = models.TextField(default=None, null=True, blank=True)
    payment             = models.ForeignKey(Payment, on_delete=models.CASCADE)
    timestamp           = models.DateTimeField(auto_now_add=True, null=True)
    pending             = models.BooleanField(default=True, null=True, blank=True)
    payment_pending     = models.TextField(default=None, null=True, blank=True)
    total_amount        = models.TextField(default=None, null=True, blank=True)

    def __str__(self):
        if self.pending:
            suffix = "Pending"
        else:
            suffix = "Delivered"
        return str(self.user) + " -- " + str(self.service_name) + " -- " + str(suffix)


class MaterialUser(models.Model):

    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    material_name       = models.TextField(default=None, null=True, blank=True)
    payment             = models.ForeignKey(Payment, on_delete=models.CASCADE)
    timestamp           = models.DateTimeField(auto_now_add=True, null=True)
    pending             = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return str(self.user) + "  PURCHASED  " + str(self.material_name)


class Statement(models.Model):

    type                = models.TextField(choices=transaction_tuple, default=1)
    detail              = models.TextField()
    amount              = models.FloatField()
    timestamp           = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.detail


class PaidMaterial(models.Model):

    name                        = models.TextField(default=None, null=True, blank=True)
    details                     = models.TextField(default=None, null=True, blank=True)
    price_inr                   = models.IntegerField(default=None, null=True, blank=True)
    price_usd                   = models.IntegerField(default=None, null=True, blank=True)
    purchase_times              = models.IntegerField(default=None, null=True, blank=True)
    limited                     = models.BooleanField(default=False)
    is_available                = models.BooleanField(default=True, null=True, blank=True)
    thumbnail                   = models.ImageField(upload_to="paid_material/", default=None, null=True, blank=True)
    price_about_to_increase     = models.BooleanField(default=False)
    slug                        = models.SlugField(default=None, null=True, blank=False)

    def __str__(self):
        return self.name


class PrincetonAccounts(models.Model):

    email_id            = models.TextField(default=None, null=True, blank=True)
    password            = models.TextField(default=None, null=True, blank=True)
    sold                = models.BooleanField(default=False)
    timestamp           = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    sold_to             = models.TextField(default=None, null=True, blank=True)

    def __str__(self):
        if self.sold:
            suffix = "Sold"
        else:
            suffix = "Available"
        return self.email_id + "   " + str(suffix)


class KaplanAccounts(models.Model):

    email_id            = models.TextField(default=None, null=True, blank=True)
    password            = models.TextField(default=None, null=True, blank=True)
    sold                = models.BooleanField(default=False)
    timestamp           = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    sold_to             = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.sold:
            suffix = "Sold"
        else:
            suffix = "Available"
        return self.email_id + "   " + str(suffix)


class PrincetonGMATAccounts(models.Model):

    email_id            = models.TextField(default=None, null=True, blank=True)
    password            = models.TextField(default=None, null=True, blank=True)
    sold                = models.BooleanField(default=False)
    timestamp           = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    sold_to             = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.sold:
            suffix = "Sold"
        else:
            suffix = "Available"
        return self.email_id + "   " + str(suffix)
