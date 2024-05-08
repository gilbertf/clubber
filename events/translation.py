from modeltranslation.translator import translator, TranslationOptions
from .models import Typ, Event

class TypTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
    required_languages = ('de', 'en')
    #required_languages = {'de': ('name'), 'default': ('name')}

    
translator.register(Typ, TypTranslationOptions)
