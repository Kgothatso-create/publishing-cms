from django import forms

from .models import Article, ArticleReport


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            "category",
            "title",
            "body",
            "featured_image",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your article title",
                }
            ),
            "body": forms.Textarea(
                attrs={
                    "rows": 10,
                    "class": "form-control",
                    "placeholder": "Write your article here...",
                }
            ),
            "category": forms.Select(
                attrs={"class": "form-select"}
            ),
            "featured_image": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
        }

        help_texts = {
            "category": (
                "Please choose the category that best matches the topic of your article."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply Bootstrap classes to any fields not explicitly styled
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.setdefault("class", "form-control")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class ArticleReportForm(forms.ModelForm):

    class Meta:
        model = ArticleReport

        fields = [
            "reason",
            "description",
        ]

        widgets = {
            "reason": forms.Select(
                attrs={
                    "class": "form-select select2"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Please provide additional details about your report (optional)."
                }
            ),
        }

        labels = {
            "reason": "Reason for reporting",
            "description": "Additional information",
        }
