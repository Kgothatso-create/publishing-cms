from django import forms
from people.models import NewsletterSubscriber, User


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


class UserRegisterForm(OnboardingBaseForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["username", "email"]

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.onboarding_status = "not_started"

        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"})
    )
