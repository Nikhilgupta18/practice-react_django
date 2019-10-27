from django.views import View
from django.shortcuts import render
from services.models import Service, ServiceUser, MaterialUser
from account.models import ContactUs
from inv.settings import enable_otp
from account.tasks import send_email
from django.shortcuts import render, redirect
from django.contrib import messages
from university.models import University
from django.db.models import Q
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from account.models import Country
from django.core.paginator import Paginator
from account.models import Decisions, LatestWhatsappGroup
from account.models import Major
from django.contrib.auth import get_user_model
from account.models import Student, GradProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMultiAlternatives, send_mail
from university.models import EngineeringGrad, BusinessGrad
import razorpay
from services.models import PaidMaterial, Payment, Statement, PrincetonAccounts, KaplanAccounts, PrincetonGMATAccounts
import os
import pickle
from django.core.files.images import get_image_dimensions
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from paypal.standard.forms import PayPalPaymentsForm


User = get_user_model()

countries = ['Canada', 'United Kingdom', 'Germany', 'Australia', 'United States']


class Index(View):

    def get(self, request, *args, **kwargs):
        services = Service.objects.all()
        context = dict()
        context['services'] = services
        univ = University.objects.filter(rank__lte=50)[:12]

        import random
        valid_profiles_id_list = list(GradProfile.objects.filter(Q(user__student__complete_profile=True), ~Q(user__student__path='default_user.jpg')).values_list('id', flat=True))
        random_profiles_id_list = random.sample(valid_profiles_id_list, min(len(valid_profiles_id_list), 12))
        grad_profiles = GradProfile.objects.filter(id__in=random_profiles_id_list)

        # countries = list(Country.objects.all().values_list('name', flat=True))
        # countries = list(University.objects.all().values_list('country__name', flat=True).annotate(itemcount=Count('id')).order_by('-itemcount').distinct())#.order_by('country__name'))
        context['univ'] = univ
        context['countries'] = countries
        context['grad_profiles'] = grad_profiles

        return render(request, template_name="react.html", context=context)


class UniversitySearchPage(View):

    def get(self, request, *args, **kwargs):
        # countries = list(Country.objects.all().values_list('name', flat=True))
        context = dict()
        context['countries'] = countries
        country_name = self.kwargs.get('country')
        country_name = country_name.title()
        if country_name not in countries:
            return render(request, 'error.html')

        country = Country.objects.filter(name__iexact=country_name).first()
        universities = University.objects.filter(country=country).order_by('rank')
        paginator = Paginator(universities, 24)
        page_num = request.GET.get('page')
        result = paginator.get_page(page_num)
        try:
            page = paginator.page(page_num)
        except:
            page = paginator.page(1)

        count = paginator.num_pages

        context['universities'] = universities
        context['country'] = country_name
        context['page'] = page
        context['page_count'] = count
        context['result'] = result

        return render(request, template_name="university/university_search.html", context=context)

    def post(self, request, *args, **kwargs):
        # countries = list(Country.objects.all().values_list('name', flat=True))
        context = dict()
        context['countries'] = countries
        country_name = self.kwargs.get('country')
        country_name = country_name.title()
        if country_name not in countries:
            return render(request, 'error.html')

        country = Country.objects.filter(name__iexact=country_name).first()
        universities = University.objects.filter(country=country).order_by('rank')
        paginator = Paginator(universities, 24)
        page_num = request.GET.get('page')
        result = paginator.get_page(page_num)
        try:
            page = paginator.page(page_num)
        except:
            page = paginator.page(1)

        count = paginator.num_pages

        context['universities'] = universities
        context['page'] = page
        context['page_count'] = count
        context['result'] = result
        context['universities'] = universities
        context['country'] = country_name

        return render(request, template_name="university/university_search.html", context=context)


class SearchUni(APIView):

    def post(self, request, *args, **kwargs):
        val = request.POST.get('val')
        if len(val) < 2:
            unis = []
            slugs = []
            limit = 0
        else:
            unis = list(University.objects.filter(Q(name__search=val) | Q(name__istartswith=val) | Q(name__icontains=val), Q(country__name__in=countries)).order_by('id').values_list('name', flat=True))[:10]
            slugs = list(University.objects.filter(Q(name__search=val) | Q(name__istartswith=val) | Q(name__icontains=val), Q(country__name__in=countries)).order_by('id').values_list('slug', flat=True))[:10]
            limit = len(unis)

        return JsonResponse({"unis": unis, 'limit': limit, 'slugs': slugs})

#
# class FetchMoreUnis(APIView):
#     def post(self, request, *args, **kwargs):
#         country_name = request.POST.get('country')
#         start = int(request.POST.get('start'))
#         end = start + 24
#         country = Country.objects.filter(name__iexact=country_name).first()
#         if not Country.objects.filter(name__iexact=country_name).exists():
#             return JsonResponse({'unis': []})
#
#         unis = University.objects.filter(country=country).order_by('rank')[start:end]
#         print(unis)
#         response = serializers.serialize("json", unis)
#         return HttpResponse(response, content_type='application/json')


