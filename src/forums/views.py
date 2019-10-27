from django.shortcuts import render
import logging
from django.db.models import Q, F
from datetime import datetime, timedelta, timezone, date
from rest_framework.views import APIView
import re
from rest_framework.response import Response
from rest_framework import status
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.utils.timezone import now
from django.contrib import messages
from ipware import get_client_ip
from django.core.paginator import Paginator
import random, string
from django.http import JsonResponse
from django.template.loader import render_to_string
from inv.utils import send_sms
from django.core.files.images import get_image_dimensions
from account.tasks import send_email
from inv.utils import send_email as s_e
from django.contrib.auth import get_user_model
from inv.settings import enable_otp
from university.models import grad_streams_list, University
from inv.views import countries
from .models import Question, Answer, Views
from django.template.defaultfilters import slugify
from dateutil.relativedelta import relativedelta
import sys
from PIL import Image as Img
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

User = get_user_model()


forum_topics = [
    'GRE Preparation',
    'GMAT Preparation',
    'MCAT Preparation',
    'LSAT Preparation',
    'TOEFL Preparation',
    'IELTS Preparation',
    'Mock Tests',
    'SOP Issues',
    'LOR Issues',
    'Application Help',
    'Profile Evaluation',
    'Visa Interview',
    'Roommates Search',
    'Housing Queries',
    'Flight Booking',
]


class ForumView(View):
    def get(self, request, *args, **kwargs):

        # question = request.POST.get('question')
        details = request.POST.get('details')
        topic = request.POST.get('topic')
        context = dict()
        context['forum_topics'] = forum_topics
        context['details'] = details
        context['topic'] = topic

        # universities = University.objects.filter(country=country).order_by('rank')
        question = Question.objects.all().order_by('-id')

        paginator = Paginator(question, 25)

        page_num = request.GET.get('page')
        result = paginator.get_page(page_num)
        try:
            page = paginator.page(page_num)
        except:
            page = paginator.page(1)

        count = paginator.num_pages

        context['question'] = question
        context['page'] = page
        context['page_count'] = count
        context['result'] = result

        # context['questions'] = Question.objects.all().order_by('-id')

        return render(request, 'forums/forums.html', context=context)

    # def post(self, request, *args, **kwargs):
    #
    #     user = request.user
    #     student = user.student
    #     question = request.POST.get('question')
    #     details = request.POST.get('details')
    #     topic = request.POST.get('topic')
    #
    #     context = dict()
    #     context['forum_topics'] = forum_topics
    #     context['question'] = question
    #     context['details'] = details
    #     context['topic'] = topic
    #
    #     context['questions'] = Question.objects.all().order_by('-id')[:25]
    #
    #     if topic not in forum_topics:
    #         messages.error(request, "No such topic exists.")
    #         return render(request, template_name='error.html', context=context)
    #
    #     if Question.objects.filter(question=question).exists():
    #         print("Duplicate")
    #         prev_q = Question.objects.filter(question=question).first()
    #         link = "/forums/" + topic + "/" + prev_q.ques_link + "/"
    #         messages.warning(request, "<a href='" + link + "'>This question</a> has already been asked. We do not allow duplicate questions.")
    #     else:
    #         student.no_of_questions_asked = student.no_of_questions_asked + 1
    #         student.save()
    #
    #         slug_candidate = question[:72]
    #         x = slug_candidate.split()
    #         x = x[:10]
    #         ques_link = '-'.join(x).lower()
    #         ques_link = slugify(ques_link)
    #
    #         q = Question.objects.create(user=user, question=question, details=details, topic=topic, ques_link=ques_link)
    #         q.followers.add(user)
    #
    #         if enable_otp:
    #             msg = "Hi " + user.first_name + ",<br><br>Your question has been posted successfully.<br><br><b>Category: </b>" + topic + "<br><br>Please note! We expect the community to help all of its members. Make sure you answer questions others post in order to get your question answered sooner.<br><br>Find your question here: https://www.ymgrad.com/forums/" + topic + "/" + str(
    #                 q.ques_link) + "/<br><br>Best,<br>The YMGrad Team"
    #             send_email.delay(receiver=user.email, email_message=msg, subject="Your Question has been posted on YMGrad.")
    #         else:
    #             print("Not sending email because in development mode.")
    #
    #         messages.success(request, "Your question has been posted!")
    #         user.save()
    #         q.save()
    #
    #     return render(request, template_name='forums/forums.html', context=context)


