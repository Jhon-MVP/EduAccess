from django.contrib import admin
from .models import AccessibilityProfile


@admin.register(AccessibilityProfile)
class AccessibilityProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "disability_type",
        "high_contrast",
        "subtitles",
        "font_size",
    )

    list_filter = (
        "disability_type",
        "high_contrast",
        "subtitles",
    )

    search_fields = ("user__username", "user__email")
