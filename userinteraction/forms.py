from django import forms
from .models import ChallengeComment

class ChallengeCommentForm(forms.ModelForm):
    class Meta:
        model = ChallengeComment
        fields = ['comment']