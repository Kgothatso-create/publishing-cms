from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse


User = get_user_model()


def send_password_reset_email(email, request):
    users = User.objects.filter(
        email__iexact=email,
        is_active=True,
    )

    for user in users:
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = request.build_absolute_uri(
            reverse(
                "reset_password",
                kwargs={
                    "uidb64": uidb64,
                    "token": token,
                },
            )
        )

        context = {
            "user": user,
            "reset_url": reset_url,
        }

        subject = "Password Reset Request"

        message = render_to_string(
            "registration/password_reset_email.html",
            context,
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


def send_username_recovery_email(email, request):
    users = User.objects.filter(
        email__iexact=email,
        is_active=True,
    )

    if not users.exists():
        return

    token = signing.dumps(
        email,
        salt="username-recovery",
    )

    recovery_url = request.build_absolute_uri(
        reverse(
            "recover_username",
            kwargs={"token": token},
        )
    )

    send_mail(
        subject="Username Recovery",
        message=(
            "You requested to recover your username.\n\n"
            f"Click the link below to view your username:\n{recovery_url}\n\n"
            "This link expires in one hour."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
