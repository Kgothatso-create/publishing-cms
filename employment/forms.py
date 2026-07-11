from django import forms

from people.models import User
from .models import Employment, EmployeeProfile, Role


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

    employee_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Employee number",
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
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        )
    )

    hire_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        )
    )


    def save(self):

        user = User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )

        employment = Employment.objects.create(
            user=user,
            employee_number=self.cleaned_data["employee_number"],
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