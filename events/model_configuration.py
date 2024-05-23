from solo.models import SingletonModel
from django.db import models

class Configuration(SingletonModel):
    impressum = models.TextField()
    email_confirm_open_subject = models.CharField(max_length=250)
    email_confirm_open_txt = models.TextField()
    email_new_event_subject = models.CharField(max_length=250)
    email_new_event_txt = models.TextField()
    email_fully_booked_subject = models.CharField(max_length=250)
    email_fully_booked_txt = models.TextField()
    email_sufficient_participants_missing_organizer_subject = models.CharField(max_length=250)
    email_sufficient_participants_missing_organizer_txt = models.TextField()
    email_cancle_subject = models.CharField(max_length=250)
    email_cancle_txt = models.TextField()
    email_pending_open_subject = models.CharField(max_length=250)
    email_pending_open_txt = models.TextField()