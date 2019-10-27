from django.shortcuts import render, redirect
from django.views import View
from services.models import Service, SopPrice
from rest_framework.views import APIView
from django.http import JsonResponse
from account.models import Country
from .models import University, BusinessGrad, LawGrad, MedicineGrad, EngineeringGrad, GRE, MCAT
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date
from dateutil.relativedelta import relativedelta
import os
from datetime import datetime
from selenium import webdriver
from django.utils.timezone import now
from selenium.webdriver.chrome.options import Options
import pickle
from account.models import UndergradUniversity, Major
from django.db.models import Q
import razorpay
from django.contrib import messages
from inv.settings import enable_otp
from services.models import ServiceUser, Payment, Statement
from account.tasks import send_email


options = Options()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')  # Last I checked this was necessary.

globa = None


class PopulateUniData(APIView):
    def post(self, request, *args, **kwargs):

        driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", chrome_options=options)
        driver.get("https://www.google.com")

        ## LOGIN

        # driver.find_element_by_id('username').send_keys('mittrayash@gmail.com')
        # driver.find_element_by_id('password').send_keys('globaedu96')
        # driver.find_element_by_class_name('medium-8').click()

        # pickle.dump(driver.get_cookies(), open("USNewsCookies.pkl", "wb"))
        for cookie in pickle.load(open("USNewsCookies.pkl", "rb")):
            driver.add_cookie(cookie)

        unis = University.objects.all().order_by('id')
        for uni in unis:
            if uni.law_link:
                link = uni.law_link
                driver.get(link)

                temp = driver.find_elements_by_class_name("ekbTOm")

                try:
                    tuition = int(temp[4].text.replace(",", "").replace("$", ""))
                except Exception as e:
                    print(e)
                    tuition = None

                btn = driver.find_elements_by_css_selector('button.cAELFP')
                for i in [0, 1, 2, 3, 4, 5]:
                    element = btn[i]
                    driver.execute_script("arguments[0].click();", element)
                temp2 = driver.find_elements_by_class_name('DataField__DataWrapper-s193d1m9-2')
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Financial aid director")]')
                    fin_aid_director_name = ttt.find_element_by_xpath('..').text.splitlines()[1]
                except Exception as e:
                    print(e)
                    fin_aid_director_name = None
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Financial aid phone")]')
                    fin_aid_director_phone = ttt.find_element_by_xpath('..').text.splitlines()[1]
                except Exception as e:
                    print(e)
                    fin_aid_director_phone = None
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Full-time program application fee")]')
                    us_application_fee = int(ttt.find_element_by_xpath('..').text.splitlines()[1].replace("$", ""))
                except Exception as e:
                    print(e)
                    us_application_fee = None

                try:
                    # ttt = driver.find_element_by_xpath('//div[contains(span, "Application deadline (U.S. residents)")]')
                    ttt = temp[5].text
                    us_deadline = datetime.strptime(ttt.strip() + " 2019", "%b. %d %Y")
                    int_deadline = us_deadline
                    rolling = False
                except Exception as e:
                    print(e)
                    try:
                        us_deadline = datetime.strptime(ttt.strip() + " 2019", "%B %d %Y")
                        int_deadline = us_deadline
                    except Exception as ee:
                        print(ee)
                        us_deadline = None
                        int_deadline = None
                    if "rolling" in ttt:
                        rolling = True
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Full-time program application fee")]')
                    int_application_fee = int(ttt.find_element_by_xpath('..').text.splitlines()[1].replace("$", ""))
                except Exception as e:
                    print(e)
                    int_application_fee = None
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Acceptance rate")]')
                    acceptance_rate = float(ttt.find_element_by_xpath('..').text.splitlines()[1].replace("%", ""))
                except Exception as e:
                    print(e)
                    acceptance_rate = None
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(p, "International")]')
                    international = float(ttt.find_element_by_xpath('..').text.splitlines()[1].replace("%", ""))
                    print(international)
                except Exception as e:
                    print(e)
                    international = None
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Employed at graduation")]')
                    employed = float(ttt.find_element_by_xpath('..').text.splitlines()[1].replace("%", ""))
                except Exception as e:
                    print(e)
                    employed = None
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Bar passage rate (first-time test takers)")]')
                    bar_passage_rate = float(ttt.find_element_by_xpath('..').text.splitlines()[1].replace("%", ""))
                except Exception as e:
                    print(e)
                    bar_passage_rate = None
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Median undergraduate GPA for all program entrants")]')
                    gpa = float(ttt.find_element_by_xpath('..').text.splitlines()[1])
                except Exception as e:
                    print(e)
                    gpa = None

                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Median LSAT score for all program entrants")]')
                    lsat_score = int(ttt.find_element_by_xpath('..').text.splitlines()[1].strip())
                except Exception as e:
                    print(e)
                    lsat_score = None

                # try:
                #     ttt = driver.find_element_by_xpath('//div[contains(span, "Average GRE score")]')
                #     quant = int(ttt.find_element_by_xpath('..').text.splitlines()[2].strip().split(' quantitative')[0])
                # except Exception as e:
                #     print(e)
                #     quant = None
                # try:
                #     ttt = driver.find_element_by_xpath('//div[contains(span, "Average GRE score")]')
                #     awa = float(ttt.find_element_by_xpath('..').text.splitlines()[2].strip().split(' writing')[0])
                # except Exception as e:
                #     print(e)
                #     awa = None
                # try:
                #     ttt = driver.find_element_by_xpath('//div[contains(span, "Minimum TOEFL score required")]')
                #     min_toefl_score = int(ttt.find_element_by_xpath('..').text.splitlines()[1].strip().split(' Internet-based test')[0])
                # except Exception as e:
                #     print(e)
                #     min_toefl_score = None
                # try:
                #     ttt = driver.find_element_by_xpath('//div[contains(span, "Mean TOEFL of entering students")]')
                #     mean_toefl_score = int(ttt.find_element_by_xpath('..').text.splitlines()[1].strip().split(' Internet-based test')[0])
                # except Exception as e:
                #     print(e)
                #     mean_toefl_score = None
                # try:
                #     ttt = driver.find_element_by_xpath('//div[contains(span, "Minimum IELTS score required")]')
                #     min_ielts_score = float(ttt.find_element_by_xpath('..').text.splitlines()[1].strip())
                # except Exception as e:
                #     print(e)
                #     min_ielts_score = None
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Enrollment (full-time)")]')
                    enrollment = int(ttt.find_element_by_xpath('..').text.splitlines()[1].strip().replace(",", ""))
                except Exception as e:
                    print(e)
                    enrollment = None
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Median grant amount")]')
                    median_grant = int(ttt.find_element_by_xpath('..').text.splitlines()[1].strip().replace(",", "").replace("$", ""))
                except Exception as e:
                    print(e)
                    median_grant = None
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Median public service starting salary")]')
                    median_public_salary = int(ttt.find_element_by_xpath('..').text.splitlines()[1].strip().replace(",", "").replace("$", ""))
                except Exception as e:
                    print(e)
                    median_public_salary = None
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Median private sector starting salary")]')
                    print(ttt.text)
                    median_private_salary = int(ttt.find_element_by_xpath('..').text.splitlines()[1].strip().replace(",", "").replace("$", ""))
                except Exception as e:
                    print(e)
                    median_private_salary = None
                try:
                    gender = driver.find_elements_by_class_name('vMPxk')[1].text.split('Female')[1]
                    female = float(gender.split('%')[0])
                    male = float(gender.split('%')[1].replace('Male', ''))
                except Exception as e:
                    print(e)
                    female = None
                    male = None
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Room and board")]')
                    living_expenses = int(ttt.find_element_by_xpath('..').text.splitlines()[1].strip().replace('$', '').replace(',', ""))
                except Exception as e:
                    print(e)
                    living_expenses = None
                try:
                    ttt = driver.find_element_by_xpath('//div[contains(span, "Full-time students receiving grants")]')
                    students_receiving_aid = float(ttt.find_element_by_xpath('..').text.splitlines()[1].strip().replace('%', ""))
                except Exception as e:
                    print(e)
                    students_receiving_aid = None

                LawGrad.objects.create(
                        university=uni,
                        enrollment=enrollment,
                        us_application_fee=us_application_fee,
                        int_application_fee=int_application_fee,
                        international=international,
                        male=male,
                        female=female,
                        acceptance_rate=acceptance_rate,
                        tuition =tuition,
                        us_deadline =us_deadline,
                        int_deadline =int_deadline,
                        rolling =rolling,
                        gpa =gpa,
                        fin_aid_director_name =fin_aid_director_name,
                        fin_aid_director_phone =fin_aid_director_phone,
                        students_receiving_aid =students_receiving_aid,
                        living_expenses=living_expenses,
                        lsat_score=lsat_score,
                        bar_passage_rate=bar_passage_rate,
                        median_grant=median_grant,
                        employed=employed,
                        median_private_salary=median_private_salary,
                        median_public_salary=median_public_salary

                )
                #
                # for j, t2 in enumerate(temp2):
                #     print(j, t2.text)


                #
                # try:
                #     deadline = int(temp[3].text.replace(",", ""))
                # except Exception as e:
                #     print(e)
                #     deadline = None



                #
                # try:
                #     uni_type = driver.find_elements_by_css_selector('dd')[3].text.split(',')[0]
                # except Exception as e:
                #     print(e)
                #     uni_type = None
                #


                # uni.uni_type = uni_type
                # uni.schools = schools_list
                # uni.engg_link = engg_link
                # uni.law_link = law_link
                # uni.med_link = med_link
                # uni.business_link = business_link
                # uni.save()

            else:
                continue

        return JsonResponse({"success": True})


