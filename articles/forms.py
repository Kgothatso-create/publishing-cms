from django import forms
from .models import Article


from django import forms
from .models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            "category",
            "title",
            "slug",
            "subheading",
            "excerpt",
            "body",
            "featured_image",
            "status",
            "is_featured",
            "meta_title",
            "meta_description",
        ]

        widgets = {
            "excerpt": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "body": forms.Textarea(attrs={"rows": 10, "class": "form-control"}),
            "meta_description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():

            # Checkbox
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"

            # File input
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs["class"] = "form-control"

            # Select dropdowns
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"

            # Default text inputs
            else:
                field.widget.attrs["class"] = "form-control"

        # Optional: ensure checkbox doesn't inherit form-control
        self.fields["is_featured"].widget.attrs["class"] = "form-check-input"
