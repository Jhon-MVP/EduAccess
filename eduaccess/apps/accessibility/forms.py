from django import forms
from .models import AccessibilityProfile

class AccessibilityProfileForm(forms.ModelForm):
    class Meta:
        model = AccessibilityProfile
        fields = ["disability_type", "high_contrast", "font_size", "subtitles"]
        widgets = {
            "disability_type": forms.RadioSelect(attrs={"class": "hidden"}),
            "high_contrast": forms.CheckboxInput(attrs={"class": "toggle-checkbox"}),
            "subtitles": forms.CheckboxInput(attrs={"class": "toggle-checkbox"}),
            "font_size": forms.NumberInput(attrs={"type": "range", "min": 1, "max": 5, "class": "w-full h-2 bg-gray-200 rounded-lg cursor-pointer dark:bg-gray-700"}),
        }
