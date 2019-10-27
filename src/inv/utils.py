from smtplib import SMTP_SSL as SMTP #SSL connection
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time, smtplib
from django.core.mail import EmailMultiAlternatives, send_mail
from account.models import User
# import requests


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


def send_sms(msg, mobile_number, country_code):

    msgApi_url = "http://api.msg91.com/api/sendhttp.php"
    recipients = mobile_number
    auth_key = "255324AWxfPq8Xc7v5c3266f0"
    params = {'authkey': auth_key,
              'mobiles': recipients,
              'message': msg,
              'sender': 'YASHMI',
              'route': 4,
              'country': country_code}
    try:
        r = requests.get(msgApi_url, params=params)
        print("sms api status code: "+str(r.status_code))
        if r.status_code == 200:
            print("sms sent successfully")
            return True
    except:
        print(r)
        print(r.status_code)
        print("Failed to hit sms api")

    return False
