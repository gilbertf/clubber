from django import forms
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django_flatpickr.widgets import DatePickerInput, TimePickerInput, DateTimePickerInput
from django_flatpickr.schemas import FlatpickrOptions
from django.contrib.auth import get_user_model
from django.db.models.functions import Now
from django.db import models
from .models import Event, Typ, Person, Configuration
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from modeltranslation.forms import TranslationModelForm

class ConfigurationForm(forms.ModelForm):
    class Meta:
        model = Configuration
        fields = [
            "impressum_de",
            "impressum_en",
            "email_confirm_open_subject_de",
            "email_confirm_open_txt_de",
            "email_confirm_open_subject_en",
            "email_confirm_open_txt_en",
            "email_new_event_subject_de",
            "email_new_event_txt_de",
            "email_new_event_subject_en",
            "email_new_event_txt_en",
            "email_fully_booked_subject_de",
            "email_fully_booked_txt_de",
            "email_fully_booked_subject_en",
            "email_fully_booked_txt_en",
            "email_sufficient_participants_missing_organizer_subject_de",
            "email_sufficient_participants_missing_organizer_txt_de",
            "email_sufficient_participants_missing_organizer_subject_en",
            "email_sufficient_participants_missing_organizer_txt_en",
            "email_cancle_subject_de",
            "email_cancle_txt_de",
            "email_cancle_subject_en",
            "email_cancle_txt_en",
            "email_pending_open_subject_de",
            "email_pending_open_txt_de",
            "email_pending_open_subject_en",
            "email_pending_open_txt_en"
        ]
        labels = {
            "impressum_de": _("Impressum in German"),
            "impressum_en": _("Impressum in English"),
            "email_confirm_open_subject_de": _("Email Confirm Open Subject in German"),
            "email_confirm_open_txt_de": _("Email Confirm Open Text in German"),
            "email_confirm_open_subject_en": _("Email Confirm Open Subject in English"),
            "email_confirm_open_txt_en": _("Email Confirm Open Text in English"),
            "email_new_event_subject_de": _("Email New Event Subject in German"),
            "email_new_event_txt_de": _("Email New Event Text in German"),
            "email_new_event_subject_en": _("Email New Event Subject in English"),
            "email_new_event_txt_en": _("Email New Event Text in English"),
            "email_fully_booked_subject_de": _("Email Fully Booked Subject in German"),
            "email_fully_booked_txt_de": _("Email Fully Booked Text in German"),
            "email_fully_booked_subject_en": _("Email Fully Booked Subject in English"),
            "email_fully_booked_txt_en": _("Email Fully Booked Text in English"),
            "email_sufficient_participants_missing_organizer_subject_de": _("Email Sufficient Participants Missing Organizer Subject in German"),
            "email_sufficient_participants_missing_organizer_txt_de": _("Email Sufficient Participants Missing Organizer Text in German"),
            "email_sufficient_participants_missing_organizer_subject_en": _("Email Sufficient Participants Missing Organizer Subject in English"),
            "email_sufficient_participants_missing_organizer_txt_en": _("Email Sufficient Participants Missing Organizer Text in English"),
            "email_cancle_subject_de": _("Email Cancel Subject in German"),
            "email_cancle_txt_de": _("Email Cancel Text in German"),
            "email_cancle_subject_en": _("Email Cancel Subject in English"),
            "email_cancle_txt_en": _("Email Cancel Text in English"),
            "email_pending_open_subject_de": _("Email Pending Open Subject in German"),
            "email_pending_open_txt_de": _("Email Pending Open Text in German"),
            "email_pending_open_subject_en": _("Email Pending Open Subject in English"),
            "email_pending_open_txt_en": _("Email Pending Open Text in English")
        }


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