class Test(APIView):
    def post(self, request, *args, **kwargs):
        # from random import random
        # from django.template.defaultfilters import slugify
        # universities = University.objects.all()
        # for university in universities:
        #     random1 = round(2*random(), 1)
        #     random2 = round(2*random(), 1)
        #     if university.med_link:
        #         engg = MedicineGrad.objects.filter(university=university).first()
        #         if engg.male and engg.female:
        #             print(engg.male, engg.female)
        #             engg.male = engg.male + random1
        #             engg.female = engg.female - random1
        #
        #             engg.male = round(engg.male - random2, 1)
        #             engg.female = round(engg.female +random2, 1)
        #             print(engg.male, engg.female)
        #             print()
        #             print()
        #             engg.save()

        # from urllib.request import urlopen as ureq
        # from bs4 import BeautifulSoup as Soup
        #
        # my_url = 'https://collegemajors101.com/'
        #
        # uClient = ureq(my_url)
        # page_html = uClient.read()
        # uClient.close()
        #
        # page_soup = Soup(page_html, "html.parser")
        #
        # containers = page_soup.findAll("div", {"id": "home-majors-listing"})[0].findAll('li')
        #
        # for li in containers:
        #     Major.objects.create(name=li.text)

        # for uni in University.objects.filter(rank__lte=100):
        #     uni.logo = uni.slug + ".png"
        #     uni.save()

        return JsonResponse({"success": True})

