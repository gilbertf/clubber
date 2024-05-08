from django import forms
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm
from django.contrib.auth.models import User
from django.forms import EmailField
from django.conf import settings
from events.models import Person
import django.contrib.auth.password_validation as password_validation
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

class NewUserForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
        validators=[validate_password]
    )

    password2 = forms.CharField(
        label=_("Confirm password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )

    email = EmailField(label=_("Email address"), required=True, help_text=_("You can enable notifications on newly created or updated events"))
    if not settings.EMAIL_NOTIFICATION_ENABLE:
        email.help_text = None

    class Meta:
        model = Person
        if settings.EMAIL_NOTIFICATION_ENABLE:
            fields = [ "username", "password1", "password2", "email", "email_notification_new_event", "email_notification_joined_event", "language" ]
        else:
            fields = [ "username", "password1", "password2", "email", "language" ]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Password mismatch"))
        return password2

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            return user
        return user

class PasswordChangeForm(SetPasswordForm):
	class Meta:
		model = User
		fields = [ "password1", "password2" ]

	def save(self, commit=True):
		user = super(PasswordChangeForm, self).save(commit=False)
		if commit:
			user.save()
		return user