class PrivacyPolicy(View):

    def get(self, request, *args, **kwargs):

        return render(request, template_name="privacy-policy.html", context={})


class TermsOfUse(View):

    def get(self, request, *args, **kwargs):

        return render(request, template_name="terms-of-use.html", context={})


class TestingPage(View):

    def get(self, request, *args, **kwargs):
        context = dict()
        context['universities'] = list(University.objects.all())#.order_by('id').values_list('name', flat=True))

        return render(request, template_name="testing-page.html", context=context)


class ContactUsView(View):

    def post(self, request, *args, **kwargs):

        name = request.POST.get('name')
        email = request.POST.get('email')
        subject1 = request.POST.get('subject')
        message = request.POST.get('message')

        subject = "Someone is contacting us on YMGrad.com"
        msg = "Sender's Name: " + name + "<br>Sender's Contact: " + email + "<br>Subject: " + subject1 + "<br>Message: " + message

        if request.user.is_authenticated:
            ContactUs.objects.create(user=request.user, name=name, email=email,
                                     subject=subject1, message=message)
        else:
            ContactUs.objects.create(name=name, email=email,
                                     subject=subject1, message=message)
        if enable_otp:
            send_email.delay(receiver=["mittrayash@gmail.com"], email_message=msg, subject=subject)
        else:
            print("Not sending email because in development mode.")
        messages.success(request, "Your message has reached us. We will get back to you soon.")

        return redirect("/")


class SearchUniversity(View):

    def get(self, request, *args, **kwargs):
        val = request.GET.get('q').strip()

        if University.objects.filter(name__iexact=val).exists():
            uni = University.objects.filter(name__iexact=val).first()
            return redirect('/university/' + uni.slug)

        unis = University.objects.filter(Q(name__search=val) | Q(name__istartswith=val) | Q(name__icontains=val), Q(country__name__in=countries)).order_by('id')[:56]
        print(unis)

        context = dict()
        context['result'] = unis
        context['q'] = val
        context['countries'] = countries
        return render(request, 'university/university_search.html', context=context)


def handler404(request, exception=None):
    return render(request, 'error.html', status=404)


def handler500(request):
    return render(request, 'error.html', status=500)


class AdmitsRejects(View):

    def get(self, request, *args, **kwargs):

        # decisions = request.GET.get('university')
        uni_name = request.GET.get('target_university')
        uni = University.objects.filter(name=uni_name).first()

        major = request.GET.get('major')
        major = Major.objects.filter(name=major).first()

        decision_type = request.GET.get('decision_type')
        # decision_type = Decisions.objects.filter(name=decision_type).first()


        if uni and major and decision_type:
            decisions = Decisions.objects.filter(university=uni, major=major, decision_type=decision_type).order_by('-id')
        elif uni and major:
            decisions = Decisions.objects.filter(university=uni, major=major).order_by('-id')
        elif uni and decision_type:
            decisions = Decisions.objects.filter(university=uni, decision_type=decision_type).order_by('-id')
        elif major and decision_type:
            decisions = Decisions.objects.filter(major=major, decision_type=decision_type).order_by('-id')
        elif uni:
            decisions = Decisions.objects.filter(university=uni).order_by('-id')
        elif major:
            decisions = Decisions.objects.filter(major=major).order_by('-id')
        elif decision_type:
            decisions = Decisions.objects.filter(decision_type=decision_type).order_by('-id')
        else:
            decisions = Decisions.objects.all().order_by('-id')

        # decisions = Decisions.objects.all().order_by('-id')

        context = dict()
        context['decisions'] = decisions
        context['universities'] = list(University.objects.all().values_list('name', flat=True).order_by('name'))
        context['majors'] = list(Major.objects.all().values_list('name', flat=True).order_by('name'))

        paginator = Paginator(decisions, 30)
        page_num = request.GET.get('page')
        result = paginator.get_page(page_num)
        try:
            page = paginator.page(page_num)
        except:
            page = paginator.page(1)

        count = paginator.num_pages

        context['page'] = page
        context['page_count'] = count
        context['decisions'] = result
        context['result'] = result
        context['target_university']= uni_name
        context['major'] = major
        context['decision_type'] = decision_type
        return render(request, 'admits_rejects.html', context=context)



    def post(self, request, *args, **kwargs):

        uni_name = request.GET.get('target_university')
        major = request.GET.get('major')
        decision_type = request.GET.get('decision_type')

        uni = University.objects.filter(name=uni_name).first()
        major = Major.objects.filter(name=major).first()

        if uni and major and decision_type:
            decisions = Decisions.objects.filter(university=uni, major=major, decision_type=decision_type).order_by('-id')
        elif uni and major:
            decisions = Decisions.objects.filter(university=uni, major=major).order_by('-id')
        elif uni and decision_type:
            decisions = Decisions.objects.filter(university=uni, decision_type=decision_type).order_by('-id')
        elif major and decision_type:
            decisions = Decisions.objects.filter(major=major, decision_type=decision_type).order_by('-id')
        elif uni:
            decisions = Decisions.objects.filter(university=uni).order_by('-id')
        elif major:
            decisions = Decisions.objects.filter(major=major).order_by('-id')
        elif decision_type:
            decisions = Decisions.objects.filter(decision_type=decision_type).order_by('-id')
        else:
            decisions = Decisions.objects.all().order_by('-id')

        paginator = Paginator(decisions, 30)
        page_num = request.GET.get('page')
        result = paginator.get_page(page_num)
        try:
            page = paginator.page(page_num)
        except:
            page = paginator.page(1)

        count = paginator.num_pages



        context = dict()
        # context['decisions'] = decisions
        context['universities'] = list(University.objects.all().values_list('name', flat=True).order_by('name'))
        context['majors'] = list(Major.objects.all().values_list('name', flat=True).order_by('name'))
        context['page'] = page
        context['page_count'] = count
        context['decisions'] = result
        context['result'] = result

        return render(request, 'admits_rejects.html', context=context)


