from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import EmailForm, LoginForm, NewsletterSubscriberForm, ProfileUpdateForm, UserPasswordChangeForm, \
    UserPasswordResetForm, UserRegisterForm
from .utility import send_password_reset_email, send_username_recovery_email


def subscribe_newsletter(request):
    if request.method != "POST":
        return redirect(request.META.get("HTTP_REFERER", "/"))

    form = NewsletterSubscriberForm(request.POST)

    if form.is_valid():
        form.save()
        messages.success(
            request,
            "Thank you for subscribing to the Inkflow Inspiration newsletter!",
            extra_tags="newsletter"
        )
    else:
        for error in form.errors.get("email", []):
            messages.error(request, error, extra_tags="newsletter")

    return redirect(request.META.get("HTTP_REFERER", "/"))


def register_view(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)

        if user_form.is_valid():
            try:
                user_form.save()

                messages.success(request, "Account created successfully. Please log in.")
                return redirect("login")

            except Exception as e:
                messages.error(request, f"Something went wrong: {e}")

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        user_form = UserRegisterForm()

    return render(request, "people/register.html", {
        "user_form": user_form,
    })


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("home")

            else:
                messages.error(request, "Invalid username or password")

    else:
        form = LoginForm()

    return render(request, "people/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def profile_view(request):

    user = request.user
    if request.method == "POST":
        profile_form = ProfileUpdateForm(
            request.POST,
            instance=user
        )
        password_form = UserPasswordChangeForm(
            user,
            request.POST
        )
        if "update_profile" in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                messages.success(
                    request,
                    "Your profile has been updated."
                )
                return redirect("profile")

        elif "change_password" in request.POST:
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(
                    request,
                    password_form.user
                )
                messages.success(
                    request,
                    "Your password has been changed."
                )
                return redirect("profile")
    else:
        profile_form = ProfileUpdateForm(
            instance=user
        )
        password_form = UserPasswordChangeForm(
            user
        )

    context = {
        "profile_form": profile_form,
        "password_form": password_form,
    }

    return render(
        request,
        "people/profile.html",
        context
    )


@require_POST
def explorer_login(request):
    User = get_user_model()

    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect("home")

    try:
        explorer = User.objects.get(username="Explorer")
    except User.DoesNotExist:
        messages.error(request, "Explorer access is currently unavailable.")
        return redirect("home")

    login(request, explorer, backend="django.contrib.auth.backends.ModelBackend")

    return redirect("home")


def forgot_username(request):
    if request.method == "POST":
        form = EmailForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            send_username_recovery_email(
                email=email,
                request=request,
            )

            messages.success(
                request,
                "If an account exists with that email, a username recovery link has been sent."
            )

            return redirect("forgot_username")

    else:
        form = EmailForm()

    return render(
        request,
        "people/forgot_email_template.html",
        {
            "form": form,
            "title": "Recover Username",
            "description": "This application is a demonstration prototype.",
            "button_text": "Recover Username",
        },
    )


def forgot_password(request):
    if request.method == "POST":
        form = UserPasswordResetForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            send_password_reset_email(
                email=email,
                request=request,
            )

            messages.success(
                request,
                "If an account exists with that email, a password reset link has been sent."
            )

            return redirect("forgot_password")

    else:
        form = UserPasswordResetForm()

    return render(
        request,
        "people/forgot_email_template.html",
        {
            "form": form,
            "title": "Reset Password",
            "description": "This application is a demonstration prototype.",
            "button_text": "Reset Password",
        },
    )
