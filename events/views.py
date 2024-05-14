from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from datetime import datetime, timedelta
import pytz
from django.http import HttpResponseRedirect
import operator
from .models import Event, Typ, Joined, NameTxt, JoinedTxt, Person
from .forms import EventForm, TypForm, EmailNotificationsForm
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import logout
from enum import Enum
import ics
from django.views.generic import ListView
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.utils import translation
from datetime import date
from django.conf import settings
from .email import sendMail, Mail

class TypListView(ListView):
    model = Typ
    template_name = "typ_list.html"

class TypAddView(UserPassesTestMixin, CreateView):
    model = Typ
    template_name = "typ_add.html"
    form_class = TypForm
    success_url = reverse_lazy("typ_list")
    def test_func(self):
        return self.request.user.is_superuser
    
class TypModifyView(UserPassesTestMixin, UpdateView):
    model = Typ
    template_name = "typ_modify.html"
    form_class = TypForm
    
    success_url = reverse_lazy("typ_list")
    def test_func(self):
        return self.request.user.is_superuser

class TypDeleteView(UserPassesTestMixin, DeleteView):
    model = Typ
    success_url = reverse_lazy("typ_list")
    def test_func(self):
        return self.request.user.is_superuser

class SettingsEmailView(UpdateView):
    model = Person
    template_name = "email.html"
    success_url = reverse_lazy("events_list")
    form_class = EmailNotificationsForm

    def get_object(self):
        model_instance = Person.objects.get(pk=self.request.user.id)
        return model_instance

def addUserToEvent(user, event):
    if not user in event.participants.all(): #Verhindern das durch wiederholtes POST Doppeleinträge erzeugt werden
        if not event.fullyBooked:
            j = Joined(user = user, event = event, date=datetime.now())
            j.save()

def removeUserFromEvent(user, event):
    if user in event.participants.all():
        event.participants.remove(user)
        event.save()
    
def event_join(request, user_id, event_id):
    user = get_user_model().objects.filter(id = user_id).get()
    if request.user == user:
        event = Event.objects.filter(id = event_id).get()
        addUserToEvent(user, event)
    else:
        logout(request)
        return redirect("/login/" + str(user_id) + "?next=" + request.path)
    return HttpResponseRedirect('/event/' + str(event_id) + "/show")

def advanceEvent(request, event):
        if request.user.is_staff:
            event.userIsStaff = True

        if request.user in event.participants.all():
            event.userIsSubscribed = True

        if request.user == event.organizer:
            event.userIsOrganizer = True

        if request.user.is_authenticated: #Wir brauchen diese Info um Anmeldung/Abmeldung Schalter ein/auszublenden
            event.auth = True

        if request.user.is_staff:
            event.nextDays = [event.date + timedelta(days=i+1) for i in range(7) ]


def prepare_event_list(request):
    event_list = Event.objects.filter(date__gte=datetime.now() + timedelta(days=0)).order_by('date') #Hide all events that started more than 1 day ago -> maybe delete or "archive" as statistical data without names in the future
    #In allen veranstaltungen markieren, ob der Nutzer bereits angemeldet ist und ob es sich um einen Admin handelt
    structured_el = list()
    l = None
    for e in event_list:
        advanceEvent(request, e)

        e.daysFuture = (e.date - date.today()).days

        if l == None:
            l = list() #Alle Elemente eines Tages
            l.append(e)
        else:
            if l[0].date != e.date: #Mit neuem Tag beginnen
                l.sort(key=operator.attrgetter('start_time'))
                structured_el.append(l) #Alte Liste sortieren und wegspeichern
                l = list()
            l.append(e)
    #Die neueste List sortieren und webspeichern
    if l != None:
        l.sort(key=operator.attrgetter('start_time'))
        structured_el.append(l) #Alte Liste sortieren und wegspeichern

    return structured_el

from django.db.models.query import QuerySet


def makeIcsForEvent(event):
    cal = ics.Calendar()
    calEvent = ics.Event()
    calEvent.name = str(event.typ)
    dt = datetime(event.date.year, event.date.month, event.date.day, event.start_time.hour, event.start_time.minute, tzinfo=pytz.timezone("Europe/Berlin"))
    calEvent.begin = dt
    dt = datetime(event.date.year, event.date.month, event.date.day, event.end_time.hour, event.end_time.minute, tzinfo=pytz.timezone("Europe/Berlin"))
    calEvent.end = dt
    calEvent.location = settings.EMAIL_EVENT_LOCATION
    calEvent.url = settings.EMAIL_SITE_URL + "/event/" + str(event.id) + "/show"
    cal.events.add(calEvent)
    return cal.serialize()


