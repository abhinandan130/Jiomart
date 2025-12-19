from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(email, otp):
    subject = "Your Login OTP - JioMart Clone"
    message = f"Your OTP is {otp}. Please do not share it with anyone."
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
