from django.contrib import messages
from django.shortcuts import redirect

from .forms import NewsletterSubscriberForm


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
