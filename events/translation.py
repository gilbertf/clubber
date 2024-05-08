from modeltranslation.translator import translator, TranslationOptions
from .models import Typ, Event

class TypTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
    required_languages = ('en', 'de')

class EventTranslationOptions(TranslationOptions):
    fields = ('typ')
    required_languages = ('en', 'de')
    
translator.register(Typ, TypTranslationOptions)
#translator.register(Event, EventTranslationOptions)