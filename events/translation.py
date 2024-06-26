from modeltranslation.translator import translator, TranslationOptions
from .models import Typ, Location, Configuration
from django.utils.translation import gettext as _

class TypTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
    required_languages = {'de': ('name',)}
translator.register(Typ, TypTranslationOptions)

class LocationTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = {'de': ('name',)}
translator.register(Location, LocationTranslationOptions)

class ConfigurationTranslationOptions(TranslationOptions):
    fields = (
        'impressum', 
        'email_confirm_open_txt', 
        'email_confirm_open_subject',
        'email_new_event_subject', 
        'email_new_event_txt', 
        'email_fully_booked_subject', 
        'email_fully_booked_txt',
        'email_sufficient_participants_missing_organizer_subject', 
        'email_sufficient_participants_missing_organizer_txt',
        'email_cancle_subject', 
        'email_cancle_txt', 
        'email_pending_open_subject', 
        'email_pending_open_txt'
    )
translator.register(Configuration, ConfigurationTranslationOptions)
