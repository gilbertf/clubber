from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django_flatpickr.widgets import DatePickerInput, TimePickerInput, DateTimePickerInput
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django_flatpickr.schemas import FlatpickrOptions
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_url(url):
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValidationError(url + _(" does not start with http:// or https://"))

def validate_date_future(d):
    if d < datetime.now().date():
        raise ValidationError("Date is in the past")

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, email = None, email_notification_new_event = False, email_notification_joined_event = False):
        if email is None:
            mail_notification_joined_event = False
            email_notification_new_event = False           

        user = self.model(email=self.normalize_email(email), username=username, email_notification_joined_event = email_notification_joined_event, email_notification_new_event = email_notification_new_event)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, email = None, email_notification_new_event = False, email_notification_joined_event = False):
        user = self.create_user(username, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

class Person(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True, verbose_name=_("Username"))
    email = models.CharField(max_length=50)
    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, verbose_name=_("Language"))

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    email_notification_new_event = models.BooleanField(default=settings.EMAIL_NOTIFICATION_NEW_EVENT_DEFAULT, verbose_name=_("Notify on new events"))
    email_notification_joined_event = models.BooleanField(default=settings.EMAIL_NOTIFICATION_JOINED_EVENT_DEFAULT, verbose_name=_("Notify on changes to events you are registered"))
    
    objects = CustomUserManager()

class NameTxt(models.Model):
    txt = models.CharField(max_length=20)

class Typ(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name=_("Name"))
    url = models.CharField(max_length=100, default="", blank=True, verbose_name=_("Address (URL)"), validators=[validate_url])

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("typ-modify", kwargs={"pk": self.pk})

class Event(models.Model):
    typ = models.ForeignKey(Typ, on_delete=models.CASCADE, blank=False, verbose_name=_("Event type"), default=1)
    max_participants = models.IntegerField(default=settings.EVENT_PARTICIPANTS_MAX_DEFAULT, verbose_name=_("Maximum number of participants"), validators=[MaxValueValidator(settings.EVENT_PARTICIPANTS_MAX_LIMIT)])
    min_participants = models.IntegerField(default=settings.EVENT_PARTICIPANTS_MIN_DEFAULT, verbose_name=_("Minimal number of participants"), validators=[MinValueValidator(settings.EVENT_PARTICIPANTS_MIN_LIMIT)])
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='%(class)s_requests_created', null=True, verbose_name=_("Who is organizing?"), blank = True)
    date = models.DateField(verbose_name=_("Date"), default=timezone.now, validators=[validate_date_future])
    start_time = models.TimeField(verbose_name=_("Begin"), default=settings.EVENT_START_TIME_DEFAULT)
    end_time = models.TimeField(verbose_name=_("End"), default=settings.EVENT_END_TIME_DEFAULT)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Joined")
    participants_txt = models.ManyToManyField(NameTxt, through="JoinedTxt")
    cancled = models.BooleanField(default=False)

    def is_empty(self):
        if len(self.participants.all()) + len(self.participants_txt.all()) == 0:
            return 1
        return 0

    def num_participants(self):
        return len(self.participants.all()) + len(self.participants_txt.all())

    def is_full(self):
       return self.num_participants() >= self.max_participants #Max. Teilnehmeranzahl berücksichtigen

class Joined(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date = models.DateField()

class JoinedTxt(models.Model):
    name_txt = models.ForeignKey(NameTxt, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date = models.DateField()
