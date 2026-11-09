import random

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

from job.models import Job
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

    # -------------------------
    # PERSONAL INFORMATION
    # -------------------------

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter first name",
        })
    )

    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter last name",
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter email address",
        })
    )

    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date",
        })
    )

    # -------------------------
    # EMPLOYMENT INFORMATION
    # -------------------------

    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        widget=forms.Select(attrs={
            "class": "form-select",
        }),
        empty_label="Select role"
    )

    job = forms.ModelChoiceField(
        queryset=Job.objects.all(),
        required=False,
        empty_label="Select job (optional)",
        widget=forms.Select(attrs={
            "class": "form-select",
        })
    )

    manager = forms.ModelChoiceField(
        queryset=Employment.objects.all(),
        required=False,
        empty_label="Select manager (optional)",
        widget=forms.Select(attrs={
            "class": "form-select",
        })
    )

    status = forms.ChoiceField(
        choices=Employment.EmploymentStatus.choices,
        initial=Employment.EmploymentStatus.ACTIVE,
        widget=forms.Select(attrs={
            "class": "form-select",
        })
    )

    employment_type = forms.ChoiceField(
        choices=Employment.EmploymentType.choices,
        widget=forms.Select(attrs={
            "class": "form-select",
        })
    )

    hire_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date",
        })
    )

    probation_end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date",
        })
    )

    termination_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date",
        })
    )

    location = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter work location",
        })
    )

    cost_center = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter cost center",
        })
    )

    # -------------------------
    # CONTACT INFORMATION
    # -------------------------

    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter phone number",
        })
    )

    address_line_1 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Address line 1",
        })
    )

    address_line_2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Address line 2",
        })
    )

    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter city",
        })
    )

    province = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter province",
        })
    )

    postal_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter postal code",
        })
    )

    country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
        })
    )

    # -------------------------
    # EMERGENCY CONTACT
    # -------------------------

    emergency_contact_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Emergency contact name",
        })
    )

    emergency_contact_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Emergency contact phone",
        })
    )

    # -------------------------
    # VALIDATION
    # -------------------------

    def clean_email(self):
        email = self.cleaned_data["email"]

        if Employment.objects.filter(
            employee_email__iexact=email
        ).exists():
            raise ValidationError(
                "This email address is already assigned to an employee."
            )

        if User.objects.filter(username__iexact=email).exists():
            raise ValidationError(
                "This email address is already being used as a username."
            )

        return email

    # -------------------------
    # SAVE
    # -------------------------

    @transaction.atomic
    def save(self):

        data = self.cleaned_data

        DEFAULT_EMPLOYEE_PASSWORD = "ChangeMe123!"

        # Create Django User
        user = User.objects.create_user(
            username=data["email"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            password=DEFAULT_EMPLOYEE_PASSWORD,
        )

        # Create Employment
        employment = Employment.objects.create(
            user=user,
            employee_number=generate_employee_number(),
            employee_email=data["email"],
            role=data["role"],
            job=data["job"],
            manager=data["manager"],
            status=data["status"],
            employment_type=data["employment_type"],
            hire_date=data["hire_date"],
            probation_end_date=data["probation_end_date"],
            termination_date=data["termination_date"],
            location=data["location"],
            cost_center=data["cost_center"],
        )

        # Create Employee Profile
        EmployeeProfile.objects.create(
            employment=employment,
            first_name=data["first_name"],
            last_name=data["last_name"],
            date_of_birth=data["date_of_birth"],
            phone_number=data["phone_number"],
            address_line_1=data["address_line_1"],
            address_line_2=data["address_line_2"],
            city=data["city"],
            province=data["province"],
            postal_code=data["postal_code"],
            country=data["country"],
            emergency_contact_name=data["emergency_contact_name"],
            emergency_contact_phone=data["emergency_contact_phone"],
        )

        return employment


class EmployeeEditForm(forms.Form):

    # -------------------------
    # PERSONAL INFORMATION
    # -------------------------

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter first name",
        })
    )

    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter last name",
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter email address",
        })
    )

    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date",
        })
    )

    # -------------------------
    # EMPLOYMENT INFORMATION
    # -------------------------

    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"})
    )

    job = forms.ModelChoiceField(
        queryset=Job.objects.all(),
        required=False,
        empty_label="Select job (optional)",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    manager = forms.ModelChoiceField(
        queryset=Employment.objects.none(),
        required=False,
        empty_label="Select manager (optional)",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    status = forms.ChoiceField(
        choices=Employment.EmploymentStatus.choices,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    employment_type = forms.ChoiceField(
        choices=Employment.EmploymentType.choices,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    hire_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date",
        })
    )

    probation_end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date",
        })
    )

    termination_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date",
        })
    )

    location = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter work location",
        })
    )

    cost_center = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter cost center",
        })
    )

    # -------------------------
    # CONTACT INFORMATION
    # -------------------------

    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter phone number",
        })
    )

    address_line_1 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Address line 1",
        })
    )

    address_line_2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Address line 2",
        })
    )

    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter city",
        })
    )

    province = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter province",
        })
    )

    postal_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter postal code",
        })
    )

    country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
        })
    )

    # -------------------------
    # EMERGENCY CONTACT
    # -------------------------

    emergency_contact_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Emergency contact name",
        })
    )

    emergency_contact_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Emergency contact phone",
        })
    )

    def __init__(self, *args, employee, **kwargs):
        super().__init__(*args, **kwargs)

        self.employee = employee
        self.profile = employee.profile
        self.user = employee.user

        self.fields["manager"].queryset = Employment.objects.exclude(
            pk=employee.pk
        )

        if not self.is_bound:
            self.initial.update({
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
                "date_of_birth": self.profile.date_of_birth,
                "role": employee.role,
                "job": employee.job,
                "manager": employee.manager,
                "status": employee.status,
                "employment_type": employee.employment_type,
                "hire_date": employee.hire_date,
                "probation_end_date": employee.probation_end_date,
                "termination_date": employee.termination_date,
                "location": employee.location,
                "cost_center": employee.cost_center,
                "phone_number": self.profile.phone_number,
                "address_line_1": self.profile.address_line_1,
                "address_line_2": self.profile.address_line_2,
                "city": self.profile.city,
                "province": self.profile.province,
                "postal_code": self.profile.postal_code,
                "country": self.profile.country,
                "emergency_contact_name": self.profile.emergency_contact_name,
                "emergency_contact_phone": self.profile.emergency_contact_phone,
            })

    def clean_email(self):
        email = self.cleaned_data["email"]

        if Employment.objects.filter(
            employee_email__iexact=email
        ).exclude(pk=self.employee.pk).exists():
            raise ValidationError(
                "This email address is already assigned to another employee."
            )

        if User.objects.filter(
            username__iexact=email
        ).exclude(pk=self.user.pk).exists():
            raise ValidationError(
                "This email address is already being used as a username."
            )

        return email

    @transaction.atomic
    def save(self):
        data = self.cleaned_data

        # Update Django User
        self.user.first_name = data["first_name"]
        self.user.last_name = data["last_name"]
        self.user.email = data["email"]
        self.user.username = data["email"]
        self.user.save()

        # Update Employment
        self.employee.employee_email = data["email"]
        self.employee.role = data["role"]
        self.employee.job = data["job"]
        self.employee.manager = data["manager"]
        self.employee.status = data["status"]
        self.employee.employment_type = data["employment_type"]
        self.employee.hire_date = data["hire_date"]
        self.employee.probation_end_date = data["probation_end_date"]
        self.employee.termination_date = data["termination_date"]
        self.employee.location = data["location"]
        self.employee.cost_center = data["cost_center"]
        self.employee.save()

        # Update EmployeeProfile
        self.profile.first_name = data["first_name"]
        self.profile.last_name = data["last_name"]
        self.profile.date_of_birth = data["date_of_birth"]
        self.profile.phone_number = data["phone_number"]
        self.profile.address_line_1 = data["address_line_1"]
        self.profile.address_line_2 = data["address_line_2"]
        self.profile.city = data["city"]
        self.profile.province = data["province"]
        self.profile.postal_code = data["postal_code"]
        self.profile.country = data["country"]
        self.profile.emergency_contact_name = data["emergency_contact_name"]
        self.profile.emergency_contact_phone = data["emergency_contact_phone"]
        self.profile.save()

        return self.employee


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
