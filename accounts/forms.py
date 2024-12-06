from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import (
                                                    UserAttributeSimilarityValidator,
                                                    MinimumLengthValidator,
                                                    CommonPasswordValidator,
                                                    NumericPasswordValidator,
                                                    validate_password,  # Import this for manual validation
                                                    )
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

class StrongPasswordValidator:
    """Custom password strength validator"""
    def validate(self, password, user=None):
        # Check password complexity
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
        # Require at least one uppercase, one lowercase, one number, and one special character
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one number.")
        # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        #     raise ValidationError("Password must contain at least one special character.")

    def get_help_text(self):
        return (
            "Your password must contain at least one uppercase letter, "
            "one lowercase letter, one number, and one special character."
        )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254, 
        help_text='Required. Enter a valid email address.',
        validators=[validate_email]
    )
    terms_and_conditions = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(),
        label='I agree to the Terms and Conditions',
        error_messages={
            'required': 'You must agree to the terms and conditions to proceed.'
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'terms_and_conditions')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password2'].help_text = (
                                              "<div class='password-requirements'>"
            "<p>Your password must meet the following requirements:</p>"
            "<ul>"
            "<li>At least 8 characters long</li>"
            "<li>Cannot be too common or easily guessed</li>"
            "<li>Must include:</li>"
            "<ul>"
            "<li>One uppercase letter</li>"
            "<li>One lowercase letter</li>"
            "<li>One number</li>"
            "</ul>"
            "</ul>"
            "</div>")
        # Multiline help text for terms and conditions
        self.fields['terms_and_conditions'].help_text = (
            "<div id='terms-conditions-popup' class='terms-conditions popup'>"
            "<button class='close-button stylish-button' onclick='closePopup()'>X</button>"
            "<h3>Terms and Conditions</h3>"
            "<div class='liability-disclaimer'>"
            "<h4>Liability Disclaimer</h4>"
            "<p>By creating an account and using this platform, you acknowledge and agree to the following:</p>"
            "<ol>"
            "<li><strong>User Content Responsibility:</strong> Users are solely responsible for the content they upload, share, or interact with on this platform.</li>"
            "<li><strong>No Liability for User Actions:</strong> The website and its owner/operator shall not be held liable for any damages, injuries, losses, or consequences arising from:</li>"
            "<ul>"
            "<li>Content uploaded by users</li>"
            "<li>Interactions between users</li>"
            "<li>Participation in website events or activities</li>"
            "<li>Any claims, actions, or damages resulting from user-generated content or interactions</li>"
            "</ul>"
            "<li><strong>Risk Acknowledgment:</strong> Users participate in any platform activities entirely at their own risk.</li>"
            "<li><strong>Content Disclaimer:</strong> We do not review, verify, or guarantee the accuracy, safety, or appropriateness of user-generated content.</li>"
            "<li><strong>Legal Protection:</strong> By agreeing, you waive any right to hold the website or its operators legally responsible for user actions or content.</li>"
            "</ol>"
            "<p><em>By checking this box, you confirm that you have read, understood, and agree to these terms.</em></p>"
            "</div>"
            "</div>"
        )


    def clean_email(self):
        # Ensure email is unique
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_password1(self):
        # Get the password from cleaned_data
        password = self.cleaned_data.get('password1')
        
        # Manually validate the password
        try:
            # Apply all validators
            validate_password(
                password, 
                user=self.instance,
                password_validators=[
                    UserAttributeSimilarityValidator(),
                    MinimumLengthValidator(min_length=8),
                    CommonPasswordValidator(),
                    NumericPasswordValidator(),
                    StrongPasswordValidator()
                ]
            )
        except ValidationError as errors:
            # Raise validation errors
            self.add_error('password1', errors)
        
        return password