class GetSubscribers(APIView):
    def post(self, request, *args, **kwargs):
        file = open('subscribers.csv', 'w')

        # users = User.objects.exclude(id__in=ServiceUser.objects.all().values_list('user_id', flat=True))
        users = User.objects.all()
        for user in users:
            has_purchased_sop = 0
            if ServiceUser.objects.filter(user=user, service_name='SOP Drafting').exists():
                has_purchased_sop = 1
            string = user.first_name + "," + user.last_name + "," + user.username + "," + user.email + "," + str(has_purchased_sop) + "\n"
            file.write(string)

        file.close()
        file = open('subscribers.csv', 'rb')
        msgtoUser = EmailMultiAlternatives(subject="Latest Subscribers CSV", body="PFA", from_email='yashmittra@gmail.com', to=['mittrayash@gmail.com'])
        msgtoUser.attach_alternative('SUBSCRIBERS', "text/html")
        msgtoUser.attach("subscribers.csv", file.read(), 'text/csv')
        msgtoUser.send()

        return JsonResponse({"success": True})


class WhatsappGroup(View):
    def get(self, request, *args, **kwargs):
        link = LatestWhatsappGroup.objects.first().link
        return redirect(link)


class AllLinks(View):
    def get(self, request, *args, **kwargs):
        link = LatestWhatsappGroup.objects.first().link

        context = dict()
        context['whatsapp_group_link'] = link

        return render(request, template_name='all_links.html', context=context)


class ViewPremiumMembers(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, 'error.html', context={})

        pending_users = ServiceUser.objects.filter(pending=True).order_by('-timestamp')
        completed_users = ServiceUser.objects.filter(pending=False).order_by('-timestamp')

        context = dict()
        context['pending_users'] = pending_users
        context['completed_users'] = completed_users

        return render(request, template_name='view_premium_members.html', context=context)


class ServiceUserDone(APIView):
    def get(self, request, *args, **kwargs):
        # if not request.user.is_superuser:
        #     return render(request, 'error.html', context={})

        service_user_id = self.kwargs.get('service_user_id')

        service_user = ServiceUser.objects.filter(id=service_user_id).first()
        service_user.pending = False
        service_user.save()

        pending_users = ServiceUser.objects.filter(pending=True).order_by('-timestamp')
        completed_users = ServiceUser.objects.filter(pending=False).order_by('-timestamp')

        context = dict()
        context['pending_users'] = pending_users
        context['completed_users'] = completed_users

        return render(request, template_name='view_premium_members.html', context=context)