def event_modify(request):
    if not request.user.is_authenticated:
        return redirect("/login?next={request.path}")

    event_id = -1
    if request.method == 'POST':
        data = request.POST
        if "modify" in data:
            event_id = data.get("modify")
            event = Event.objects.filter(id=event_id).get()
            event_form = EventForm(instance=event)
        elif "modify_done" in data:
            event_id = data.get("modify_done")
            event = Event.objects.filter(id=event_id).get()
            event_form = EventForm(request.POST, instance=event)
            event_form.event_id = int(event_id) #Bei der Validierung soll der eigene Eintrag nicht berücksichtigt werden, sonst fehlschlag da Zeitüberschreitung
            if event_form.is_valid():
                event = event_form.save()
                removeUserFromEvent(request.user, event)
                return redirect('/')
        else:
            event_form = EventForm()
    else:
        event_form = EventForm()
    return render(request, "event_modify.html", context={"event_form":event_form, "event_id" : event_id})

def event_add(request): #eventFlow c5
    if not request.user.is_authenticated:
        return redirect("/login?next={request.path}")

    event_form = EventForm()
    if request.method == "POST":
        event_form = EventForm(request.POST)
        if event_form.is_valid():
            event = event_form.save()
            sendMailNewEvent(event)
            return redirect('/')

    context = dict()
    context["event_form"] = event_form
    if len(Typ.objects.all()) == 0:
        context["empty_type"] = True
    return render(request, "event_add.html", context)

def user_delete(request, user_id):
    if request.user.is_staff:
        user = get_user_model().objects.filter(id=user_id).get()
        if user != request.user:
            user.delete()
            return HttpResponse(status=200)

