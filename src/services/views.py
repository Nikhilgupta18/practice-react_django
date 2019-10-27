from django.shortcuts import render, redirect
from django.views import View
from services.models import Service, SopPrice, LORPrice, UnivShortlising, GreConsultation, ToeflConsultation, HistoryDraft, FreeConsultation, CompleteApplication, CreateAdmissionPlan, Resume, ServiceUser, Payment, Statement, Testimonial
from rest_framework.views import APIView
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
import razorpay
from services.models import consult_list
from inv.settings import enable_otp
from account.tasks import send_email
from django.contrib.auth import get_user_model
from django.core import serializers



User = get_user_model()

consult_list = [
    'Google Hangouts',
    'Call',
]


class ServiceHandler(View):
    def get(self, request, *args, **kwargs):
        service_name = kwargs.get('service_name')

        if not Service.objects.filter(link=service_name).exists():
            return redirect('error.html')

        service = Service.objects.filter(link=service_name).first()

        context = dict()
        context['consult_list'] = consult_list
        context['service'] = service
        service_name = Service.objects.all()
        context['service_name'] = service_name
        context['testimonials'] = Testimonial.objects.filter(service=service).order_by('-timestamp')

        if enable_otp:
            key_id = "rzp_live_6MxRlb7ZCO7XaB"
            client = razorpay.Client(auth=(key_id, "fGjvMdo8cs7o48pXou5sa3Y5"))
        else:
            key_id = "rzp_test_QiGwvmuHqNFHk5"
            client = razorpay.Client(auth=(key_id, "v4gHikpMnv2DVK0OK6CQ9Ttm"))

        context['key_id'] = key_id
        if not request.user.is_anonymous:
            if ServiceUser.objects.filter(user=request.user).exists():
                context['service_user'] = True

        return render(request, template_name="service/services.html", context=context)


class ServiceHandlerAPIView(APIView):
    queryset            = Service.objects.all()
    # serializer_class    = PostSerializer
    # permission_classes  = [IsOwnerOrReadOnly]

    # def get_serializer_context(self):
    #     context = get_serializer_context()
    #     context['request'] = self.request
    #     return context

class SopAmount(APIView):

    def post(self, request, *args, **kwargs):
        try:
            customization = self.request.POST.get('customizations')
            currency = self.request.POST.get('currency')
            user_id = self.request.POST.get('user_id')
            raztext = "SOP Drafting"
            if user_id != "None":
                if User.objects.filter(id=user_id).exists():
                    user = User.objects.filter(id=user_id).first()
                else:
                    user = None
            else:
                user = None

            if SopPrice.objects.filter(customizations=customization).exists():
                price_inr = SopPrice.objects.filter(customizations=customization).first().price_inr
                price_usd = SopPrice.objects.filter(customizations=customization).first().price_usd

                if not user:
                    if currency == "inr":
                        link = "/account/login/?next=/service/premium/sop-drafting"
                        link_text = "Login And Pay"

                        return JsonResponse({'price':price_inr,'price_d': '₹ ','link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = "/account/login/?next=/service/premium/sop-drafting"
                        link_text = "Login And Pay"
                        return JsonResponse({'price':price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text,'curr': "USD",'raztext':raztext})
                else:
                    if currency == "inr":
                        link = SopPrice.objects.filter(customizations=customization).first().link_inr
                        link_text = "Pay"
                        return JsonResponse({'price':price_inr, 'link': link,'price_d': '₹ ', 'link_text':link_text, 'curr': "INR",'raztext':raztext})
                    else:
                        link = SopPrice.objects.filter(customizations=customization).first().link_usd
                        link_text = "Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})

            else:
                return JsonResponse({'error': "No such customization exists."})

        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)})


