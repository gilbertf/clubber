from django import forms
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django_flatpickr.widgets import DatePickerInput, TimePickerInput, DateTimePickerInput
from django_flatpickr.schemas import FlatpickrOptions
from django.contrib.auth import get_user_model
from django.db.models.functions import Now
from django.db import models
from .models import Event, Typ, Person
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from modeltranslation.forms import TranslationModelForm

class TypForm(forms.ModelForm):
    class Meta:
        model = Typ
        fields = [
                  "name_de",
                  "description_de",
                  "name_en",
                  "description_en",
                  "url"]
        labels = { "name_en": _("Name in English"),
                  "name_de": _("Name in German"),
                  "description_en": _("Description in English"),
                  "description_de": _("Description in German"),
                  }

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Person
        if settings.EMAIL_NOTIFICATION_ENABLE:
            fields = [ "username", "email", "language", "email_notification_new_event", "email_notification_joined_event" ]
        else:
            fields = [ "username", "email", "language" ]
        labels = { "email": _("Email address"), "language": _("Language") }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [ "date", "start_time", "end_time", "typ", "min_participants", "max_participants", "organizer" ]
        widgets = {
            "date" : DatePickerInput(options=FlatpickrOptions(altFormat='d. F Y',minDate='today')),
            "start_time" : TimePickerInput(options=FlatpickrOptions(altFormat="H:i",minuteIncrement = "15")),
            "end_time" : TimePickerInput(range_from="start_time",options=FlatpickrOptions(altFormat="H:i",minuteIncrement = "15")),
        }

    def __init__(self, *args, **kwargs):
            super(EventForm, self).__init__(*args, **kwargs) 
            self.fields['organizer'].queryset = get_user_model().objects.filter(is_staff=True)