class FilterUnis(View):

    def get(self, request, *args, **kwargs):
        from inv.views import countries
        from django.core.paginator import Paginator

        percentage = request.POST.get('percentage')
        gre_quant = request.POST.get('gre_quant')
        gre_verbal = request.POST.get('gre_verbal')
        gmat = request.POST.get('gmat')
        test = request.POST.get('test')
        lang = request.POST.get('lang')
        ielts = request.POST.get('ielts_score')
        toefl = request.POST.get('toefl_score')

        context = dict()

        context['test'] = test
        context['percentage'] = percentage
        context['lang'] = lang
        context['gre_quant'] = gre_quant
        context['gre_verbal'] = gre_verbal
        context['gmat'] = gmat
        context['ielts_score'] = ielts
        context['toefl_score'] = toefl

        return render(request, template_name='filter_unis.html', context=context)

    def post(self, request, *args, **kwargs):
        from django.core.paginator import Paginator

        percentage = float(request.POST.get('percentage'))
        gre_quant = request.POST.get('gre_quant')
        gre_verbal = request.POST.get('gre_verbal')
        gmat = request.POST.get('gmat')
        test = request.POST.get('test')
        lang = request.POST.get('lang')
        ielts = request.POST.get('ielts_score')
        slider1 = int(request.POST.get('slider1'))
        slider2 = int(request.POST.get('slider2'))
        toefl = request.POST.get('toefl_score')

        gpa = min(((percentage**2)/1104) - (0.05924 * percentage) + 2.491, 4)
        print(gpa)

        if gpa > 4:
            gpa = 4
        if percentage < 50:
            messages.error(request, "Your percentage is too low! Unfortunately, we couldn't find any universities for you.")
            return render(request, template_name='filter_unis.html', context=dict())

        context = dict()
        if test == 'gre':
            gre_quant = int(gre_quant)
            gre_verbal = int(gre_verbal)

            if gre_quant > 157:
                quant_upper_limit = gre_quant + 6
            else:
                quant_upper_limit = gre_quant + 10

            if gre_quant > 157:
                quant_lower_limit = gre_quant - 5
            else:
                quant_lower_limit = gre_quant - 10

            if gre_quant > 167:
                quant_lower_limit = quant_lower_limit - 7

            if gre_verbal > 154:
                verbal_upper_limit = gre_verbal + 6
            else:
                verbal_upper_limit = gre_verbal + 10

            if gre_verbal > 154:
                verbal_lower_limit = gre_verbal - 12
            else:
                verbal_lower_limit = gre_verbal - 15

            if gre_verbal > 167:
                verbal_lower_limit = verbal_lower_limit - 7

            universities = EngineeringGrad.objects.filter(gre__quant__lte=quant_upper_limit, gre__quant__gte=quant_lower_limit)  #.exclude(gre__quant__isnull=True)
            universities = universities.filter(gre__verbal__lte=verbal_upper_limit, gre__verbal__gte=verbal_lower_limit)

        elif test == 'gmat':
            gmat = int(gmat)
            if gmat > 700:
                gmat_upper_limit = gmat + 30
            else:
                gmat_upper_limit = gmat + 50

            if gmat > 700:
                gmat_lower_limit = gmat - 120
            else:
                gmat_lower_limit = gmat - 100

            universities = BusinessGrad.objects.filter(gmat__lte=gmat_upper_limit, gmat__gte=gmat_lower_limit)
        if gpa > 3.9:
            gpa = gpa - 0.2

        if gpa > 3.5:
            gpa_upper_limit = gpa + 0.2
        else:
            gpa_upper_limit = gpa + 0.45

        if gpa > 3.5:
            gpa_lower_limit = gpa - 0.3
        else:
            gpa_lower_limit = gpa - 0.4

        universities = universities.filter(gpa__lte=gpa_upper_limit, gpa__gte=gpa_lower_limit)

        if lang == 'toefl':
            toefl = int(toefl)
            if toefl > 110:
                toefl_upper_limit = toefl + 20
                toefl_lower_limit = toefl - 20
            else:
                toefl_upper_limit = toefl + 10
                toefl_lower_limit = toefl - 10
            universities = universities.filter(mean_toefl_score__lte=toefl_upper_limit, mean_toefl_score__gte=toefl_lower_limit)
        else:
            ielts = float(ielts)
            universities = universities.filter(min_ielts_score__lte=ielts)

        from django.db.models import F, Sum, FloatField

        universities = universities.annotate(total_exp=Sum(F('tuition') + F('living_expenses'), output_field=FloatField())).filter(total_exp__lte=slider2, total_exp__gte=slider1)

        universities = universities.order_by('university__rank')

        context['universities'] = universities
        context['result'] = universities
        context['test'] = test
        context['percentage'] = percentage
        context['lang'] = lang
        context['gre_quant'] = gre_quant
        context['gre_verbal'] = gre_verbal
        context['gmat'] = gmat
        context['ielts_score'] = ielts
        context['toefl_score'] = toefl

        return render(request, template_name='filter_unis.html', context=context)