class LorAmount(APIView):

    def post(self, request, *args, **kwargs):
        try:

            numLor = self.request.POST.get('numLor')
            currency = self.request.POST.get('currency')
            user_id = self.request.POST.get('user_id')
            raztext = "LOR Drafting"
            if user_id != "None":
                if User.objects.filter(id=user_id).exists():
                    user = User.objects.filter(id=user_id).first()
                else:
                    user = None
            else:
                user = None

            if LORPrice.objects.filter(customizations=numLor).exists():
                price_inr = LORPrice.objects.filter(customizations=numLor).first().price_inr
                price_usd = LORPrice.objects.filter(customizations=numLor).first().price_usd

                if not user:
                    if currency == "inr":
                        link = "/account/login/?next=/service/premium/lor-drafting"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = "/account/login/?next=/service/premium/lor-drafting"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
                else:

                    if currency == "inr":
                        link = LORPrice.objects.filter(customizations=numLor).first().link_inr
                        link_text = "Pay"
                        return JsonResponse({'price':price_inr,'price_d': '₹ ','link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = LORPrice.objects.filter(customizations=numLor).first().link_usd
                        link_text = "Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
            else:
                return JsonResponse({'error': "No such customization exists."})

        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)})


class UniversityShortlisting(APIView):

    def post(self, request, *args, **kwargs):
        try:
            user_id = self.request.POST.get('user_id')
            currency = self.request.POST.get('currency')
            topic = self.request.POST.get('topic')
            raztext = "Profile Evaluation & University Shortlisting"
            if user_id != "None":
                if User.objects.filter(id=user_id).exists():
                    user = User.objects.filter(id=user_id).first()
                else:
                    user = None
            else:
                user = None

            if UnivShortlising.objects.filter(service=topic).exists():
                price_inr = UnivShortlising.objects.filter(service=topic).first().price_inr
                print(price_inr)
                price_usd = UnivShortlising.objects.filter(service=topic).first().price_usd

                if not user:
                    if currency == "inr":
                        link = "/account/login/?next=/service/premium/profile-evaluation"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = "/account/login/?next=/service/premium/profile-evaluation"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
                else:

                    if currency == "inr":
                        link = UnivShortlising.objects.filter(service=topic).first().link_inr
                        link_text = "Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = UnivShortlising.objects.filter(service=topic).first().link_usd
                        link_text = "Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
            else:
                return JsonResponse({'error': "No such customization exists."})

        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)})


class GreConsult(APIView):
    def post(self, request, *args, **kwargs):
        try:

            user_id = self.request.POST.get('user_id')
            currency = self.request.POST.get('currency')
            topic = self.request.POST.get('topic')
            raztext = "GRE Consultation"
            if user_id != "None":
                if User.objects.filter(id=user_id).exists():
                    user = User.objects.filter(id=user_id).first()
                else:
                    user = None
            else:
                user = None

            if GreConsultation.objects.filter(service=topic).exists():
                price_inr = GreConsultation.objects.filter(service=topic).first().price_inr
                print(price_inr)
                price_usd = GreConsultation.objects.filter(service=topic).first().price_usd

                if not user:
                    if currency == "inr":
                        link = "/account/login/?next=/service/premium/gre-consultation"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = "/account/login/?next=/service/premium/gre-consultation"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
                else:

                    if currency == "inr":
                        link = GreConsultation.objects.filter(service=topic).first().link_inr
                        link_text = "Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = GreConsultation.objects.filter(service=topic).first().link_usd
                        link_text = "Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
            else:
                return JsonResponse({'error': "No such customization exists."})

        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)})


class ToeflConsult(APIView):
    def post(self, request, *args, **kwargs):
        try:

            user_id = self.request.POST.get('user_id')
            currency = self.request.POST.get('currency')
            topic = self.request.POST.get('topic')
            raztext = "TOEFL Consultation"
            if user_id != "None":
                if User.objects.filter(id=user_id).exists():
                    user = User.objects.filter(id=user_id).first()
                else:
                    user = None
            else:
                user = None

            if ToeflConsultation.objects.filter(service=topic).exists():
                price_inr = ToeflConsultation.objects.filter(service=topic).first().price_inr
                print(price_inr)
                price_usd = ToeflConsultation.objects.filter(service=topic).first().price_usd

                if not user:
                    if currency == "inr":
                        link = "/account/login/?next=/service/premium/toefl-consultation"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = "/account/login/?next=/service/premium/toefl-consultation"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
                else:

                    if currency == "inr":
                        link = ToeflConsultation.objects.filter(service=topic).first().link_inr
                        link_text = "Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = ToeflConsultation.objects.filter(service=topic).first().link_usd
                        link_text = "Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
            else:
                return JsonResponse({'error': "No such customization exists."})

        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)})


