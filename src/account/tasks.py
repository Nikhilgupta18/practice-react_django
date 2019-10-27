from celery import shared_task
import time, smtplib
from django.core.mail import EmailMultiAlternatives, send_mail
import datetime


@shared_task
def send_email(receiver, email_message, subject, **kwargs):

    sender = "yashmittra@gmail.com"

    if type(receiver) == list or type(receiver) == tuple:
        receivers = list(receiver)

    else:
        receivers = [receiver]

    init = time.time()


    try:
        otp = kwargs.get('otp')
    except:
        otp = None

    try:
        # smtp_server.sendmail(sender, receivers, msg.as_string())

        for rec in receivers:
            recipient = [rec]
            msgtoUser = EmailMultiAlternatives(subject=subject, body=email_message, from_email=sender, to=recipient)
            msgtoUser.attach_alternative(email_message, "text/html")
            msgtoUser.send()

        print("Successfully sent email")
    except smtplib.SMTPException as e:
        print("Error: unable to send email", e)
    finally:
        pass

    print("send email took " + str(time.time() - init) + " secs")


@shared_task
def send_backup_with_email(**kwargs):

    sender = "mittrayash@gmail.com"
    receiver = "mittrayash@gmail.com"
    today = datetime.datetime.today().strftime('%d-%b-%Y')

    subject = "Study Abroad Backup for " + str(today)

    backup_name = 'study_abroad_' + datetime.datetime.today().strftime('%d%m%y') + '.bak'
    # backup_name = 'abc.bak'
    # file = open('/home/kali/Desktop/Study Abroad/backups/' + backup_name, 'rb')
    file = open('/home/ubuntu/Ltigo/backups/' + backup_name, 'rb')
    email_message = "Backup for " + str(today) + "<br>" + str(backup_name)

    if type(receiver) == list or type(receiver) == tuple:
        receivers = list(receiver)

    else:
        receivers = [receiver]
    init = time.time()

    try:
        otp = kwargs.get('otp')
    except:
        otp = None

    try:
        # smtp_server.sendmail(sender, receivers, msg.as_string())

        for rec in receivers:
            recipient = [rec]
            msgtoUser = EmailMultiAlternatives(subject=subject, body=email_message, from_email=sender, to=recipient)
            msgtoUser.attach_alternative(email_message, "text/html")
            msgtoUser.attach(backup_name, file.read(), 'text/csv')
            msgtoUser.send()

        print("Successfully sent email")
    except smtplib.SMTPException as e:
        print("Error: unable to send email", e)
    finally:
        pass

    print("send email took " + str(time.time() - init) + " secs")
