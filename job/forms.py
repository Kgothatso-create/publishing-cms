from django import forms

from .models import Department, Job


def generate_department_code():
    """
    Generates department codes in the format:

    DEP-001
    DEP-002
    DEP-003

    Reuses deleted department codes.
    """

    existing_codes = set(
        Department.objects.values_list("code",flat=True,)
    )

    number = 1
    while True:
        code = f"DEP-{number:03d}"
        if code not in existing_codes:
            return code
        number += 1


def generate_job_code():

    last_job = Job.objects.order_by("-created_at").first()
    if not last_job:
        number = 1
    else:
        try:
            number = int(last_job.job_code.split("-")[1]) + 1
        except (IndexError, ValueError):
            number = Job.objects.count() + 1

    return f"IF-{number:05d}"


class JobCreateForm(forms.ModelForm):

    class Meta:
        model = Job
        fields = [
            "title",
            "description",
            "department",
            "is_active",
            "level",
            "grade",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

        self.fields["is_active"].widget.attrs.update({"class": "form-check-input"})

    def save(self, commit=True):

        job = super().save(commit=False)

        if not job.job_code:
            job.job_code = generate_job_code()

        if commit:
            job.save()

        return job


class DepartmentCreateForm(forms.ModelForm):

    class Meta:
        model = Department
        fields = ["name", "description", "is_active",]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update(
                {"class": "form-control"}
            )

        self.fields["is_active"].widget.attrs.update(
            {"class": "form-check-input"}
        )

    def save(self, commit=True):

        department = super().save(commit=False)

        if not department.code:
            department.code = generate_department_code()

        if commit:
            department.save()

        return department
