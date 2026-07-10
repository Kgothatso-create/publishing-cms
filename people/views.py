from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, NewsletterSubscriberForm, ProfileUpdateForm, UserPasswordChangeForm, UserRegisterForm


def subscribe_newsletter(request):
    if request.method != "POST":
        return redirect(request.META.get("HTTP_REFERER", "/"))

    form = NewsletterSubscriberForm(request.POST)

    if form.is_valid():
        form.save()
        messages.success(
            request,
            "Thank you for subscribing to the Inkflow Inspiration newsletter!"
        )
    else:
        for error in form.errors.get("email", []):
            messages.error(request, error)

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