class HisDraft(APIView):
    def post(self, request, *args, **kwargs):
        try:

            user_id = self.request.POST.get('user_id')
            currency = self.request.POST.get('currency')
            topic = self.request.POST.get('topic')
            raztext = "Personal History Statement Drafting"
            if user_id != "None":
                if User.objects.filter(id=user_id).exists():
                    user = User.objects.filter(id=user_id).first()
                else:
                    user = None
            else:
                user = None

            if HistoryDraft.objects.filter(service=topic).exists():
                price_inr = HistoryDraft.objects.filter(service=topic).first().price_inr
                print(price_inr)
                price_usd = HistoryDraft.objects.filter(service=topic).first().price_usd

                if not user:
                    if currency == "inr":
                        link = "/account/login/?next=/service/premium/history-draft"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = "/account/login/?next=/service/premium/history-draft"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
                else:

                    if currency == "inr":
                        link = HistoryDraft.objects.filter(service=topic).first().link_inr
                        link_text = "Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = HistoryDraft.objects.filter(service=topic).first().link_usd
                        link_text = "Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
            else:
                return JsonResponse({'error': "No such customization exists."})

        except Exception as e:
            print(e)
            return JsonResponse({'error': "An Error Occurred."})


class CompleteApp(APIView):
    def post(self, request, *args, **kwargs):
        try:

            user_id = self.request.POST.get('user_id')
            currency = self.request.POST.get('currency')
            topic = self.request.POST.get('topic')
            raztext = "Complete Application Help"
            if user_id != "None":
                if User.objects.filter(id=user_id).exists():
                    user = User.objects.filter(id=user_id).first()
                else:
                    user = None
            else:
                user = None

            if CompleteApplication.objects.filter(service=topic).exists():
                price_inr = CompleteApplication.objects.filter(service=topic).first().price_inr
                print(price_inr)
                price_usd = CompleteApplication.objects.filter(service=topic).first().price_usd

                if not user:
                    if currency == "inr":
                        link = "/account/login/?next=/service/premium/complete-application"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = "/account/login/?next=/service/premium/complete-application"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
                else:

                    if currency == "inr":
                        link = CompleteApplication.objects.filter(service=topic).first().link_inr
                        link_text = "Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = CompleteApplication.objects.filter(service=topic).first().link_usd
                        link_text = "Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
            else:
                return JsonResponse({'error': "No such customization exists."})

        except Exception as e:
            print(e)
            return JsonResponse({'error': "An Error Occurred."})


class CreateAdmission(APIView):
    def post(self, request, *args, **kwargs):
        try:

            user_id = self.request.POST.get('user_id')
            currency = self.request.POST.get('currency')
            topic = self.request.POST.get('topic')
            raztext = "Create Admissions Preparation Plan"
            if user_id != "None":
                if User.objects.filter(id=user_id).exists():
                    user = User.objects.filter(id=user_id).first()
                else:
                    user = None
            else:
                user = None

            if CreateAdmissionPlan.objects.filter(service=topic).exists():
                price_inr = CreateAdmissionPlan.objects.filter(service=topic).first().price_inr
                print(price_inr)
                price_usd = CreateAdmissionPlan.objects.filter(service=topic).first().price_usd

                if not user:
                    if currency == "inr":
                        link = "/account/login/?next=/service/premium/admission-preparation"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = "/account/login/?next=/service/premium/admission-preparation"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
                else:

                    if currency == "inr":
                        link = CreateAdmissionPlan.objects.filter(service=topic).first().link_inr
                        link_text = "Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = CreateAdmissionPlan.objects.filter(service=topic).first().link_usd
                        link_text = "Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
            else:
                return JsonResponse({'error': "No such customization exists."})

        except Exception as e:
            print(e)
            return JsonResponse({'error': "An Error Occurred."})


