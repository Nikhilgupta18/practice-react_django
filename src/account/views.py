from django.template.defaultfilters import slugify
import logging
from django.db.models import Q
from datetime import datetime, timedelta, timezone, date
from rest_framework.views import APIView
from account.tasks import send_backup_with_email
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.utils.timezone import now
from django.contrib import messages
import random, string
from django.http import JsonResponse
from django.template.loader import render_to_string
from inv.utils import send_sms
from django.core.files.images import get_image_dimensions
from account.tasks import send_email
from inv.utils import send_email as s_e
from .models import Country, Student, OtpDB, how_did_you_hear_about_us_list, GradProfile, GREScore, MCATScore, IELTSScore, TOEFLScore, Major, Referral
from .forms import AuthenticationForm
from django.contrib.auth import get_user_model
from inv.settings import enable_otp
from university.models import grad_streams_list, University
from .models import UndergradUniversity, Decisions, State
from services.models import ServiceUser
from inv.views import countries
from article.models import Article
import sys
from django.db import models
from PIL import Image as Img
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
User = get_user_model()

# Get an instance of a logger
logger = logging.getLogger(__name__)


class RegisterInvestor(View):
    def get(self, request, *args, **kwargs):
        referred_by = request.GET.get('ref')
        if User.objects.filter(username=referred_by).exists():
            referred_by = User.objects.filter(username=referred_by).first()
        else:
            referred_by = None
        countries = Country.objects.all()

        if request.user.is_authenticated:
            messages.warning(request, "You are already registered.")
            return redirect("/dashboard/")
        context = dict()
        context['how_did_you_hear_about_us'] = how_did_you_hear_about_us_list
        context['countries'] = countries
        context['ref'] = referred_by

        return render(request, "account/signup1.html", context=context)

    def post(self, request, *args, **kwargs):

        countries = Country.objects.all()

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        hear_about_us = request.POST.get("hear_about_us")
        mobile = request.POST.get("mobile")
        country = request.POST.get("country")
        state = request.POST.get("state")
        referral_code = request.POST.get("ref")
        referred_by = referral_code
        if User.objects.filter(username=referred_by).exists():
            referred_by = User.objects.filter(username=referred_by).first()
        else:
            referred_by = None

        context = dict()
        context['countries'] = countries
        context['email'] = email
        context['first_name'] = first_name
        context['last_name'] = last_name
        context['username'] = username
        context['mobile'] = mobile
        context['country'] = country
        context['state'] = state
        context['how_did_you_hear_about_us'] = how_did_you_hear_about_us_list
        context['ref'] = referral_code

        country = Country.objects.filter(name=country).first()
        state = State.objects.filter(name=state).first()

        if len(username) < 4:
            messages.error(request, "Username must be at least 4 characters long.")
            return render(request, template_name='account/signup1.html', context=context)

        if ' ' in username:
            messages.error(request, "Username cannot contain white space.")
            return render(request, template_name='account/signup1.html', context=context)

        if '#' in username:
            messages.error(request, "Username cannot contain '#'.")
            return render(request, template_name='account/signup1.html', context=context)

        if password != confirm_password:
            context['password_unmatch'] = 'Password and Confirm Password must match.'
            return render(request, template_name='account/signup1.html', context=context)

        if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists() or Student.objects.filter(mobile=mobile).exists():
            context['user_found'] = 'You already seem to have an account. Please log in instead.'
            return render(request, template_name='account/signup1.html', context=context)

        if 'profile_picture' in request.FILES:
            image = request.FILES['profile_picture']

            width, height = get_image_dimensions(image)
            hor_len = width / height

            if hor_len > 1.5:
                print("Rejecting too long image.")
                context[
                    'errors'] = "Image too long horizontally and too short vertically. Approximately square image needed."
                return render(request, 'account/signup1.html', context)
            if hor_len < 0.5:
                print("Rejecting too long image.")
                context[
                    'errors'] = "Image too short horizontally and too long vertically. Approximately square image needed."
                return render(request, 'account/signup1.html', context)
            if image.size > 4194304:
                context['errors'] = "Image Size Too Big. Please upload a profile picture with an image size less than 4MB."
                return render(request, 'account/signup1.html', context)

        try:
            user = User.objects.create(
                username=username.strip(),
                email=email.strip(),
                first_name=first_name.strip().title(),
                last_name=last_name.strip().title(),
                is_active=False,
                is_staff=False,
                is_superuser=False,
            )
            student = Student.objects.create(
                user=user,
                mobile=mobile.strip(),
                how_did_you_hear_about_us=hear_about_us.strip(),
                country=country,
                state=state
            )
            if referred_by:
                Referral.objects.create(user=user, referred_by=referred_by)

            user.set_password(password)
            user.save()

            if 'profile_picture' in request.FILES:
                image = request.FILES['profile_picture']
                width, height = get_image_dimensions(image)

                img = Img.open(BytesIO(image.read()))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                new_width = 800
                img.thumbnail((new_width, new_width * height / width), Img.ANTIALIAS)
                # img.thumbnail((self.path.width / 1.5, self.path.height / 1.5), Img.ANTIALIAS)
                output = BytesIO()
                img.save(output, format='JPEG', quality=70)

                output.seek(0)
                image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % image.name.split('.')[0],
                                             'image/jpeg', sys.getsizeof(output), None)
                student.path = image
                student.save()

            context['email'] = email

            ########################### OTP DB

            otp = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(8))
            OtpDB.objects.create(user=user, otp=otp)
            link = "https://www.ymgrad.com/account/confirm-email/" + username + "/" + otp + "/"
            email_message = "Dear " + first_name + " " + last_name + ",<br/><br/>" + \
                            "Please use the following link to continue registration at YMGrad.com<br><br>" + \
                            link + "<br/><br/>" + "I look forward to helping you get admits from some of the world's top-most universities by sharing with you some of the hard-earned secrets I have learned about the admissions process by years of research.<br/><br/>" + \
                            "To learn some of my tips and tricks to maximize chances of admit, please complete your registration.<br><br>" + \
                            "Best,<br>" + "The YMGrad Team"

            print('Link', 'http://localhost:8000/account/confirm-email/' + username + '/' + str(otp) + '/')
            if enable_otp:
                send_email.delay(receiver=email, email_message=email_message, subject="Confirm your Email | Begin your StudyAbroad Journey Now!")
            else:
                print("Not sending email because in development mode.")
        except Exception as e:
            print(e)
            context['errors'] = e

            return render(request, "account/signup1.html", context)

        return render(request, template_name='account/email_sent.html', context=context)