class PaidMaterialView(View):

    def get(self, request):
        user = request.user
        if not user.is_anonymous:
            student = user.student
            student.study_material_page_opens = student.study_material_page_opens + 1
            student.save()

            if student.study_material_page_opens >= student.study_material_email_threshold:
                student.study_material_page_opens = 0
                student.study_material_email_threshold = student.study_material_email_threshold + 2
                student.save()
                msg = "Hi " + user.first_name + ",<br>Notification: <b>The prices for the <a href='https://www.ymgrad.com/study_material/'>study material</a> are bound to increase by tomorrow</b>." \
                       "<br><br>In order to get the material at the current price, please purchase the material today.<br><br>" \
                       "In case you face any issues purchasing the material and would like to use PayPal instead, feel free to reply to this email with the material name and we will arrange that for you." \
                       "<br>Please note that using PayPal will increase the charges by up to $2 depending on the material you wish to purchase.<br><br>We hope to serve you soon.<br><br>Best,<br>YMGrad"

                sub = "Important: Prices about to increase for the study material."
                send_email.delay(receiver=[user.email], email_message=msg, subject=sub)

        material = PaidMaterial.objects.filter(is_available=True).order_by('name')
        context = dict()
        if enable_otp:
            key_id = "rzp_live_6MxRlb7ZCO7XaB"
            client = razorpay.Client(auth=(key_id, "fGjvMdo8cs7o48pXou5sa3Y5"))
        else:
            key_id = "rzp_test_QiGwvmuHqNFHk5"
            client = razorpay.Client(auth=(key_id, "v4gHikpMnv2DVK0OK6CQ9Ttm"))

        context['key_id'] = key_id
        context['materials'] = material

        return render(request, template_name="service/all-material.html", context=context)

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            material_name = request.POST.get('material_name')
            material = PaidMaterial.objects.filter(name=material_name).first()
            material_slug = material.slug
            amount = request.POST.get('amount')
            currency = request.POST.get('currency')
            payment_id = request.POST.get('razorpay_payment_id')

            price_inr = material.price_inr
            price_usd = material.price_usd

            if enable_otp:
                key_id = "rzp_live_6MxRlb7ZCO7XaB"
                client = razorpay.Client(auth=(key_id, "fGjvMdo8cs7o48pXou5sa3Y5"))
            else:
                key_id = "rzp_test_QiGwvmuHqNFHk5"
                client = razorpay.Client(auth=(key_id, "v4gHikpMnv2DVK0OK6CQ9Ttm"))

            payment_obj = client.payment.fetch(payment_id)
            user_email = payment_obj['email']

            paid = False
            if currency == "inr":
                if payment_obj['status'] == 'authorized' and int(amount) >= price_inr:
                    paid = True
                    client.payment.capture(payment_id, amount)
                    payment = Payment.objects.create(user=user, payment_id=payment_id, status='Paid', amount=amount, service_name=material_name, currency="INR")
                    student = user.student
                    student.payments.add(payment)
                    MaterialUser.objects.create(user=user,
                                               material_name=material_name,
                                               payment=payment,
                                               )

                    # send_email.delay(receiver=[user.email, "mittrayash@gmail.com"], email_message=msg, subject=subject)
                    detail = user.first_name + " " + user.last_name + " bought " + material_name + "."
                    Statement.objects.create(type='Credit', detail=detail, amount=price_inr)
            elif currency == "usd":
                if payment_obj['status'] == 'authorized' and int(amount) >= price_usd:
                    paid = True
                    # client.payment.capture(payment_id, amount)  # currency field is required.
                    payment = Payment.objects.create(user=user, payment_id=payment_id, status='Paid', amount=amount, service_name=material_name, currency="USD")
                    student = user.student
                    student.payments.add(payment)
                    MaterialUser.objects.create(user=user,
                                               material_name=material_name,
                                               payment=payment,
                                               )

                    # send_email.delay(receiver=[user.email, "mittrayash@gmail.com"], email_message=msg, subject=subject)
                    detail = user.first_name + " " + user.last_name + " bought " + material_name + "."
                    Statement.objects.create(type='Credit', detail=detail, amount=price_inr)

            if paid:
                material.purchase_times = material.purchase_times + 1
                material.save()

                if material_slug == 'magoosh_gre':
                    email_domain = user_email.split('@')[1]
                    if email_domain == 'gmail.com':
                        messages.success(request,
                                         "Thank You for your payment. Your order has been received and will be processed soon. Please check your email for further instructions.")
                        # share
                        if os.path.exists('token.pickle'):
                            with open('token.pickle', 'rb') as token:
                                creds = pickle.load(token)
                        from googleapiclient.discovery import build
                        service = build('drive', 'v3', credentials=creds)
                        file_id = '1vKTxnTEFRWiEbnmBuU_B2lZhbwcSW_hm'

                        def callback(request_id, response, exception):
                            if exception:
                                # Handle error
                                print(exception)
                            else:
                                print("Permission Id: %s" % response.get('id'))
                        # res = insert_permission(service, "1eXY0GOhZ6pN7C7_id57oxByHPUzKTLT2", user_email, 'user', 'reader')
                        # print(res)
                        batch = service.new_batch_http_request(callback=callback)
                        user_permission = {
                            'type': 'user',
                            'role': 'reader',
                            'emailAddress': user_email
                        }
                        batch.add(service.permissions().create(
                            fileId=file_id,
                            body=user_permission,
                            fields='id',
                            emailMessage="This is a huge package. You may see the folders are empty at first. Please give it an hour to sync on your Google Drive and then download the package."
                        ))

                        batch.execute()

                    else:
                        messages.info(request,
                                         "Thank You for your payment. However, we need a Gmail email ID to process your order. Please check your email.")
                        msg = "Hi " + user.first_name + ",<br>We have received your payment for <b>" + material_name + "</b>." \
                              "<br><br>However, we need a GMAIL email ID to give you access to the material.<br><br>" \
                              "<b>Please reply to this email with your GMAIL email ID and we will process your order " \
                              "within the next 8 hours.</b><br>In case you still fail to receive the material, feel " \
                              "free to contact us by replying to this email again.<br><br>Best,<br>YMGrad"

                        sub = "Additional Information Needed to give access to the material."
                        send_email.delay(receiver=[user_email, "mittrayash@gmail.com"], email_message=msg, subject=sub)

                elif material_slug == 'ets_toefl_tests':
                    email_domain = user_email.split('@')[1]
                    if email_domain == 'gmail.com':
                        messages.success(request, "Thank You for your payment. Your order has been received and will be processed soon. Please check your email for further instructions.")
                        # share
                        if os.path.exists('token.pickle'):
                            with open('token.pickle', 'rb') as token:
                                creds = pickle.load(token)
                        from googleapiclient.discovery import build
                        service = build('drive', 'v3', credentials=creds)
                        file_id = '1eXY0GOhZ6pN7C7_id57oxByHPUzKTLT2'

                        def callback(request_id, response, exception):
                            if exception:
                                # Handle error
                                print(exception)
                            else:
                                print("Permission Id: %s" % response.get('id'))
                        # res = insert_permission(service, "1eXY0GOhZ6pN7C7_id57oxByHPUzKTLT2", user_email, 'user', 'reader')
                        # print(res)
                        batch = service.new_batch_http_request(callback=callback)
                        user_permission = {
                            'type': 'user',
                            'role': 'reader',
                            'emailAddress': user_email
                        }
                        batch.add(service.permissions().create(
                            fileId=file_id,
                            body=user_permission,
                            fields='id',
                            emailMessage="This is a huge package. You may see the folders are empty at first. Please give it an hour to sync on your Google Drive and then download the package."
                        ))

                        batch.execute()

                    else:
                        messages.info(request, "Thank You for your payment. However, we need a Gmail email ID to process your order. Please check your email.")
                        msg = "Hi " + user.first_name + ",<br>We have received your payment for <b>" + material_name + "</b>." \
                              "<br><br>However, we need a GMAIL email ID to give you access to the material.<br><br>" \
                              "<b>Please reply to this email with your GMAIL email ID and we will process your order " \
                              "within the next 8 hours.</b><br>In case you still fail to receive the material, feel " \
                              "free to contact us by replying to this email again.<br><br>Best,<br>YMGrad"

                        sub = "Additional Information Needed to give access to the material."
                        send_email.delay(receiver=[user_email, "mittrayash@gmail.com"], email_message=msg, subject=sub)


                elif material_slug == 'kaplan_practice_sets':
                    email_domain = user_email.split('@')[1]
                    if email_domain == 'gmail.com':
                        messages.success(request, "Thank You for your payment. Your order has been received and will be processed soon. Please check your email for further instructions.")
                        # share
                        if os.path.exists('token.pickle'):
                            with open('token.pickle', 'rb') as token:
                                creds = pickle.load(token)
                        from googleapiclient.discovery import build
                        service = build('drive', 'v3', credentials=creds)
                        file_id = '15EeDQ_bvxUWCdCBoV5FDjblPlH11U_B5'

                        def callback(request_id, response, exception):
                            if exception:
                                # Handle error
                                print(exception)
                            else:
                                print("Permission Id: %s" % response.get('id'))
                        # res = insert_permission(service, "1eXY0GOhZ6pN7C7_id57oxByHPUzKTLT2", user_email, 'user', 'reader')
                        # print(res)
                        batch = service.new_batch_http_request(callback=callback)
                        user_permission = {
                            'type': 'user',
                            'role': 'reader',
                            'emailAddress': user_email
                        }
                        batch.add(service.permissions().create(
                            fileId=file_id,
                            body=user_permission,
                            fields='id',
                            emailMessage="This is a huge package. You may see the folders are empty at first. Please give it an hour to sync on your Google Drive and then download the package."
                        ))

                        batch.execute()

                    else:
                        messages.info(request, "Thank You for your payment. However, we need a Gmail email ID to process your order. Please check your email.")
                        msg = "Hi " + user.first_name + ",<br>We have received your payment for <b>" + material_name + "</b>." \
                              "<br><br>However, we need a GMAIL email ID to give you access to the material.<br><br>" \
                              "<b>Please reply to this email with your GMAIL email ID and we will process your order " \
                              "within the next 8 hours.</b><br>In case you still fail to receive the material, feel " \
                              "free to contact us by replying to this email again.<br><br>Best,<br>YMGrad"

                        sub = "Additional Information Needed to give access to the material."
                        send_email.delay(receiver=[user_email, "mittrayash@gmail.com"], email_message=msg, subject=sub)

                elif material_slug == 'magoosh_ielts':
                    email_domain = user_email.split('@')[1]
                    if email_domain == 'gmail.com':
                        messages.success(request, "Thank You for your payment. Your order has been received and will be processed soon. Please check your email for further instructions.")
                        # share
                        if os.path.exists('token.pickle'):
                            with open('token.pickle', 'rb') as token:
                                creds = pickle.load(token)
                        from googleapiclient.discovery import build
                        service = build('drive', 'v3', credentials=creds)
                        file_id = '1QjwfL1EVMIM-p21IvtvWBYdoHUSCmBKc'

                        def callback(request_id, response, exception):
                            if exception:
                                # Handle error
                                print(exception)
                            else:
                                print("Permission Id: %s" % response.get('id'))
                        # res = insert_permission(service, "1eXY0GOhZ6pN7C7_id57oxByHPUzKTLT2", user_email, 'user', 'reader')
                        # print(res)
                        batch = service.new_batch_http_request(callback=callback)
                        user_permission = {
                            'type': 'user',
                            'role': 'reader',
                            'emailAddress': user_email
                        }
                        batch.add(service.permissions().create(
                            fileId=file_id,
                            body=user_permission,
                            fields='id',
                            emailMessage="This is a huge package. You may see the folders are empty at first. Please give it an hour to sync on your Google Drive and then download the package."
                        ))

                        batch.execute()

                    else:
                        messages.info(request, "Thank You for your payment. However, we need a Gmail email ID to process your order. Please check your email.")
                        msg = "Hi " + user.first_name + ",<br>We have received your payment for <b>" + material_name + "</b>." \
                              "<br><br>However, we need a GMAIL email ID to give you access to the material.<br><br>" \
                              "<b>Please reply to this email with your GMAIL email ID and we will process your order " \
                              "within the next 8 hours.</b><br>In case you still fail to receive the material, feel " \
                              "free to contact us by replying to this email again.<br><br>Best,<br>YMGrad"

                        sub = "Additional Information Needed to give access to the material."
                        send_email.delay(receiver=[user_email, "mittrayash@gmail.com"], email_message=msg, subject=sub)


                elif material_slug == 'kaplan_gre':
                    account = KaplanAccounts.objects.filter(sold=False).first()
                    sub = "Your Kaplan GRE Online Tests Account"
                    msg = "Hi " + user.first_name + ",<br>We have received your payment for <b>" + material_name + "</b>." \
                           "<br><br>Here are your account details. Please login <a href='https://www.kaptest.com/login'>here</a>.<br><br>" \
                           "<b>Email: </b> " + account.email_id + "<br>" \
                           "<b>Password: </b>" + account.password + "<br><br>" \
                           "Please note that the password is case-sensitive. In case you need help," \
                           " feel free to reply to this email.<br><br>Best,<br>YMGrad"

                    send_email.delay(receiver=[user_email], email_message=msg, subject=sub)

                    account.sold = True
                    account.sold_to = user
                    account.save()
                    messages.success(request,
                                     "Thank You for your payment. Your order has been received and will be processed soon. Please check your email for further instructions.")

                    accounts_left = KaplanAccounts.objects.filter(sold=False).count()
                    if accounts_left <= 3:
                        msg = "Only " + str(accounts_left) + " Kaplan accounts left!!! Reload now!"
                        sub = "Kaplan Accounts sold out ALERT"
                        send_email.delay(receiver=["mittrayash@gmail.com"], email_message=msg, subject=sub)

                    if accounts_left == 0:
                        kaplan = PaidMaterial.objects.filter(slug='kaplan_gre').first()
                        kaplan.is_available = False
                        kaplan.save()

                elif material_slug == 'princeton_gre_tests':
                    account = PrincetonAccounts.objects.filter(sold=False).first()
                    sub = "Your Princeton GRE Online Tests Account"
                    msg = "Hi " + user.first_name + ",<br>We have received your payment for <b>" + material_name + "</b>." \
                           "<br><br>Here are your account details. Please login <a href='https://secure.princetonreview.com/account/signin/?go=http%3a%2f%2fsecure.princetonreview.com%2f'>here</a>.<br><br>" \
                           "<b>Email: </b> " + account.email_id + "<br>" \
                           "<b>Password: </b>" + account.password + "<br><br>" \
                           "Please note that the password is case-sensitive. In case you need help," \
                           " feel free to reply to this email.<br><br>Best,<br>YMGrad"

                    send_email.delay(receiver=[user_email], email_message=msg, subject=sub)

                    account.sold = True
                    account.sold_to = user.username
                    account.save()
                    messages.success(request,
                                     "Thank You for your payment. Your order has been received and will be processed soon. Please check your email for further instructions.")

                    accounts_left = PrincetonAccounts.objects.filter(sold=False).count()
                    if accounts_left <= 3:
                        msg = "Only " + str(accounts_left) + " princeton accounts left!!! Reload now!"
                        sub = "Princeton GRE Accounts sold out ALERT"
                        send_email.delay(receiver=["mittrayash@gmail.com"], email_message=msg, subject=sub)

                    if accounts_left == 0:
                        princeton = PaidMaterial.objects.filter(slug='princeton_gre_tests').first()
                        princeton.is_available = False
                        princeton.save()


                elif material_slug == 'princeton_gmat':
                    account = PrincetonGMATAccounts.objects.filter(sold=False).first()
                    sub = "Your Princeton GRE Online Tests Account"
                    msg = "Hi " + user.first_name + ",<br>We have received your payment for <b>" + material_name + "</b>." \
                           "<br><br>Here are your account details. Please login <a href='https://secure.princetonreview.com/account/signin/?go=http%3a%2f%2fsecure.princetonreview.com%2f'>here</a>.<br><br>" \
                           "<b>Email: </b> " + account.email_id + "<br>" \
                           "<b>Password: </b>" + account.password + "<br><br>" \
                           "Please note that the password is case-sensitive. In case you need help," \
                           " feel free to reply to this email.<br><br>Best,<br>YMGrad"

                    send_email.delay(receiver=[user_email], email_message=msg, subject=sub)

                    account.sold = True
                    account.sold_to = user
                    account.save()
                    messages.success(request,
                                     "Thank You for your payment. Your order has been received and will be processed soon. Please check your email for further instructions.")

                    accounts_left = PrincetonGMATAccounts.objects.filter(sold=False).count()
                    if accounts_left <= 3:
                        msg = "Only " + str(accounts_left) + " princeton GMAT accounts left!!! Reload now!"
                        sub = "Princeton GMAT Accounts sold out ALERT"
                        send_email.delay(receiver=["mittrayash@gmail.com"], email_message=msg, subject=sub)

                    if accounts_left == 0:
                        princeton = PaidMaterial.objects.filter(slug='princeton_gre_tests').first()
                        princeton.is_available = False
                        princeton.save()

                elif material_slug == 'grammarly_business':
                    sub = "Your Grammarly Business Account"
                    msg = "Hi " + user.first_name + ",<br>We have received your payment for <b>" + material_name + "</b>." \
                           "<br><br>Here are your account details.<br><br>" \
                           "<b>Email: </b>crystal.g.lewis@gmail.com<br>" \
                           "<b>Password: </b>12131981c<br><br>" \
                           "Please note that the password is case-sensitive. Please do not change the password at any point of time. In case you need help," \
                           " feel free to reply to this email.<br><br>Best,<br>YMGrad"

                    send_email.delay(receiver=[user_email], email_message=msg, subject=sub)
                    messages.success(request,
                                     "Thank You for your payment. Your order has been received and will be processed soon. Please check your email for further instructions.")

                elif material_slug == 'usnews':
                    sub = "Your USNews Premium Account"
                    msg = "Hi " + user.first_name + ",<br>We have received your payment for <b>" + material_name + "</b>." \
                           "<br><br>Here are your account details.<br><br>" \
                           "<b>Email: </b>mittrayash@gmail.com<br>" \
                           "<b>Password: </b>Apropos12<br><br>" \
                           "Please note that the password is case-sensitive. Please do not change the password at any point of time. In case you need help," \
                           " feel free to reply to this email.<br><br>Best,<br>YMGrad"

                    send_email.delay(receiver=[user_email], email_message=msg, subject=sub)
                    messages.success(request,
                                     "Thank You for your payment. Your order has been received and will be processed soon. Please check your email for further instructions.")

                elif material_slug == 'manhattan_toefl':
                    sub = "Your Manhattan TOEFL Online Access + Ebook"
                    msg = "Hi " + user.first_name + ",<br>We have received your payment for <b>" + material_name + "</b>." \
                           "<br><br>First step: Download the ebook <a href='https://drive.google.com/open?id=15AFBhsKdlCRpEWnTTsSdkYH1CRo3kDxl'>here</a>.<br><br>" \
                           "<br>Second Step: Download epubfilereader for windows to open the ebook." \
                           "<br><br>With the ebook, use the portal with the details below:" \
                           "<br><br>Here are your account details which can be used to log in <a href='https://www.manhattanprep.com/college/studentcenter/'>here</a>.<br><br>" \
                           "<b>Email: </b>Yashmittra4@gmail.com<br>" \
                           "<b>Password: </b>Toefl422019<br><br>" \
                           "Please note that the password is case-sensitive. Please do not change the password at any point of time. In case you need help," \
                           " feel free to reply to this email.<br><br>Best,<br>YMGrad"

                    send_email.delay(receiver=[user_email], email_message=msg, subject=sub)
                    messages.success(request,
                                     "Thank You for your payment. Your order has been received and will be processed soon. Please check your email for further instructions.")

        except Exception as e:
            print(e)
            messages.error(request, "Unfortunately, we are unable to process your request at this time. In case any funds have been deducted from your account, please contact us and we will resolve the issue for you.")
        return redirect("/account/dashboard/")


