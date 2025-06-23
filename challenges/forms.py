from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from .models import Challenge, Spot, Visual, get_challenge_model_class


def get_challenge_form_class(challenge_type):
    if challenge_type == Challenge.__name__:
        return ChallengeForm
    elif challenge_type == Spot.__name__:
        return SpotForm


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ChallengeForm(forms.ModelForm):
    files = MultipleFileField(label=_('Select files'), required=False)
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': _("Enter a description..."),
            'rows': 3,
            'required': 'required',  # Explicitly mark it as required in HTML
        }),
        required=True
    )
    class Meta:
        model = Challenge
        fields = ['longitude', 'latitude', 'files', 'description']

    def __init__(self, *args, **kwargs):
        # Check if we're editing an existing instance
        self.is_edit = kwargs.get('instance') is not None
        super().__init__(*args, **kwargs)
        self.fields['files'].widget.attrs['accept'] = 'video/*'
        # the clean makes one required and this allows editing
        self.fields['files'].required = False
        self.fields['longitude'].widget = forms.HiddenInput()
        self.fields['latitude'].widget = forms.HiddenInput()
        # Hide the file field if we're editing
        if self.is_edit:
            # self.fields['event'].widget = forms.HiddenInput()
            self.fields['files'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()

        # Check if there is at least one file uploaded
        files = cleaned_data.get('files', [])

        # Check if this is a new instance (creation)
        if not self.instance.pk:
            if not files:
                raise ValidationError(_('At least one file is required.'))
        return cleaned_data


class SpotForm(forms.ModelForm):
    files = MultipleFileField(label=_('Select files'), required=False)
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': _("Enter a description..."),
            'rows': 3,
            'required': 'required',  # Explicitly mark it as required in HTML
        }),
        required=True
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': _("Enter a spot name..."),
            'required': 'required',  # Explicitly mark it as required in HTML
        }),
        required=True
    )

    class Meta:
        model = Spot
        fields = ['name', 'longitude', 'latitude', 'files', 'description']

    def __init__(self, *args, **kwargs):
        # Check if we're editing an existing instance
        self.is_edit = kwargs.get('instance') is not None
        super().__init__(*args, **kwargs)
        self.fields['files'].widget.attrs['accept'] = 'video/*,image/*'
        # the clean makes one required and this allows editing
        self.fields['files'].required = False
        self.fields['longitude'].widget = forms.HiddenInput()
        self.fields['latitude'].widget = forms.HiddenInput()
        # Hide the file field if we're editing
        if self.is_edit:
            self.fields['files'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()

        # Check if there is at least one file uploaded
        files = cleaned_data.get('files', [])
        if not self.instance.pk:
            if not files:  # If the list is empty, raise an error
                raise ValidationError(_('At least one file is required.'))

        return cleaned_data

class VisualForm(forms.ModelForm):
    class Meta:
        model = Visual
        fields = ['file']

    def __init__(self, *args, **kwargs):
        super(VisualForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = False
        self.fields['file'].widget.attrs['accept'] = 'video/*,image/*'