class CustomLoginView(LoginView):
    """
    Custom login view.
    """

    form_class = AuthenticationForm
    template_name = 'account/login.html'


class ConfirmEmail(View):

    def get(self, request, *args, **kwargs):

        otp = self.kwargs.get('otp')
        username = self.kwargs.get('username')

        user = User.objects.filter(username=username).first()

        if user:
            db_otp = OtpDB.objects.filter(user=user).first()

            if otp == db_otp.otp:
                db_otp.verified = True
                user.is_active = True
                db_otp.save()
                user.save()

                referral = Referral.objects.filter(user=user, confirm=False).first()
                if referral:
                    ref_user = referral.referred_by
                    ref_student = ref_user.student
                    referral.confirm = True
                    ref_student.no_of_referrals = ref_student.no_of_referrals + 1
                    referral.save()
                    ref_student.save()
                    subject = str(user.first_name) + " " + (user.last_name) + " signed up with your referral code!"
                    msg = "Dear " + str(ref_user.first_name) + ",<br>You are now one step closer to any free study material of your choice." \
                            "<br>" + str(user.first_name) + " " + (user.last_name) + " just signed up with your referral code! See your referral signups on your <a href='https://www.ymgrad.com/account/dashboard/'>dashboard</a>!<br>" \
                            "<br>Increase your chances by sharing your <b>referral code</b> with more people!<br><br>" \
                            "<b>Your referral code: </b>  https://www.ymgrad.com/account/register?ref=" + ref_user.username + "<br><br>" \
                            "The winners will be announced and notified at the end of the month. All the best!<br><br>" \
                            "Best,<br>Team YMGrad"
                    send_email.delay(receiver=[ref_user.email], email_message=msg, subject=subject)

            else:
                messages.error(request, "Invalid Link. Please try again.")
                return redirect("/")
        else:
            return redirect('/')
        # messages.add_message(request, messages.SUCCESS, "Congo!")
        # return redirect('/account/login/')
        context = dict()
        context['success_msg'] = True
        context['form'] = AuthenticationForm
        return render(request, 'account/login.html', context=context)


