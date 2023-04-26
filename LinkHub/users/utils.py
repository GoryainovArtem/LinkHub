from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail


def send_verification_email(request, user):
    current_site = get_current_site(request)
    context = {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user)
    }
    send_mail(
        subject='Подтверждение регистрации',
        message=render_to_string(template_name='users/verification_email.html',
                                 context=context),
        from_email='linkhub@gmail.com',
        recipient_list=[user.email]
    )
    return redirect('users:verification_message')