def user_list(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("/login?next={request.path}")

    if request.method == "POST":
        data = request.POST

        if not "admin-events" in data:
            i = data["user_id"]
            u = get_user_model().objects.filter(id=i).get()
            if not u.is_superuser:
                u.is_staff = False
                u.save()

        if "admin-events" in data:
            i = data["user_id"]
            u = get_user_model().objects.filter(id=i).get()
            u.is_staff = True
            u.save()

        if "admin-users" in data:
            i = data["user_id"]
            u = get_user_model().objects.filter(id=i).get()
            u.is_superuser = True
            u.is_staff = True
            u.save()

        if not "admin-users" in data:
            i = data["user_id"]
            u = get_user_model().objects.filter(id=i).get()
            if u != request.user:
                u.is_superuser = False
                u.save()

    return render(request, "user_list.html", {"users": get_user_model().objects.all()})

def events_list(request, event_id = None):
    context = dict()
    events = prepare_event_list(request)

    for events_of_day in events:
        for event in events_of_day:
          if event.id == event_id:
              event.expand = True
          else:
              event.expand = False

    if event_id == None: #Wenn kein spezielles Event angefragt wird, dann das erste ausklappen
        if len(events) > 0:
            events_of_day = events[0]
            if len(events_of_day) > 0:
                event = events_of_day[0]
                event.expand = True
    
    context["event_list"] = events
    return render(request, "events_list.html", context)

def username_check(name, event):
    if len(name) > 0 and len(name) <= 20: #Max. Feldlänge sicherstellen, dann: Sicherstellen das niemand mit gleichem Namen bereits eingetragen ist
        others = event.participants.filter(username__iexact=name).count()
        others_txt = event.participants_txt.filter(txt__iexact=name).count()
        if others == 0 and others_txt == 0:
            return True, ""
        else:
            return False, name + _(" is already registered")
    else:
            if len(name) == 0:
                return False, _("You are required to enter a name")
            else:
                return False, _("Exceeding max. length")

def eventParticipantTxtModify(request, event_id, participant_txt_id):
    if request.user.is_staff:
        event = Event.objects.filter(id=event_id).get()
        advanceEvent(request, event)
        name = request.POST.get("txt")
        participant_txt = event.participants_txt.filter(id=participant_txt_id).get()
        
        checkRet = username_check(name, event)
        if checkRet[0]:
            participant_txt.txt = name
            participant_txt.save()
        else:
            messages.error(request, checkRet[1])
    return render(request, 'event.html', {'event': event})
        
def sendMailNewEvent(event):
    if settings.EMAIL_NOTIFICATION_ENABLE:
                if event.sufficientParticipants and event.organizer == None:
                    sendMail(event, Mail.EventSufficientParticipantsMissingOrganizer) #eventFlow m3
                if event.fullyBooked:
                    sendMail(event, Mail.EventFullyBooked) #eventFlow m6
                sendMail(event, Mail.NewEvent, newEventIcs = makeIcsForEvent(event)) #eventFlow m5

def eventReplicate(request, event_id):
    if not request.user.is_authenticated:
        return redirect("/login?next={request.path}")
    
    if request.user.is_staff:
        event = Event.objects.filter(id=event_id).get()
        inDays = int(request.GET.get("inDays"))
        if inDays > 0 and inDays < 8 and event != None:
            event.pk = None #make as new object by deleting id
            event.organizer = None
            event.cancled = False
            event.date += timedelta(days=inDays)
            event.save()
            sendMailNewEvent(event)

    return redirect('/')

def eventDelete(request, event_id): #eventFlow c7
    event = Event.objects.filter(id=event_id).get()
    advanceEvent(request, event)
    if request.user.is_staff and event.cancled == True and event.noParticipants:
        event.delete()
        r = HttpResponse(status=200)
        r["HX-Refresh"] = "true"
        return r
    return render(request, 'event.html', {'event': event})

def eventParticipantAdd(request, event_id): #eventFlow c3
    event = Event.objects.filter(id=event_id).get()
    preSufficientParticipants = event.sufficientParticipants

    addUserToEvent(request.user, event)

    if not preSufficientParticipants and event.sufficientParticipants and event.organizer == None:
        sendMail(event, Mail.EventSufficientParticipantsMissingOrganizer) #eventFlow m3
    if not preSufficientParticipants and event.sufficientParticipants and event.organizer != None:
        sendMail(event, Mail.EventConfirmedOpen) #eventFlow m1
    if event.fullyBooked:
        sendMail(event, Mail.FullyBooked) #eventFlow m6

    advanceEvent(request, event)
    return render(request, 'event.html', {'event': event})

def eventParticipantTxtAdd(request, event_id):
    name = request.POST.get("username")
    event = Event.objects.filter(id=event_id).get()
    checkRet = username_check(name, event)
    if checkRet[0]:
        n = NameTxt(txt=name)
        n.save()
        if not event.fullyBooked:
            jt = JoinedTxt(name_txt = n, event = event, date=datetime.now())
            jt.save()
    else:
        messages.error(request, checkRet[1])

    advanceEvent(request, event)
    return render(request, 'event.html', {'event': event})

def eventParticipantRemoveBase(request, event_id, participant_id = None, participant_txt_id = None, admin = False): #eventFlow c4
    event = Event.objects.filter(id=event_id).get()
    preSufficientParticipants = event.sufficientParticipants
    
    if admin and participant_txt_id != None: #Admin removing some participant without auser ccount from event
        event.participants_txt.filter(id=participant_txt_id).delete()
        event.save()
    elif admin and request.user.is_staff and participant_id != None: #Admin removing some participant with user account from event
        user = get_user_model().objects.filter(id=participant_id).get()
        removeUserFromEvent(user, event)
    elif not admin and participant_id == None and participant_txt_id == None: #User with account removing himself from event
        event = Event.objects.filter(id=event_id).get()
        removeUserFromEvent(request.user, event)

    if preSufficientParticipants and not event.sufficientParticipants:
        sendMail(event, Mail.EventPendingOpen) #eventFlow m2

    advanceEvent(request, event)
    return render(request, 'event.html', {'event': event})

def eventParticipantRemove(request, event_id):
    return eventParticipantRemoveBase(request, event_id, admin = False)

def adminEventParticipantRemove(request, event_id, participant_id):
    return eventParticipantRemoveBase(request, event_id, participant_id = participant_id, admin = True)

def adminEventParticipantTxtRemove(request, event_id, participant_txt_id):
    return eventParticipantRemoveBase(request, event_id, participant_txt_id = participant_txt_id, admin = True)

def eventCancle(request, event_id): #eventFlow c6
    event = Event.objects.filter(id=event_id).get()
    advanceEvent(request, event)
    if request.user.is_staff:
        if settings.EMAIL_NOTIFICATION_ENABLE:
            sendMail(event, Mail.EventCancle) #eventFlow m4
        event.cancled = True
        event.organizer = None
        event.participants.clear()
        event.participants_txt.clear()
        event.save()
    return render(request, 'event.html', {'event': event})

def eventCancleUndo(request, event_id): #eventFlow c7
    event = Event.objects.filter(id=event_id).get()
    advanceEvent(request, event)
    if request.user.is_staff:
        event.cancled = False
        event.save()
        if settings.EMAIL_NOTIFICATION_ENABLE:
            if not event.sufficientParticipants:
                sendMail(event, Mail.EventPendingOpen) #eventFlow m2
            if event.sufficientParticipants and event.organizer == None:
                sendMail(event, Mail.EventSufficientParticipantsMissingOrganizer) #eventFlow m3
            if event.fullyBooked:
                sendMail(event, Mail.FullyBooked) #eventFlow m6

    return render(request, 'event.html', {'event': event})

def eventOrganizerSet(request, event_id): #eventFlow c1
    if request.user.is_staff:
        event = Event.objects.filter(id=event_id).get()
        event.organizer = request.user
        removeUserFromEvent(request.user, event)
        event.save()
        advanceEvent(request, event)
        if settings.EMAIL_NOTIFICATION_ENABLE:
            if event.sufficientParticipants:
                sendMail(event, Mail.EventConfirmedOpen) #eventFlow m1
    return render(request, 'event.html', {'event': event})

def eventOrganizerClear(request, event_id): #eventFlow c2
    if request.user.is_staff:
        event = Event.objects.filter(id=event_id).get()
        event.organizer = None
        event.save()
        advanceEvent(request, event)
        if settings.EMAIL_NOTIFICATION_ENABLE:
            if event.sufficientParticipants:
                sendMail(event, Mail.EventPendingOpen) #eventFlow m2
                sendMail(event, Mail.EventSufficientParticipantsMissingOrganizer) #eventFlow m3
    return render(request, 'event.html', {'event': event})