class RegisterInvestor2(View):

    def get(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        user = User.objects.filter(username=username).first()
        otp_db_obj = OtpDB.objects.filter(user=user).first()

        if request.user != user:
            return render(request, 'error.html', context={})

        if user.student.complete_profile:
            return render(request, 'error.html', context={})

        hear_about_us               = request.POST.get("hear_about_us")  #
        backlogs                    = request.POST.get('backlogs')  #
        area_of_study               = request.POST.get('area_of_study')  #
        undergrad_uni               = request.POST.get('undergrad_uni')  #
        has_taken_gre               = request.POST.get('has_taken_gre')  #
        gre_verbal                  = request.POST.get('gre_verbal')  #
        gre_quant                   = request.POST.get('gre_quant')  #
        gre_awa                     = request.POST.get('gre_awa')  #
        mcat_chemical_physical      = request.POST.get('mcat_chemical_physical')  #
        mcat_critical_analysis      = request.POST.get('mcat_critical_analysis')  #
        mcat_biologic_biochemical   = request.POST.get('mcat_biologic_biochemical')  #
        mcat_psycho_social_biological = request.POST.get('mcat_psycho_social_biological')  #
        gmat                        = request.POST.get('gmat')  #
        lsat                        = request.POST.get('lsat')  #
        has_taken_toefl             = request.POST.get('has_taken_toefl')  #
        toefl_reading               = request.POST.get('toefl_reading')  #
        toefl_speaking              = request.POST.get('toefl_speaking')  #
        toefl_listening             = request.POST.get('toefl_listening')  #
        toefl_writing               = request.POST.get('toefl_writing')  #
        ielts_reading               = request.POST.get('ielts_reading')  #
        ielts_speaking              = request.POST.get('ielts_speaking')  #
        ielts_listening             = request.POST.get('ielts_listening')  #
        ielts_writing               = request.POST.get('ielts_writing')  #
        cgpa                        = request.POST.get('cgpa')  #
        cgpa_out_of                 = request.POST.get('cgpa_out_of')  #
        major                      = request.POST.get('major')  #
        work_ex_months              = request.POST.get('work_ex_months')  #
        research_papers             = request.POST.get('research_papers')  #
        int_term                    = request.POST.get('int_term')  #
        int_year                    = request.POST.get('int_year')  #
        target_university           = request.POST.get('target_university')  #
        target_major                = request.POST.get('target_major')  #

        context = dict()
        context['hear_about_us'] = hear_about_us
        context['username'] = username
        context['areas_of_study'] = grad_streams_list
        context['majors'] = list(Major.objects.all().values_list('name', flat=True).order_by('name'))

        context['backlogs'] = backlogs
        context['area_of_study'] = area_of_study
        context['undergrad_uni'] = undergrad_uni
        context['gre_verbal'] = gre_verbal
        context['has_taken_gre'] = has_taken_gre
        context['gre_quant'] = gre_quant
        context['gre_awa'] = gre_awa
        context['mcat_chemical_physical'] = mcat_chemical_physical
        context['mcat_critical_analysis'] = mcat_critical_analysis
        context['mcat_biologic_biochemical'] = mcat_biologic_biochemical
        context['mcat_psycho_social_biological'] = mcat_psycho_social_biological
        context['gmat'] = gmat
        context['lsat'] = lsat
        context['has_taken_toefl'] = has_taken_toefl
        context['toefl_reading'] = toefl_reading
        context['toefl_speaking'] = toefl_speaking
        context['toefl_listening'] = toefl_listening
        context['toefl_writing'] = toefl_writing
        context['ielts_reading'] = ielts_reading
        context['ielts_speaking'] = ielts_speaking
        context['ielts_listening'] = ielts_listening
        context['ielts_writing'] = ielts_writing
        context['cgpa'] = cgpa
        context['cgpa_out_of'] = cgpa_out_of
        context['major'] = major
        context['work_ex_months'] = work_ex_months
        context['research_papers'] = research_papers
        context['int_term'] = int_term
        context['int_year'] = int_year
        context['target_university'] = target_university
        context['target_major'] = target_major

        # for ios mac
        context['universities'] = list(University.objects.filter(country__name__in=countries).order_by('name').values_list('name', flat=True))
        context['ug_universities'] = list(UndergradUniversity.objects.all().order_by('name').values_list('name', flat=True))


        # malicious request
        if not otp_db_obj:
            return redirect('/')

        return render(request, template_name="account/signup2.html", context=context)

    def post(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        user = User.objects.filter(username=username).first()
        otp_db_obj = OtpDB.objects.filter(user=user).first()

        if not otp_db_obj:
            return redirect('/')

        if not otp_db_obj.verified:
            messages.error(request, "You must confirm your email first.")
            return render(request, template_name='error.html', context={})

        user = User.objects.filter(username=username).first()
        form = AuthenticationForm

        if not user:
            return redirect('/')

        hear_about_us               = request.POST.get("hear_about_us")
        backlogs                    = request.POST.get('backlogs')
        area_of_study               = request.POST.get('area_of_study')
        undergrad_uni               = request.POST.get('undergrad_uni')
        has_taken_gre               = request.POST.get('has_taken_gre')
        gre_verbal                  = request.POST.get('gre_verbal')
        gre_quant                   = request.POST.get('gre_quant')
        gre_awa                     = request.POST.get('gre_awa')
        mcat_chemical_physical      = request.POST.get('mcat_chemical_physical')
        mcat_critical_analysis      = request.POST.get('mcat_critical_analysis')
        mcat_biologic_biochemical   = request.POST.get('mcat_biologic_biochemical')
        mcat_psycho_social_biological = request.POST.get('mcat_psycho_social_biological')
        gmat                        = request.POST.get('gmat')
        lsat                        = request.POST.get('lsat')
        has_taken_toefl             = request.POST.get('has_taken_toefl')
        toefl_reading               = request.POST.get('toefl_reading')
        toefl_speaking              = request.POST.get('toefl_speaking')
        toefl_listening             = request.POST.get('toefl_listening')
        toefl_writing               = request.POST.get('toefl_writing')
        ielts_reading               = request.POST.get('ielts_reading')
        ielts_speaking              = request.POST.get('ielts_speaking')
        ielts_listening             = request.POST.get('ielts_listening')
        ielts_writing               = request.POST.get('ielts_writing')
        cgpa                        = request.POST.get('cgpa')
        cgpa_out_of                 = request.POST.get('cgpa_out_of')
        major                      = request.POST.get('major')
        work_ex_months              = request.POST.get('work_ex_months')
        research_papers             = request.POST.get('research_papers')
        int_term                    = request.POST.get('int_term')
        int_year                    = request.POST.get('int_year')
        target_university           = request.POST.get('target_university')
        target_major                = request.POST.get('target_major')

        context = dict()
        context['form'] = form
        context['majors'] = list(Major.objects.all().values_list('name', flat=True))
        context['hear_about_us'] = hear_about_us
        context['username'] = username
        context['areas_of_study'] = grad_streams_list

        context['backlogs'] = backlogs
        context['area_of_study'] = area_of_study
        context['undergrad_uni'] = undergrad_uni
        context['has_taken_gre'] = has_taken_gre
        context['gre_verbal'] = gre_verbal
        context['gre_quant'] = gre_quant
        context['gre_awa'] = gre_awa
        context['mcat_chemical_physical'] = mcat_chemical_physical
        context['mcat_critical_analysis'] = mcat_critical_analysis
        context['mcat_biologic_biochemical'] = mcat_biologic_biochemical
        context['mcat_psycho_social_biological'] = mcat_psycho_social_biological
        context['gmat'] = gmat
        context['lsat'] = lsat
        context['has_taken_toefl'] = has_taken_toefl
        context['toefl_reading'] = toefl_reading
        context['toefl_speaking'] = toefl_speaking
        context['toefl_listening'] = toefl_listening
        context['toefl_writing'] = toefl_writing
        context['ielts_reading'] = ielts_reading
        context['ielts_speaking'] = ielts_speaking
        context['ielts_listening'] = ielts_listening
        context['ielts_writing'] = ielts_writing
        context['cgpa'] = cgpa
        context['cgpa_out_of'] = cgpa_out_of
        context['major'] = major
        context['work_ex_months'] = work_ex_months
        context['research_papers'] = research_papers
        context['int_term'] = int_term
        context['int_year'] = int_year
        context['target_university'] = target_university
        context['target_major'] = target_major

        # for ios mac
        context['universities'] = list(University.objects.filter(country__name__in=countries).order_by('name').values_list('name', flat=True))
        context['ug_universities'] = list(UndergradUniversity.objects.all().order_by('name').values_list('name', flat=True))

        if gre_awa == "":
            gre_awa = None
            gre_quant = None
            gre_verbal = None

        if gmat == "":
            gmat = None

        if lsat == "":
            lsat = None

        if mcat_psycho_social_biological == '':
            mcat_psycho_social_biological = None
            mcat_biologic_biochemical = None
            mcat_critical_analysis = None
            mcat_chemical_physical = None

        if toefl_writing == '':
            toefl_listening = None
            toefl_reading = None
            toefl_speaking = None
            toefl_writing = None

        if ielts_reading == '':
            ielts_reading = None
            ielts_speaking = None
            ielts_writing = None
            ielts_listening = None

        if area_of_study not in grad_streams_list:
            messages.error(request, "Area of Study is not correct.")
            return redirect('/account/' + username + '/complete-registration/')

        if not UndergradUniversity.objects.filter(name=undergrad_uni).exists():
            messages.error(request, "Undergrad University Name is not correct. Please select one of the options.")
            return redirect('/account/' + username + '/complete-registration/')

        undergrad_uni = UndergradUniversity.objects.filter(name=undergrad_uni).first()

        if not University.objects.filter(name=target_university).exists():
            messages.error(request, "Target University Name is not correct. Please select one of the options.")
            return redirect('/account/' + username + '/complete-registration/')

        target_university = University.objects.filter(name=target_university).first()

        if not Major.objects.filter(name=major).exists():
            messages.error(request, "Major name is not correct. Please select one of the options.")
            return redirect('/account/' + username + '/complete-registration/')
        if not Major.objects.filter(name=target_major).exists():
            messages.error(request, "Major name is not correct. Please select one of the options.")
            return redirect('/account/' + username + '/complete-registration/')

        major = Major.objects.filter(name=major).first()
        target_major = Major.objects.filter(name=target_major).first()

        if 'resume' in request.FILES:
            resume = request.FILES['resume']
            if resume.size > 4194304:
                messages.error(request,
                               "Resume Size Too Big. Please upload a resume with size less than 4MB.")
                return redirect('/account/' + username + '/complete-registration/')

        if float(cgpa) > float(cgpa_out_of):
            messages.error(request,
                           "Your CGPA cannot be greater than Maximum CGPA.")
            return redirect('/account/' + username + '/complete-registration/')

        grad = GradProfile(
            user=user,
            backlogs=backlogs,
            area_of_study=area_of_study,
            undergrad_uni=undergrad_uni,
            cgpa=cgpa,
            cgpa_out_of=cgpa_out_of,
            major=major,
            target_major=target_major,
            work_ex_months=work_ex_months,
            research_papers=research_papers,
            int_term=int_term,
            int_year=int_year,
            target_university=target_university,

        )

        if area_of_study == "Engineering" or area_of_study == "Business":
            if has_taken_toefl == "true":
                has_taken_toefl = True
                total = int(toefl_writing) + int(toefl_speaking) + int(toefl_reading) + int(toefl_listening)
                toefl = TOEFLScore.objects.create(listening=toefl_listening, reading=toefl_reading,
                                                  speaking=toefl_speaking, writing=toefl_writing, total=total,
                                                )
                grad.toefl = toefl
            else:
                has_taken_toefl = False
                ielts = IELTSScore.objects.create(listening=ielts_listening, writing=ielts_writing,
                                                  speaking=ielts_speaking, reading=ielts_reading
                                                )
                grad.ielts = ielts

        if area_of_study == "Engineering":
            gre = GREScore.objects.create(verbal=gre_verbal, quant=gre_quant, awa=gre_awa)
            grad.gre = gre
        elif area_of_study == "Medicine":
            mcat_total = int(mcat_chemical_physical) + int(mcat_critical_analysis) + int(mcat_biologic_biochemical) + int(mcat_psycho_social_biological)
            mcat = MCATScore.objects.create(chemical_physical=mcat_chemical_physical,
                                            critical_analysis=mcat_critical_analysis,
                                            biologic_biochemical=mcat_biologic_biochemical,
                                            psycho_social_biological=mcat_psycho_social_biological,
                                            total=mcat_total
                                            )
            grad.mcat = mcat
        elif area_of_study == "Business":
            if has_taken_gre == "true":
                has_taken_gre = True
                gre = GREScore.objects.create(verbal=gre_verbal, quant=gre_quant, awa=gre_awa)
                grad.gre = gre
            else:
                has_taken_gre = False
                grad.gmat = gmat
        elif area_of_study == "Law":
            grad.lsat = lsat

        if 'resume' in request.FILES:
            resume = request.FILES['resume']
            grad.resume = resume

        grad.has_taken_toefl = has_taken_toefl
        grad.has_taken_gre = has_taken_gre
        grad.save()

        student = Student.objects.filter(user=user)
        student.update(
            complete_profile=True
        )

        user.is_active = True
        user.save()

        email_message = "Dear " + user.first_name + " " + user.last_name + ",<br/><br/>" + \
                        "At YMGrad, we want to be your helping hand starting from day 1 of your study abroad application process. This email begins that relationship. Here, we give you all the relevant material for the GRE for free.<br><br>"\
                        "Please use the link to get your GRE Material.<br><center><button class='btn btn-success'><a href='https://drive.google.com/open?id=1HQ8IXi11jfXOUYLLQ1m7xw22qs5Ur9Uk'>GRE Material</a></button></center>"\
                        "<br><br>In case you would like to access the recommended Premium Material, get the latest material for GRE/TOEFL from here: <br><center><a href='https://www.ymgrad.com/study_material/'><button class='btn btn-success' style='background: green; border-radius:100px; color: white !important; padding: 5px;'>Premium GRE Material</button></a></center><br>"\
                        "<br>Still, by any chance if you feel you have hit a plateau and are unable to improve your performance on the GRE, I would recommend getting one-on-one help directly from me. To do that, please book a <a href='https://www.ymgrad.com/service/premium/gre-consulation/'>GRE Consultation</a>.<br><br>"\
                        "Finally, if you need one-on-one help in regard to your <b>SOPs and LORs</b>, please stay away from consultancies and read the following.<br><br>"\
                        "Last year, we sent applicants to unviersities like <b>UIUC, UCLA, ASU, Cornell, UC, and more</b>. These results are shown on my Instagram highlights. To check them out, <a href='https://www.instagram.com/s/aGlnaGxpZ2h0OjE4MDAyNDc4Njc5MjI0OTEy?igshid=1lfqi8jbq8bg4'>click here</a>.<br><br>" \
                        "Now, I wish to do the same for you. SOPs and LORs are a huge part of your application. Book your services in advance before the prices increase.<br><br>"\
                        "To book your SOP/LOR drafting service now, <a href='https://www.ymgrad.com/service/'>click here</a>.<br><br>"\
                        "Please note that we only work with a limited number of applicants. If you cannot see the button to make payment, it means we would be unable to work with your profile.<br><br>"\
                        "Make the best of the only time you are going to be applying to universities. Most people only go through this process once in their lifetime. If done right, your dream university awaits you. If you have gained value from my content on YouTube, you know I am the best person to help you with your applications.<br><br>"\
                        "I look forward to getting you into your dream university.<br><br>"\
                        "Best,<br>" + "The YMGrad Team"
        # enable_otp = 1

        email_message2 = "Dear " + user.first_name + ", <br><br>Unfortunately, <b>almost</b> all of the following accounts are sold out, so they had to be removed from YMGrad Study Material page. <br><br><b>- Kaplan GRE 5 Online Tests + QBank<br>- Kaplan 20 Practice Sets (Windows Software)<br>- ManhattanPrep TOEFL Online Access</b><br><br>If you still need one of these accounts, here's how you can get them:<br><br><ol><li>Kaplan GRE 5 Online Tests + QBank:   <a href='https://rzp.io/l/qvFGkHM'>Buy Now (INR)</a>    |   <a href='https://rzp.io/l/WT4QhHB'>Buy Now (USD)</a></li><li>Kaplan 20 Practice Sets (Windows Software):  <a href='https://rzp.io/l/KrZVGeR'>Buy Now (INR)</a>   |  <a href='https://rzp.io/l/0jqem0d'>Buy Now (USD)</a></li><li>ManhattanPrep TOEFL Online Access:    <a href='https://rzp.io/l/mXJOC57'>Buy Now (INR)</a>     |   <a href='https://rzp.io/l/snyNPbN'>Buy Now (USD)</a></li></ol><br><br><b>Please Note: </b>An EXTREMELY Limited number of these accounts are left. These will go back up on YMGrad once we restock. It may take a while. Using these links will make sure that you get an account because they will only work until we have an account available for you.<br><br>We apologize for the inconvenience.<br><br>Regards,<br>Team YMGrad"

        if enable_otp:
            send_email.delay(receiver=user.email, email_message=email_message, subject="YMGrad - Your Study Material and More!")
            # send_email.delay(receiver=user.email, email_message=email_message2, subject="Sold Out: Kaplan GRE Tests Account, Manhattan TOEFL Online Account")
        else:
            print("Not sending email because in development mode.")

        return render(request, template_name="dashboard.html", context=context)


class PopulateFlagDB(APIView):

    def post(self, request):

        queryset = Country.objects.all()

        for obj in queryset:
            obj.flag_filename = "flag-of-" + obj.name + ".jpg"
            obj.save()

        return JsonResponse({"success": "True"})


class GetStatesAndCC(APIView):
    def post(self, request, *args, **kwargs):
        try:
            country = self.request.POST.get('country')
            country_id = Country.objects.filter(name=country).first().id
            states = State.objects.filter(country_id=country_id).order_by('name').values()
            cc = Country.objects.filter(name=country).first().phone_code
            length = len(states)

            return JsonResponse({'states': list(states), 'cc': cc, 'length': length})
        except Exception as e:
            return JsonResponse({'error': str(e)})


class CheckUsername(APIView):
    def post(self, request, *args, **kwargs):
        try:
            username = self.request.POST.get('username')
            taken = User.objects.filter(username=username).first()

            if taken:
                taken = True
            else:
                taken = False

            return JsonResponse({'taken': taken})
        except Exception as e:
            return JsonResponse({'error': e})


class EmailSent(View):

    def get(self, request):

        return render(request, template_name='account/email_sent.html', context={})


class VerifyMobile(APIView):
    def post(self, request, *args, **kwargs):
        username          = request.POST.get('username')
        mobile          = request.POST.get('mobile')
        user              = User.objects.filter(username=username).first()

        if not user:
            return JsonResponse({"success": False})

        otp_from_frontend = request.POST.get('otp')
        otp_db_obj        = OtpDB.objects.filter(user=user).first()
        otp_from_backend  = otp_db_obj.mobile_otp

        if otp_from_backend == otp_from_frontend:
            otp_db_obj.confirm_mobile = True
            otp_db_obj.save()

            state = State.objects.filter(name='Delhi').first()
            country = Country.objects.filter(name='India').first()

            investor = Student.objects.create(
                user=user,
                address='',
                state=state,
                country=country,
                mobile=mobile,
                how_did_you_hear_about_us='',
            )
            investor.save()

            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False})


