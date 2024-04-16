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


class EmailNotificationsForm(forms.ModelForm):
    class Meta:
        model = Person
        if settings.EMAIL_NOTIFICATION_ENABLE:
            fields = [ "email", "email_notification_new_event", "email_notification_joined_event" ]
        else:
            fields = [ "email" ]
        labels = { "email": "E-Mail-Adresse" }

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
            #if self.instance and self.instance.pk:
            self.fields['organizer'].queryset = get_user_model().objects.filter(is_staff=True)
    
    def clean(self):
        if self.cleaned_data["date"] < datetime.now().date():
            raise ValidationError("The date cannot be in the past!")

        if self.cleaned_data["start_time"] >= self.cleaned_data["end_time"]:
            raise ValidationError("Es wird erwartet, dass die Endzeit später als die Startzeit liegt.")

        #Zeitliche Überschneidung von Veranstaltungen verhindern
        if not settings.EVENT_TIME_OVERLAP_ALLOW:
            sameTime = False
            for e in Event.objects.all():
                if hasattr(self, "event_id") and self.event_id == e.id:
                    continue
                if self.cleaned_data["date"] == e.date: #Gleicher Tag
                    if self.cleaned_data["start_time"] >= e.end_time:
                        sameTime = False
                    elif e.start_time >= self.cleaned_data["end_time"]:
                        sameTime = False
                    else:
                        sameTime = True
            if sameTime:
                raise ValidationError("Zeitliche Überschneidung zweier Treffen ist nicht zulässig")

        return self.cleaned_data
