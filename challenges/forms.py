from django import forms
from .models import Challenge, Spot, Visual


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
    files = MultipleFileField(label='Select files', required=False)

    class Meta:
        model = Challenge
        fields = ['event', 'longitude', 'latitude', 'files', 'description']

    def __init__(self, *args, **kwargs):
        # Check if we're editing an existing instance
        self.is_edit = kwargs.get('instance') is not None
        super().__init__(*args, **kwargs)
        #self.fields['files'].required = False
        self.fields['files'].widget.attrs['accept'] = 'video/*'
        self.fields['longitude'].widget = forms.HiddenInput()
        self.fields['latitude'].widget = forms.HiddenInput()
        # Hide the file field if we're editing
        if self.is_edit:
            self.fields['event'].widget = forms.HiddenInput()
            self.fields['files'].widget = forms.HiddenInput()



class SpotForm(forms.ModelForm):
    files = MultipleFileField(label='Select files', required=False)

    class Meta:
        model = Spot
        fields = ['event', 'name', 'longitude', 'latitude', 'files', 'description']

    def __init__(self, *args, **kwargs):
        # Check if we're editing an existing instance
        self.is_edit = kwargs.get('instance') is not None
        super().__init__(*args, **kwargs)
        #self.fields['files'].required = False
        self.fields['files'].widget.attrs['accept'] = 'video/*,image/*'
        self.fields['longitude'].widget = forms.HiddenInput()
        self.fields['latitude'].widget = forms.HiddenInput()
        # Hide the file field if we're editing
        if self.is_edit:
            self.fields['files'].widget = forms.HiddenInput()


class VisualForm(forms.ModelForm):
    class Meta:
        model = Visual
        fields = ['file']

    def __init__(self, *args, **kwargs):
        super(VisualForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = False
        self.fields['file'].widget.attrs['accept'] = 'video/*,image/*'