class SendOTP(APIView):
    def post(self, request, *args, **kwargs):
        username          = request.POST.get('username')
        country          = request.POST.get('country')
        mobile          = request.POST.get('mobile')
        user              = User.objects.filter(username=username).first()
        otp_db_obj = OtpDB.objects.filter(user=user).first()
        country = Country.objects.filter(name=country).first()
        cc = country.phone_code

        if not country:
            messages.error(request, "Invalid Country")
            return JsonResponse({"success": False})

        if not user:
            return JsonResponse({"success": False})

        mobile_otp = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(5))
        otp_db_obj.mobile_otp = mobile_otp
        otp_db_obj.save()
        msg = "Welcome to YashMittra.com. Use the following OTP to finish registration: " + mobile_otp
        if enable_otp:
            res = send_sms(msg=msg, mobile_number=mobile, country_code=cc)
        else:
            print(mobile_otp)
            return JsonResponse({"success": True})

        if res:
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False})


class Dashboard(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        user = request.user
        decision = Decisions.objects.filter(user=user).order_by('decision_type')
        services = ServiceUser.objects.filter(user=user).order_by('-pending')
        articles = Article.objects.filter(author=user).order_by('-timestamp')
        today = datetime.now()
        referrals = Referral.objects.filter(referred_by=user, timestamp__month=today.month, confirm=True).order_by('-timestamp')
        context = dict()
        context['decision'] = decision
        context['services'] = services
        context['referrals'] = referrals
        context['no_of_referrals'] = referrals.count()

        if user.student.publisher:
            context['articles'] = articles

        return render(request, template_name='dashboard.html', context=context)


class EditProfile(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        pk = self.request.user.pk
        user = User.objects.filter(id=pk).first()
        student = Student.objects.filter(user_id=pk).first()
        grad = GradProfile.objects.filter(user_id=pk).first()

        context = dict()
        if student.dob:
            context['dob'] = datetime.strftime(student.dob, '%Y-%m-%d')

        context['majors'] = list(Major.objects.all().values_list('name', flat=True).order_by('name'))
        context['resume'] = str(grad.resume).replace('resume/', '')
        if student.dob:
            context['dob'] = datetime.strftime(student.dob, '%Y-%m-%d')

        return render(request, 'profile/edit_profile.html', context=context)

    def post(self, request, *args, **kwargs):
        user = request.user
        student = Student.objects.filter(user=user).first()
        grad = GradProfile.objects.filter(user=user).first()
        context = dict()

        try:

            ###### Security Checks ######
            cgpa = request.POST.get('cgpa')
            cgpa_out_of = request.POST.get('cgpa_out_of')
            target_major = request.POST.get('target_major')
            target_university = request.POST.get('target_university')

            if 'resume' in request.FILES:
                resume = request.FILES['resume']
                if resume.size > 4194304:
                    messages.error(request,
                                   "Resume Size Too Big. Please upload a resume with size less than 4MB.")
                    return redirect('/account/edit_profile/')

            if float(cgpa) > float(cgpa_out_of):
                messages.error(request,
                               "Your CGPA cannot be greater than Maximum CGPA.")
                return redirect('/account/edit_profile/')

            if not Major.objects.filter(name=target_major).exists():
                messages.error(request, "Major name is not correct. Please select one of the options.")
                return redirect('/account/edit_profile/')

            if not University.objects.filter(name=target_university).exists():
                messages.error(request, "Target University Name is not correct. Please select one of the options.")
                return redirect('/account/edit_profile/')


            ###### SECURITY CHECKS END ######



            ####### Edit AUTH_USER DB ########
            first_name = request.POST.get('first_name').title()
            last_name = request.POST.get('last_name').title()

            user.first_name = first_name
            user.last_name = last_name
            user.save()
            ####### Edit AUTH_USER DB END ########

            ####### Edit ACCOUNT_STUDENT DB ########

            mobile = request.POST.get('mobile')
            dob = request.POST.get('dob')
            about = request.POST.get('about')
            website = request.POST.get('website')

            student.about = about
            student.website = website

            student.mobile = mobile

            if dob:
                student.dob = datetime.strptime(dob, '%Y-%m-%d')

            student.save()

            if student.dob:
                context['dob'] = datetime.strftime(student.dob, '%Y-%m-%d')

            ####### Edit ACCOUNT_STUDENT DB  END ########

            ####### Edit ACCOUNT_GRADPROFILE DB ########

            if grad.area_of_study == 'Business' and not grad.has_taken_gre:
                gmat = request.POST.get('gmat')
                grad.gmat = gmat
            elif grad.area_of_study == 'Business' and grad.has_taken_gre:
                gre_quant = request.POST.get('gre_quant')
                gre_verbal = request.POST.get('gre_verbal')
                gre_awa = request.POST.get('gre_awa')

                gre = grad.gre
                gre.quant = gre_quant
                gre.verbal = gre_verbal
                gre.awa = gre_awa
                gre.save()
            elif grad.area_of_study == 'Engineering':
                gre_quant = request.POST.get('gre_quant')
                gre_verbal = request.POST.get('gre_verbal')
                gre_awa = request.POST.get('gre_awa')

                gre = grad.gre
                gre.quant = gre_quant
                gre.verbal = gre_verbal
                gre.awa = gre_awa
                gre.save()
            elif grad.area_of_study == 'Law':
                lsat = request.POST.get('lsat')
                grad.lsat = lsat
            elif grad.area_of_study == 'Medicine':
                mcat_chemical_physical = request.POST.get('mcat_chemical_physical')
                mcat_critical_analysis = request.POST.get('mcat_critical_analysis')
                mcat_biologic_biochemical = request.POST.get('mcat_biologic_biochemical')
                mcat_psycho_social_biological = request.POST.get('mcat_psycho_social_biological')

                mcat = grad.mcat
                mcat.chemical_physical = mcat_chemical_physical
                mcat.critical_analysis = mcat_critical_analysis
                mcat.biologic_biochemical = mcat_biologic_biochemical
                mcat.psycho_social_biological = mcat_psycho_social_biological
                mcat.total = mcat_psycho_social_biological + mcat_biologic_biochemical + mcat_critical_analysis + mcat_chemical_physical
                mcat.save()

            if grad.area_of_study == 'Business' or grad.area_of_study == 'Engineering':
                if grad.has_taken_toefl:
                    toefl = grad.toefl
                    toefl_reading = request.POST.get('toefl_reading')
                    toefl_speaking = request.POST.get('toefl_speaking')
                    toefl_listening = request.POST.get('toefl_listening')
                    toefl_writing = request.POST.get('toefl_writing')

                    toefl.reading = toefl_reading
                    toefl.writing = toefl_writing
                    toefl.speaking = toefl_speaking
                    toefl.listening = toefl_listening
                    toefl.total = toefl_listening + toefl_speaking + toefl_writing + toefl_reading
                    toefl.save()
                else:
                    ielts = grad.ielts
                    ielts_reading = request.POST.get('ielts_reading')
                    ielts_speaking = request.POST.get('ielts_speaking')
                    ielts_listening = request.POST.get('ielts_listening')
                    ielts_writing = request.POST.get('ielts_writing')

                    ielts.reading = ielts_reading
                    ielts.speaking = ielts_speaking
                    ielts.writing = ielts_writing
                    ielts.listening = ielts_listening
                    ielts.save()

            if 'resume' in request.FILES:
                resume = request.FILES['resume']
                grad.resume = resume
                if resume.size > 4194304:
                    messages.error(request,
                                   "Resume Size Too Big. Please upload a resume with size less than 4MB.")
                    return redirect('/account/edit_profile/')

            cgpa = request.POST.get('cgpa')
            cgpa_out_of = request.POST.get('cgpa_out_of')
            work_ex_months              = request.POST.get('work_ex_months')
            research_papers             = request.POST.get('research_papers')
            int_term                    = request.POST.get('int_term')
            int_year                    = request.POST.get('int_year')
            backlogs                    = request.POST.get('backlogs')

            target_major = Major.objects.filter(name=target_major).first()
            target_university = University.objects.filter(name=target_university).first()

            grad.cgpa = cgpa
            grad.cgpa_out_of = cgpa_out_of
            grad.work_ex_months = work_ex_months
            grad.research_papers = research_papers
            grad.int_term = int_term
            grad.int_year = int_year
            grad.backlogs = backlogs
            grad.target_major = target_major
            grad.target_university = target_university

            grad.save()

            context=dict()
            context['majors'] = list(Major.objects.all().values_list('name', flat=True).order_by('name'))
            if student.dob:
                context['dob'] = datetime.strftime(student.dob, '%Y-%m-%d')
            context['resume'] = str(grad.resume).replace('resume/', '')

            messages.success(request, "Successfully updated account details.")
        except Exception as e:
            print(e)
            context = dict()
            context['majors'] = list(Major.objects.all().values_list('name', flat=True).order_by('name'))
            if student.dob:
                context['dob'] = datetime.strftime(student.dob, '%Y-%m-%d')
            messages.error(request, "An error occured at our end. Please let us know if you think it is our mistake.")
            context['majors'] = list(Major.objects.all().values_list('name', flat=True).order_by('name'))
            context['resume'] = str(grad.resume).replace('resume/', '')

        return render(request, 'profile/edit_profile.html', context=context)


class EditProfilePicture(LoginRequiredMixin, View):


    def post(self, request, *args, **kwargs):
        student = request.user.student
        ############ Change Profile Picture #############################3
        if 'profile_picture' in request.FILES:
            image = request.FILES['profile_picture']
            width, height = get_image_dimensions(image)
            hor_len = width / height

            if hor_len > 1.5:
                print("Rejecting too long image.")
                messages.error(request,
                               "Image too long horizontally and too short vertically. Approximately square image needed.")
                return redirect('/account/edit_profile/')
            if hor_len < 0.5:
                print("Rejecting too long image.")
                messages.error(request,
                               "Image too short horizontally and too long vertically. Approximately square image needed.")
                return redirect('/account/edit_profile/')

            if image.size > 4194304:
                messages.error(request,
                               "Image Size Too Big. Please upload a profile picture with an image size less than 4MB.")
                return redirect('/account/edit_profile/')



            img = Img.open(BytesIO(image.read()))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            new_width = 800
            img.thumbnail((new_width, new_width * height / width), Img.ANTIALIAS)
            # img.thumbnail((self.path.width / 1.5, self.path.height / 1.5), Img.ANTIALIAS)
            output = BytesIO()
            img.save(output, format='JPEG', quality=70)

            output.seek(0)
            image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % image.name.split('.')[0],
                                             'image/jpeg', sys.getsizeof(output), None)

            student.path = image
            student.save()

        ########## Change Profile Picture End #######################
        context = dict()
        context['majors'] = list(Major.objects.all().values_list('name', flat=True).order_by('name'))
        if student.dob:
            context['dob'] = datetime.strftime(student.dob, '%Y-%m-%d')
        return render(request, 'profile/edit_profile.html', context=context)


class DecisionView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = dict()
        user = request.user
        context['majors'] = list(Major.objects.all().values_list('name', flat=True).order_by('name'))
        context['admits'] = Decisions.objects.filter(user=user, decision_type='admit')
        context['applied'] = Decisions.objects.filter(user=user, decision_type='applied')
        context['rejects'] = Decisions.objects.filter(user=user, decision_type='reject')
        context['universities'] = University.objects.filter(country__name__in=countries).order_by('name')
        if Decisions.objects.filter(user=user, final=True).exists():
            context['finalized'] = True
        else:
            context['finalized'] = False
        return render(request, template_name='account/decisions.html', context=context)


class AddDecision(APIView):
    def post(self, request, *args, **kwargs):

        operation = request.POST.get('operation').lower()
        uni_name = request.POST.get('uni_name')
        major = request.POST.get('major')
        user_id = request.POST.get('user_id')
        application_date = request.POST.get('application_date')
        decision_date = request.POST.get('decision_date')

        if not User.objects.filter(id=user_id).exists():
            return JsonResponse({"success": True,
                                 "msg": "User not logged in.",
                                 'color': 'red'})

        user = User.objects.filter(id=user_id).first()

        # Fix date format - parse in datetime
        application_date = datetime.strptime(application_date, '%Y-%m-%d')
        if decision_date:
            decision_date = datetime.strptime(decision_date, '%Y-%m-%d')
            if application_date > decision_date:
                return JsonResponse({"success": True,
                                     "msg": "Failed to add university. Application Date cannot be later than decision date.",
                                     'color': 'red'})

        if University.objects.filter(name=uni_name).exists() or not Major.objects.filter(name=major).exists():
            university = University.objects.filter(name=uni_name).first()
            major = Major.objects.filter(name=major).first()
        else:
            return JsonResponse({"success": True, "msg": "Failed to add university. Please select the University and Major from the options", 'color': 'red'})

        if operation == 'applied':
            if Decisions.objects.filter(user=user, major=major, university=university, decision_type='applied').exists():
                return JsonResponse({"success": True, "msg": "You have already applied to this university.", "color": "red"})
            elif Decisions.objects.filter(user=user, major=major, university=university, decision_type='admit').exists():
                return JsonResponse({"success": True, "msg": "University already present in admits/rejects.", "color": "red"})
            elif Decisions.objects.filter(user=user, major=major, university=university, decision_type='reject').exists():
                return JsonResponse({"success": True, "msg": "University already present in admits/rejects.", "color": "red"})
            else:
                d = Decisions.objects.create(
                    user=user,
                    major=major,
                    university=university,
                    decision_type='applied',
                    application_date=application_date,
                    final=False,
                )
                return JsonResponse({"success": True, "msg": "Successfully Added University.", 'color': 'green', 'decision_id': d.id})

        elif operation == "admit":
            if Decisions.objects.filter(user=user, major=major, university=university, decision_type='admit').exists():
                return JsonResponse({"success": True, "msg": "You already have an admit from this university.", "color": "red"})
            elif Decisions.objects.filter(user=user, major=major, university=university, decision_type='applied').exists():
                return JsonResponse({"success": True, "msg": "You already have this university in applied. Please edit it instead.", "color": "red"})
            elif Decisions.objects.filter(user=user, major=major, university=university, decision_type='reject').exists():
                return JsonResponse({"success": True, "msg": "University already present in rejects. Please edit it instead.", "color": "red"})
            else:
                d = Decisions.objects.create(
                    user=user,
                    major=major,
                    university=university,
                    decision_type='admit',
                    application_date=application_date,
                    decision_date=decision_date,
                    final=False,

                )
                return JsonResponse({"success": True, "msg": "Successfully Added University.", 'color': 'green', 'decision_id': d.id})
        elif operation == "reject":
            if Decisions.objects.filter(user=user, major=major, university=university, decision_type='reject').exists():
                return JsonResponse({"success": True, "msg": "You already have a reject from this university.", "color": "red"})
            elif Decisions.objects.filter(user=user, major=major, university=university, decision_type='applied').exists():
                return JsonResponse({"success": True, "msg": "You already have this university in applied. Please edit it instead.", "color": "red"})
            elif Decisions.objects.filter(user=user, major=major, university=university, decision_type='admit').exists():
                return JsonResponse({"success": True, "msg": "University already present in admits. Please edit it instead.", "color": "red"})
            else:
                d = Decisions.objects.create(
                    user=user,
                    major=major,
                    university=university,
                    decision_type='reject',
                    application_date=application_date,
                    decision_date=decision_date,
                    final=False,
                )
                return JsonResponse({"success": True, "msg": "Successfully Added University.", 'color': 'green', 'decision_id': d.id})


class EditDecision(APIView):
    def post(self, request, *args, **kwargs):
        operation = request.POST.get('operation').lower()
        decision_id = int(request.POST.get('decision_id'))
        user_id = request.POST.get('user_id')
        decision = Decisions.objects.filter(id=decision_id).first()
        user = User.objects.filter(id=user_id).first()

        if decision.decision_type == 'admit':
            if operation == 'delete':
                decision.delete()
                return JsonResponse({"success": True, "msg": "Deleted Decision Successfully.", 'color': 'green'})
            if operation == 'final':
                if Decisions.objects.filter(user=user, final=True).exists():
                    return JsonResponse({"success": True, "msg": "Cannot Finalize University. You have already finalized one University", "color": "red"})
                decision.final = True
                decision.save()
                return JsonResponse({"success": True, "msg": "Finalized University Successfully.", 'color': 'green'})
            else:
                return JsonResponse({"success": False})

        if decision.decision_type == 'reject':
            if operation == 'delete':
                decision.delete()
                return JsonResponse({"success": True, "msg": "Deleted Decision Successfully.", 'color': 'green'})

        if decision.decision_type == 'applied':
            if operation == 'delete':
                decision.delete()
                return JsonResponse({"success": True, "msg": "Deleted Decision Successfully.", 'color': 'green'})
            if operation == 'admit':
                decision.decision_type = 'admit'
                decision.decision_date = now()
                decision.save()
                return JsonResponse({"success": True, "msg": "Successfully Converted Decision to an Admit", "color": "green"})
            if operation == 'reject':
                decision.decision_type = 'reject'
                decision.decision_date = now()
                decision.save()
                return JsonResponse({"success": True, "msg": "Successfully Converted Decision to a Reject", "color": "green"})
        return JsonResponse({"success": False})


class ProfilePage(View):

    def get(self, request, *args, **kwargs):

        viewer = request.user
        profile_of = kwargs.get('username')

        if not User.objects.filter(username=profile_of).exists():
            messages.error(request, "User not found.")
            return render(request, template_name='error.html', context={})

        profile_of_user = User.objects.filter(username=profile_of).first()

        decision = Decisions.objects.filter(user__username=profile_of).order_by('decision_type')

        if profile_of_user.student.publisher:
            articles = Article.objects.filter(author__username=profile_of).order_by('-timestamp')

        if viewer == User.objects.filter(username=profile_of).first():
            return redirect('/account/dashboard')

        if not User.objects.filter(username=profile_of).exists():
            messages.error(request, "No such user found.")
            return render(request, 'error.html')

        context = dict()
        context['obj'] = User.objects.filter(username=profile_of).first()
        context['decision'] = decision
        if profile_of_user.student.publisher:
            context['articles'] = articles

        return render(request, template_name='profile/user_profile.html', context=context)


class SendBackupToEmail(APIView):

    def post(self, request):

        send_backup_with_email.delay()

        return JsonResponse({"success": True})