import random
class UniversityView(View):

    def get(self, request, *args, **kwargs ):
        uni_name = self.kwargs.get('uni_name')
        user = request.user

        university = University.objects.filter(slug__iexact=uni_name).first()
        rank = university.rank
        random_unis_id_list = list(University.objects.filter(rank__lte=rank+5, rank__gte=rank-5, country__name='United States').exclude(rank=rank).values_list('id', flat=True))
        random_unis_id_list = set(random.sample(random_unis_id_list, min(len(random_unis_id_list), 5)))
        other_unis = University.objects.filter(id__in=random_unis_id_list)

        if not university:
            return render(request, "error.html", context={})

        context = dict()
        context['university'] = university
        if enable_otp:
            key_id = "rzp_live_6MxRlb7ZCO7XaB"
            client = razorpay.Client(auth=(key_id, "fGjvMdo8cs7o48pXou5sa3Y5"))
        else:
            key_id = "rzp_test_QiGwvmuHqNFHk5"
            client = razorpay.Client(auth=(key_id, "v4gHikpMnv2DVK0OK6CQ9Ttm"))
        context['key_id'] = key_id

        today = now()
        if not user.is_anonymous:
            if request.user.student.plan_valid_till < today:
                context['explorer_access'] = False
            else:
                context['explorer_access'] = True
        else:
            context['explorer_access'] = False

        context['other_unis'] = other_unis
        context['the'] = False
        if university.name.startswith('University'):
            context['the'] = True

        return render(request, template_name='university/univ-information.html', context=context)

    def post(self, request, *args, **kwargs):

        try:
            user = request.user
            price_inr = 75000
            price_usd = 1200
            validity = 12

            amount = request.POST.get('amount')
            currency = request.POST.get('currency')
            service_name = "YMExplorer"

            if enable_otp:
                key_id = "rzp_live_6MxRlb7ZCO7XaB"
                client = razorpay.Client(auth=(key_id, "fGjvMdo8cs7o48pXou5sa3Y5"))
            else:
                key_id = "rzp_test_QiGwvmuHqNFHk5"
                client = razorpay.Client(auth=(key_id, "v4gHikpMnv2DVK0OK6CQ9Ttm"))

            payment_id = request.POST.get('razorpay_payment_id')
            payment_obj = client.payment.fetch(payment_id)

            subject = "Thank you for your purchase - Yash Mittra"

            msg = "Dear " + user.first_name + " " + user.last_name + ",<br><br>We have successfully received your" \
                  " order. We look forward to helping you with your application." \
                  " We strongly believe that the data provided to you through the YMExplorer will save you months of" \
                  " research and money.<br><br>In case you face any issues, feel free to connect with us." \
                  "<br><br>Best Regards,<br>YMGrad"

            if currency == "inr":
                if payment_obj['status'] == 'authorized' and int(amount) >= price_inr:
                    client.payment.capture(payment_id, amount)
                    payment = Payment.objects.create(user=user, payment_id=payment_id, status='Paid', amount=amount, service_name=service_name, currency="INR")
                    student = user.student
                    student.payments.add(payment)
                    send_email.delay(receiver=[user.email, "mittrayash@gmail.com"], email_message=msg, subject=subject)
                    if student.plan_valid_till < now():
                        student.plan_valid_till = date.today() + relativedelta(months=+validity)
                    else:
                        student.plan_valid_till = student.plan_valid_till + relativedelta(months=+validity)
                    student.save()
                    messages.success(request, "Thank You for your payment. Your access to YMExplorer has been activated.")
                    detail = user.first_name + " " + user.last_name + " bought " + service_name + "."
                    Statement.objects.create(type='Credit', detail=detail, amount=price_inr)
            elif currency == "usd":
                if payment_obj['status'] == 'authorized' and int(amount) >= price_usd:
                    # client.payment.capture(payment_id, amount)
                    payment = Payment.objects.create(user=user, payment_id=payment_id, status='Paid', amount=amount, service_name=service_name, currency="USD")
                    student = user.student
                    student.payments.add(payment)
                    send_email.delay(receiver=[user.email, "mittrayash@gmail.com"], email_message=msg, subject=subject)
                    if student.plan_valid_till < now():
                        student.plan_valid_till = date.today() + relativedelta(months=+validity)
                    else:
                        student.plan_valid_till = student.plan_valid_till + relativedelta(months=+validity)
                    student.save()
                    messages.success(request, "Thank You for your payment. Your access to YMExplorer has been activated.")
                    detail = user.first_name + " " + user.last_name + " bought " + service_name + "."
                    Statement.objects.create(type='Credit', detail=detail, amount=price_inr)

        except Exception as e:
            print(e)
            messages.error(request, "Unfortunately, we are unable to process your request at this time. In case any funds have been deducted from your account, please contact us and we will resolve the issue for you.")
        return redirect("/account/dashboard/")


class GetUniNames(APIView):

    def post(self, request, *args, **kwargs):
        val = request.POST.get('valu')
        unis = list(UndergradUniversity.objects.filter(Q(name__search=val) | Q(name__istartswith=val) | Q(name__icontains=val)).values_list('name', flat=True))[:5]
        limit = len(unis)

        return JsonResponse({"unis": unis, 'limit': limit})


class GetTargetUniversity(APIView):

    def post(self, request, *args, **kwargs):
        val = request.POST.get('val')
        unis = list(University.objects.filter(Q(name__search=val) | Q(name__istartswith=val) | Q(name__icontains=val)).values_list('name', flat=True))[:5]
        limit = len(unis)

        return JsonResponse({"unis": unis, 'limit': limit})