class AskQuestion(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        template_name = "forums/ask-question.html"
        context = dict()
        context['forum_topics'] = forum_topics

        return render(request, template_name=template_name, context=context)

    def post(self, request, *args, **kwargs):

        template_name = "forums/question-submitted.html"
        user = request.user
        student = user.student
        question = request.POST.get('question')
        details = request.POST.get('details')
        topic = request.POST.get('topic')

        context = dict()
        context['forum_topics'] = forum_topics
        context['question'] = question
        context['details'] = details
        context['topic'] = topic
        context['questions'] = Question.objects.all().order_by('-id')[:25]

        if topic not in forum_topics:
            messages.error(request, "No such topic exists.")
            return render(request, template_name='error.html', context=context)

        if 'manhattan' in question.lower() or 'magoosh' in question.lower() or '@' in question or 'manhattan' in details.lower() or 'magoosh' in details.lower() or '@' in details:
            messages.error(request, "Please do not ask for material in the forums. Your account will be suspended and you will not be able to make any purchases on the study material page. Please consider purchasing access to the material. You will have instant access and our support in case you need help with the access.")
            return redirect('/study_material/')

        if Question.objects.filter(question__iexact=question).exists():
            print("Duplicate")
            prev_q = Question.objects.filter(question=question).first()
            link = "/forums/question/" + prev_q.ques_link + "/"
            messages.warning(request, "<a href='" + link + "'>This question</a> has already been asked. We do not allow duplicate questions.")
            return redirect('/forums/ask-question/')
        else:
            student.no_of_questions_asked = student.no_of_questions_asked + 1
            student.save()

            slug_candidate = question[:72]
            x = slug_candidate.split()
            x = x[:10]
            ques_link = '-'.join(x).lower()
            ques_link = slugify(ques_link)

            q = Question.objects.create(user=user, question=question, details=details, topic=topic, ques_link=ques_link)
            q.followers.add(user)

            if 'imgInp' in request.FILES:
                image = request.FILES['imgInp']
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

                q.path = image

            if enable_otp:
                msg = "Hi " + user.first_name + ",<br><br>Your question has been posted successfully.<br><br><b>Category: </b>" + topic + "<br><br>Please note! We expect the community to help all of its members. Make sure you answer questions others post in order to get your question answered sooner.<br><br>Find your question here: https://www.ymgrad.com/forums/question/" + str(
                    q.ques_link) + "/<br><br>Best,<br>The YMGrad Team"
                send_email.delay(receiver=user.email, email_message=msg, subject="Your Question has been posted on YMGrad.")
            else:
                print("Not sending email because in development mode.")

            messages.success(request, "Your question has been posted!")
            user.save()
            q.save()

        context = {}

        return render(request, template_name=template_name, context=context)


class ViewQuestion(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        ques_link = kwargs.get('ques_link')

        if not Question.objects.filter(ques_link__iexact=ques_link).exists():
            messages.error(request, "Question not found!")

        q = Question.objects.filter(ques_link__iexact=ques_link).first()

        # Add View...
        if not user.is_anonymous:  # track by user
            if Views.objects.filter(user=user, q=q).exists():
                test = Views.objects.filter(user=user, q=q).first()
                t = test.latest_view_time
                t_plus_15 = t + relativedelta(minutes=15)
                if now() < t_plus_15:
                    print("Caught, within 15 min. window, no update")
                else:
                    Views.objects.filter(user=user, q=q).update(latest_view_time=now())
                    q.views = q.views + 1
                    print("Exist, but update, add view")
            else:
                Views.objects.create(user=user, q=q)
                q.views = q.views + 1
                print("NOO, add view")
        else:  # track by ip address
            ip, is_routable = get_client_ip(request)
            if ip is None:
                pass
            else:
                if Views.objects.filter(q=q, is_anonymous=True, ip_address=ip).exists():
                    test = Views.objects.filter(q=q, is_anonymous=True, ip_address=ip).first()
                    t = test.latest_view_time
                    t_plus_15 = t + relativedelta(minutes=15)
                    if now() < t_plus_15:
                        print("Caught, within 15 min. window, no update")
                    else:
                        Views.objects.filter(q=q, is_anonymous=True, ip_address=ip).update(latest_view_time=now())
                        q.views = q.views + 1
                        print("Exist, but update, add view")
                else:
                    Views.objects.create(q=q, is_anonymous=True, ip_address=ip)
                    q.views = q.views + 1
                    print("NOO, add view")

        q.save()

        ### END Add View...

        context = dict()
        context['forum_topics'] = forum_topics
        context['question'] = q
        context['answers'] = Answer.objects.filter(question=q).order_by('-upvotes', 'timestamp')

        return render(request, template_name='forums/view-question.html', context=context)

    def post(self, request, *args, **kwargs):  # Save Answer

        user = request.user
        ques_link = kwargs.get('ques_link')
        details = request.POST.get('details')

        if not Question.objects.filter(ques_link__iexact=ques_link).exists():
            messages.error(request, "Question not found!")

        q = Question.objects.filter(ques_link__iexact=ques_link).first()

        context = dict()
        context['forum_topics'] = forum_topics
        context['question'] = q
        context['answers'] = Answer.objects.filter(question=q).order_by('-timestamp')

        if Answer.objects.filter(question=q, details=details).exists():
            messages.error(request, "A similar answer for the question already exists")
            return render(request, template_name='forums/view-question.html', context=context)

        Answer.objects.create(user=user, question=q, details=details)
        q.no_of_ans = q.no_of_ans + 1
        link = 'https://www.ymgrad.com/forums/question/' + q.ques_link
        for follower in q.followers.all():
            email_message = "Dear " + follower.first_name + " " + follower.last_name + ",<br/><br/>" \
                            "There has been a new correspondence for '" + q.question + "' at YMGrad.com<br><br>" \
                            "Check out the answer by clicking on the link below:<br><br>" + \
                            link + "<br/><br/>" \
                            "To maximize chances of gaining admits and selecting the right universities for your " \
                            "profile, please check out YMExplorer.<br><br>" + \
                            "Best,<br>" + "The YMGrad Team"
            if enable_otp:
                send_email.delay(receiver=follower.email, email_message=email_message, subject="New Answer for " + q.question)
            else:
                print("Not sending email because in development mode.")
        q.followers.add(user)
        q.save()

        messages.success(request, "Your answer has been published.")

        return render(request, template_name='forums/view-question.html', context=context)


class DeleteAns(APIView):
    def post(self, request, *args, **kwargs):
        try:
            ans_id = request.POST.get('ans_id')
            username = request.POST.get('user')
            user = User.objects.filter(username=username).first()
            answer = Answer.objects.filter(id=ans_id).first()
            question = answer.question

            data = dict()

            if answer.user == user:
                answer.delete()
                question.no_of_ans = question.no_of_ans - 1
                question.save()
            else:
                data['error'] = "Error Occured."
            return JsonResponse(data)
        except Exception as e:
            data = {}
            logging.error(e)
            print(e)
            return JsonResponse(data)


class EditAns(APIView):

    def post(self, request, *args, **kwargs):
        try:
            ans_id = request.POST.get('ans_id')
            new_answer = request.POST.get('new_answer')
            username = request.POST.get('user')
            user = User.objects.filter(username=username).first()

            answer = Answer.objects.filter(id=ans_id).first()

            if answer.user == user:

                answer.details = new_answer
                answer.timestamp = now()
                answer.save()

                string = str(answer.timestamp)
                d = datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')

                d = d.strftime('%b %d, %Y, %I:%M %p')
                data = dict()
                data['timestamp'] = d
                data['new_answer'] = answer.details
            else:
                data = dict()
                data['error'] = "Error Occured."
        except Exception as e:
            print(e)
            data = {}
            logging.error(e)
            print(e)

        return JsonResponse(data)


class Vote(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        ans_id = request.POST.get('ans_id')
        upvote = request.POST.get('upvote')
        downvote = request.POST.get('downvote')
        type = request.POST.get('req_type')
        ans = Answer.objects.filter(id=ans_id).first()

        if upvote == '1' and type == 'added':
            Answer.objects.filter(id=ans_id).update(upvotes=F('upvotes')+1)
            ans.liked_by.add(User.objects.get(id=user_id))
        elif downvote == '1' and type == 'added':
            Answer.objects.filter(id=ans_id).update(downvotes=F('downvotes')+1)
            ans.disliked_by.add(User.objects.get(id=user_id))
        elif upvote == '1' and type == 'removed':
            Answer.objects.filter(id=ans_id).update(upvotes=F('upvotes')-1)
            ans.liked_by.remove(User.objects.get(id=user_id))
        elif downvote == '1' and type == 'removed':
            Answer.objects.filter(id=ans_id).update(downvotes=F('downvotes')-1)
            ans.disliked_by.remove(User.objects.get(id=user_id))
        elif upvote == '2':
            Answer.objects.filter(id=ans_id).update(downvotes=F('downvotes') - 1, upvotes=F('upvotes')+1)
            ans.liked_by.add(User.objects.get(id=user_id))
            ans.disliked_by.remove(User.objects.get(id=user_id))
        elif downvote == '2':
            Answer.objects.filter(id=ans_id).update(downvotes=F('downvotes') + 1, upvotes=F('upvotes')-1)
            ans.liked_by.remove(User.objects.get(id=user_id))
            ans.disliked_by.add(User.objects.get(id=user_id))

        ans = Answer.objects.filter(id=ans_id).first()
        value = ans.upvotes - ans.downvotes

        vote = {
            'success': True,
            'value': value,
            'ans_id': ans_id,
        }

        return JsonResponse(vote)


class SearchForums(View):

    def get(self, request, *args, **kwargs):

        topic = request.GET.get('topic')
        q = request.GET.get('q')
        # if topic.lower() in (x.lower() for x in forum_topics):
        #     template_name = 'forums/forums.html'
        #     questions = Question.objects.filter(topic__iexact=topic).order_by('-timestamp')
        # elif topic == 'None':
        #     template_name = 'forums/forums.html'
        #     questions = Question.objects.all().order_by('-timestamp')
        #
        # elif topic == 'all':
        #     return ForumView.as_view()(self.request)
        # else:
        #     template_name = 'error.html'
        #     questions = Question.objects.filter(topic__iexact=topic).order_by('-timestamp')

        if topic:
            if topic.lower() in (x.lower() for x in forum_topics):
                template_name = 'forums/forums.html'
                if q is None:
                    results = Question.objects.filter(topic__iexact=topic).order_by('-timestamp')
                elif len(q) > 0:   # case TQ
                    results = Question.objects.filter(Q(question__search=q) | Q(details__search=q), Q(topic__iexact=topic)).order_by('-timestamp')
                else:    # case TQ'
                    results = Question.objects.filter(topic__iexact=topic).order_by('-timestamp')
            else:
                template_name = 'error.html'

        else:
            template_name = 'forums/forums.html'
            if q is None:
                results = Question.objects.all()
            elif len(q) > 0:    # case T'Q
                results = Question.objects.filter(Q(question__search=q) | Q(details__search=q)).order_by('-timestamp')
            else:    # T'Q'
                results = Question.objects.all()

        paginator = Paginator(results, 25)

        page_num = request.GET.get('page')
        result = paginator.get_page(page_num)
        try:
            page = paginator.page(page_num)
        except:
            page = paginator.page(1)

        count = paginator.num_pages
        context = {
            'topic': topic.title(),
            'questions': results,
            'forum_topics': forum_topics,
            # 'questions': questions,
            'page': page,
            'page_count': count,
            'result': result,

        }

        return render(request, template_name, context)

    # def post(self, request, *args, **kwargs):
    #     # Search Questions Directory here
    #     # topic = request.POST.get('topic')
    #
    #     template_name = 'forums/forums.html'
    #
    #     if len(request.POST.get('topic')) > 0:
    #         topic = request.POST.get('topic').lower()
    #     else:
    #         topic = None
    #
    #     q = request.POST.get('q')
    #
    #     if topic:
    #         if topic in (x.lower() for x in forum_topics):
    #             template_name = 'forums/forums.html'
    #             if len(q) > 0:   # case TQ
    #                 results = Question.objects.filter(Q(question__search=q) | Q(details__search=q), Q(topic__iexact=topic)).order_by('-timestamp')
    #             else:    # case TQ'
    #                 results = Question.objects.filter(topic__iexact=topic).order_by('-timestamp')
    #         else:
    #             template_name = 'error.html'
    #
    #     else:
    #         if len(q) > 0:    # case T'Q
    #             results = Question.objects.filter(Q(question__search=q) | Q(details__search=q)).order_by('-timestamp')
    #         else:    # T'Q'
    #             results = Question.objects.all()
    #
    #     # Apply pagination
    #     paginator = Paginator(results, 25)
    #
    #     page_num = request.GET.get('page')
    #     result = paginator.get_page(page_num)
    #     try:
    #         page = paginator.page(page_num)
    #     except:
    #         page = paginator.page(1)
    #
    #     count = paginator.num_pages
    #
    #     if topic is None:
    #         topic = 'all'
    #     context = {
    #         'questions': results,
    #         'forum_topics': forum_topics,
    #         'topic': topic,
    #         'search': True,
    #         'query': q,
    #         'page': page,
    #         'page_count': count,
    #         'result': result
    #     }
    #     #####################################
    #
    #     return render(request, template_name, context)


class VoteQuestion(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):

        user = request.user
        operation = request.POST.get('operation')

        question_id = request.POST.get('question_id')
        question = Question.objects.filter(id=question_id).first()

        if not question:
            return JsonResponse({"success": False})

        if operation == 'upvote':
            question.upvotes = question.upvotes + 1
            question.ques_liked_by.add(user)
            question.save()
            return JsonResponse({"success": True, "likes": question.upvotes})
        elif operation == "remove_upvote":
            question.upvotes = question.upvotes - 1
            question.ques_liked_by.remove(user)
            question.save()
            return JsonResponse({"success": True, "likes": question.upvotes})


