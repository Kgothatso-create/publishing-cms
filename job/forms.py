from django import forms

from .models import Department, Job


def generate_department_code():
    """
    Generates department codes in the format:
    DEP001
    DEP002
    DEP003
    """

    last_department = (
        Department.objects
        .order_by("-code")
        .first()
    )

    if (
        last_department and
        last_department.code.startswith("DEP")
    ):
        try:
            last_number = int(
                last_department.code.replace("DEP", "")
            )
        except ValueError:
            last_number = 0
    else:
        last_number = 0

    return f"DEP{last_number + 1:03d}"


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
