from django import forms
from django.forms import modelformset_factory

from people.models import NewsletterSubscriber, PersonIdentityDocument, PersonProfile, User


class OnboardingBaseForm(forms.ModelForm):
    """
    Shared behavior for onboarding forms.
    Keeps forms clean and consistent.
    """

    def __init__(self, *args, **kwargs):
        self.is_edit_mode = kwargs.pop("is_edit_mode", False)
        super().__init__(*args, **kwargs)

        # Future hook: consistent styling or field handling


class UserOnboardingForm(OnboardingBaseForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class PersonProfileForm(OnboardingBaseForm):
    class Meta:
        model = PersonProfile
        fields = [
            "gender", "race", "address_line_1", "address_line_2",
            "city", "province", "postal_code", "country",
        ]


class PersonIdentityDocumentForm(OnboardingBaseForm):
    class Meta:
        model = PersonIdentityDocument
        fields = [
            "document_type",
            "file",
            "identification_document_number",
            "issued_country",
            "issue_date",
            "expiry_date",
            "is_primary",
        ]


PersonIdentityDocumentFormSet = modelformset_factory(
    PersonIdentityDocument,
    form=PersonIdentityDocumentForm,
    extra=1,
    can_delete=True,
    validate_min=False,
    validate_max=False
)


class NewsletterSubscriberForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your email address",
                    "autocomplete": "email",
                }
            ),
        }
        labels = {
            "email": "",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if NewsletterSubscriber.objects.filter(
            email=email,
            is_active=True,
        ).exists():
            raise forms.ValidationError(
                "This email address is already subscribed."
            )

        return email
