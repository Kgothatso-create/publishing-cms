from django import forms

from .models import Job


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