class ResumeHelp(APIView):

    def post(self, request, *args, **kwargs):
        try:

            user_id = self.request.POST.get('user_id')

            currency = self.request.POST.get('currency')
            raztext = "Resume Help"
            topic = self.request.POST.get('topic')
            if user_id != "None":
                if User.objects.filter(id=user_id).exists():
                    user = User.objects.filter(id=user_id).first()
                else:
                    user = None
            else:
                user = None

            if Resume.objects.filter(service=topic).exists():
                price_inr = Resume.objects.filter(service=topic).first().price_inr
                price_usd = Resume.objects.filter(service=topic).first().price_usd

                if not user:
                    if currency == "inr":
                        link = "/account/login/?next=/service/premium/resume-help"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = "/account/login/?next=/service/premium/resume-help"
                        link_text = "Login And Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
                else:
                    if currency == "inr":
                        link = Resume.objects.filter(service=topic).first().link_inr
                        link_text = "Pay"
                        return JsonResponse({'price': price_inr, 'price_d': '₹ ', 'link': link, 'link_text': link_text, 'curr': "INR", 'raztext':raztext})
                    else:
                        link = Resume.objects.filter(service=topic).first().link_usd
                        link_text = "Pay"
                        return JsonResponse({'price': price_usd, 'link': link, 'price_d': '$ ', 'link_text': link_text, 'curr': "USD",'raztext':raztext})
            else:
                return JsonResponse({'error': "No such customization exists."})

        except Exception as e:
            print(e)
            return JsonResponse({'error': "An Error Occurred."})


class FreeConsult(View):

    def post(self, request, *args, **kwargs):

        user = request.user
        if not user.is_authenticated:
            messages.error(request, "You cannot access this service without logging in.")
            return redirect('/')

        date = request.POST.get("contact_date")
        mobile = request.POST.get("mobile")
        service1 = request.POST.get("service")
        service_link = Service.objects.filter(heading=service1).first().link


        context = dict()
        # service = Services.objects.filter(link=service_name).first()
        # context['service'] = service

        try:

            email_message = str(user) + " wants a free consultations" + "<br><b>country: </b>" + user.student.country.name + "<br><b>Service: </b>" + service1 + "<br><b>medium of contact: </b>" + "Call" + "<br><b>Preffered Date: </b>" + date + "<br><b>mobile number: </b>" + mobile
            email_msg_for_user = "Dear " + str(user.first_name) + ",<br> Your free consultation" + "has been booked." + "<br><b>Service: </b>" + service1 + "<br><b>medium of contact: </b>" + "Call" + "<br><b>Preffered Date: </b>" + date + "<br><b>mobile number: </b>" + mobile

            FreeConsultation.objects.create(
                user=user,
                date=date,
                number=mobile,
                service=service1,
            )

            if enable_otp:
                send_email.delay(receiver=["mittrayash@gmail.com"],
                                 email_message=email_message,
                                 subject="Free Consultation Booking at YMGrad.com")
                send_email.delay(receiver=[user.email],
                                 email_message=email_msg_for_user,
                                 subject="Your Free Consultation Booking at YMGrad.com")
            else:
                print("Not sending email because in development mode.")
        except Exception as e:
            print(e)

        return redirect("/service/premium/" + service_link)


class AllServices(View):

    def get(self, request):
        services = Service.objects.all()
        context = dict()
        context['services'] = services
        return render(request, template_name="react.html", context=context)

#
# class ServiceHandlerAPI(View):
#     def get(selfself,request):