class Compress(APIView):
    def post(self, request):
        from PIL import Image
        import os, sys

        path = "/home/kali/Desktop/Study Abroad/StudyAbroad/static_my_proj/base/"
        dirs = os.listdir(path)

        def resize():
            for item in dirs:
                if os.path.isfile(path + item):
                    im = Image.open(path + item)
                    width, height = im.size

                    if im.mode != 'RGB':
                        im = im.convert('RGB')
                    f, e = os.path.splitext(path + item)
                    new_width = width
                    im.thumbnail((new_width, new_width * height / width), Image.ANTIALIAS)
                    # imResize = im.resize((200, 200), Image.ANTIALIAS)
                    im.save(f + '.jpg', 'JPEG', quality=100)

        resize()

        return JsonResponse({'success': True})


class Fix(APIView):
    def post(self, request):
        all = Student.objects.all()

        for obj in all:
            path = str(obj.path)
            f = path.split('.')[0]
            e = path.split('.')[1]

            if e == 'jpeg' or e == 'png' or e == 'JPG':
                e = 'jpg'
                new_path = f + '.' + e
                obj.path = new_path
                obj.save()

        return JsonResponse({'success': True})



def payment_process(request):
    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '100',
        'item_name': 'Item_Name_xyz',
        'invoice': 'Test Payment Invoice',
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host, reverse('payment_done')),
        'cancel_return': 'http://{}{}'.format(host, reverse('payment_canceled')),
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'pets/payment_process.html', {'form': form})
