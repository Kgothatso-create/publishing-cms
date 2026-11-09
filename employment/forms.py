import random

from django import forms

from people.models import User
from .models import CompanyEvent, Employment, EmployeeProfile, Notification, Role


def generate_role_code():
    """
    Generates role codes in the format:

    ROLE-001
    ROLE-002
    ROLE-003

    Reuses deleted role codes.
    """

    existing_codes = set(
        Role.objects.values_list("code", flat=True, )
    )

    number = 1
    while True:
        code = f"ROLE-{number:03d}"
        if code not in existing_codes:
            return code
        number += 1


def generate_employee_number():
    """
    Generate a unique six-digit employee number.
    """

    while True:
        employee_number = f"INKF-{random.randint(100000, 999999)}"

        if not Employment.objects.filter(
            employee_number=employee_number
        ).exists():
            return employee_number


class RoleCreateForm(forms.ModelForm):

    class Meta:
        model = Role
        fields = [
            "name",
            "description",
            "is_active",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                }
            )

        self.fields["is_active"].widget.attrs.update(
            {
                "class": "form-check-input",
            }
        )

    def save(self, commit=True):

        role = super().save(commit=False)

        role.code = generate_role_code()

        if commit:
            role.save()

        return role


class EmployeeCreateForm(forms.Form):

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter first name",
            }
        )
    )

    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter last name",
            }
        )
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter email address",
            }
        )
    )

    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(is_active=True),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        empty_label="Select role"
    )

    employment_type = forms.ChoiceField(
        choices=Employment.EmploymentType.choices,
        widget=forms.Select(attrs={"class": "form-select",})
    )

    hire_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date",}
        )
    )

    def save(self):
        DEFAULT_EMPLOYEE_PASSWORD = "ChangeMe123!"

        user = User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            password=DEFAULT_EMPLOYEE_PASSWORD,
        )

        employment = Employment.objects.create(
            user=user,
            employee_number=generate_employee_number(),
            employee_email=self.cleaned_data["email"],
            role=self.cleaned_data["role"],
            employment_type=self.cleaned_data["employment_type"],
            hire_date=self.cleaned_data["hire_date"],
        )

        EmployeeProfile.objects.create(
            employment=employment,
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )

        return employment


class CompanyEventForm(forms.ModelForm):
    class Meta:
        model = CompanyEvent
        fields = [
            "title",
            "description",
            "event_type",
            "event_date",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter event title",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter event description (optional)",
            }),
            "event_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "event_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
        }


class NotificationForm(forms.ModelForm):

    class Meta:
        model = Notification
        fields = ["title", "message", "link", "recipients"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Notification title"
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Write your notification..."
            }),
            "link": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "Optional URL"
            }),
            "recipients": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["recipients"].queryset = Employment.objects.filter(
            status=Employment.EmploymentStatus.ACTIVE
        ).select_related("user")
