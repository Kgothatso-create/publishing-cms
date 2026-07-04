from .forms import NewsletterSubscriberForm


def newsletter_form(request):
    return {
        "newsletter_form": NewsletterSubscriberForm(),
    }