class Purchase(View):

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            amount = request.POST.get('amount')
            service_name = request.POST.get('service_name')
            customizations = None
            if service_name == "LOR Drafting":
                customizations = request.POST.get('customizations')
                service = LORPrice.objects.filter(customizations=customizations).first()

            elif service_name == "SOP Drafting":
                customizations = request.POST.get('customizations')
                service = SopPrice.objects.filter(customizations=customizations).first()

            elif service_name == "Profile Evaluation & University Shortlisting":
                service = UnivShortlising.objects.first()

            elif service_name == "Complete Application Help":
                service = CompleteApplication.objects.first()

            elif service_name == "GRE Consultation":
                service = GreConsultation.objects.first()

            elif service_name == "TOEFL Consultation":
                service = ToeflConsultation.objects.first()

            elif service_name == "Personal History Statement Drafting":
                service = HistoryDraft.objects.first()

            elif service_name == "Resume Help":
                service = Resume.objects.first()

            elif service_name == "Create Admissions Preparation Plan":
                service = CreateAdmissionPlan.objects.first()

            price_inr = service.price_inr
            price_usd = service.price_usd

            currency = request.POST.get('currency')

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
                  "<br><br><b>Service Name: </b>" + service_name + "<br>" \
                  "<b>Customizations:</b> " + str(customizations) + "<br><br>" \
                  " We can personally assure you that your application is in good hands and that we will take care of" \
                  " everything here on out.<br>" \
                  "<br>From now on, we share the same goal: Getting you into the best university possible as per your " \
                  "requirements.<br>" \
                  "<br>Someone from our team will be in touch with you within 2 working" \
                  " days and will personally work with you on your application.<br><br>Best Regards,<br>Yash"

            if currency == "inr":
                if payment_obj['status'] == 'authorized' and int(amount) >= price_inr:
                    client.payment.capture(payment_id, amount)
                    payment = Payment.objects.create(user=user, payment_id=payment_id, status='Paid', amount=amount, service_name=service_name, currency="INR")
                    student = user.student
                    student.payments.add(payment)
                    ServiceUser.objects.create(user=user,
                                               service_name=service_name,
                                               customizations=customizations,
                                               payment=payment,
                                               )

                    send_email.delay(receiver=[user.email, "mittrayash@gmail.com"], email_message=msg, subject=subject)
                    messages.success(request, "Thank You for your payment. Your order has been received and will be processed soon.")
                    detail = user.first_name + " " + user.last_name + " bought " + service_name + "."
                    Statement.objects.create(type='Credit', detail=detail, amount=price_inr)
            elif currency == "usd":
                if payment_obj['status'] == 'authorized' and int(amount) >= price_usd:
                    # client.payment.capture(payment_id, amount)  # currency field is required
                    payment = Payment.objects.create(user=user, payment_id=payment_id, status='Paid', amount=amount, service_name=service_name, currency="USD")
                    student = user.student
                    student.payments.add(payment)
                    ServiceUser.objects.create(user=user,
                                               service_name=service_name,
                                               customizations=customizations,
                                               payment=payment,
                                               )

                    send_email.delay(receiver=[user.email, "mittrayash@gmail.com"], email_message=msg, subject=subject)
                    messages.success(request, "Thank You for your payment. Your order has been received and will be processed soon.")
                    detail = user.first_name + " " + user.last_name + " bought " + service_name + "."
                    Statement.objects.create(type='Credit', detail=detail, amount=price_inr)

        except Exception as e:
            print(e)
            messages.error(request, "Unfortunately, we are unable to process your request at this time. In case any funds have been deducted from your account, please contact us and we will resolve the issue for you.")
        return redirect("/account/dashboard/")


class PublishTestimonial(View):
    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            messages.error(request, "You cannot access this resource.")
            return render(request, "error.html", context={})

        if not ServiceUser.objects.filter(user=request.user).exists():
            messages.error(request, "You cannot access this resource.")
            return render(request, "error.html", context={})

        context = dict()
        service = self.kwargs.get('service_name')
        service = Service.objects.filter(heading=service).first()

        context['services'] = Service.objects.all()
        context['service'] = service

        return render(request, template_name='service/write-testimonial.html', context=context)

    def post(self, request, *args, **kwargs):

        if not ServiceUser.objects.filter(user=request.user).exists():
            messages.error(request, "You cannot access this resource.")
            return render(request, "error.html", context={})

        context = dict()
        rating = request.POST.get('rating')
        headline = request.POST.get('headline')
        details = request.POST.get('details')
        service = request.POST.get('service')
        is_anon = request.POST.get('is_anon')

        if is_anon == 'true':
            is_anon = True
        else:
            is_anon = False

        service = Service.objects.filter(heading=service).first()
        user = request.user

        t = Testimonial.objects.create(user=user, service=service, rating=rating, headline=headline, details=details, anonymous=is_anon)

        if 'imgInp' in request.FILES:
            image = request.FILES['imgInp']
            t.path = image

        if enable_otp:
            msg = str(user.first_name) + str(user.last_name) + " posted a testimonial for the " + str(service.heading) + "<br><br>Rating: " + str(rating) + "<br>Heading: " + str(headline) + "<br>Description: " + str(details)  + "<br>"
            send_email.delay(receiver="mittrayash@gmail.com", email_message=msg, subject="Testimonial posted on YMGrad.")
        else:
            print("Not sending email because in development mode.")

        messages.success(request, "Your testimonial has been posted!")
        t.save()

        context['services'] = Service.objects.all()
        context['service'] = service

        return render(request, template_name='service/write-testimonial.html', context=context)


