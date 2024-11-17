from django.contrib import admin
from .models import Challenge, Spot, Visual
# from django.contrib.contenttypes.admin import GenericTabularInline


# class VisualInline(GenericTabularInline):
#     model = Visual


# class ChallengeAdmin(admin.ModelAdmin):
#     inlines = [
#         VisualInline,
#     ]


# class SpotAdmin(admin.ModelAdmin):
#     inlines = [
#         VisualInline,
#     ]


# admin.site.register(Challenge, ChallengeAdmin)
# admin.site.register(Spot, SpotAdmin)


class VisualInline(admin.TabularInline):
    model = Visual
    extra = 0  # Number of empty forms to display

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    inlines = [
        VisualInline,
    ]

@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    inlines = [
        VisualInline,
    ]


admin.site.register(Visual)