from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = [
            "name", "email", "phone", "package", "package_interest",
            "travel_date", "adults", "children", "message",
        ]
        widgets = {
            "package": forms.HiddenInput(),
            "package_interest": forms.TextInput(
                attrs={"placeholder": "Which tour are you interested in?"}),
            "travel_date": forms.DateInput(attrs={"type": "date"}),
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ("package",):
                field.widget.attrs.setdefault(
                    "placeholder", field.label or name.replace("_", " ").title())
        self.fields["phone"].required = False
        self.fields["travel_date"].required = False
        self.fields["adults"].required = False
        self.fields["children"].required = False
        self.fields["package_interest"].required = False
