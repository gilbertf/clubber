from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from datetime import datetime, timedelta
import pytz
from django.http import HttpResponseRedirect
import operator
from .models import Event, Typ, Joined, NameTxt, JoinedTxt
from .forms import EventForm, EmailNotificationsForm
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
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

class TypListView(ListView):
    model = Typ

class TypUpdateView(UserPassesTestMixin, UpdateView):
    model = Typ
    template_name = "events/typ_edit_form.html"
    fields = ["name", "url"]
    success_url = reverse_lazy("typ-list")
    def test_func(self):
        return self.request.user.is_superuser

class TypDeleteView(UserPassesTestMixin, DeleteView):
    model = Typ
    success_url = reverse_lazy("typ-list")
    def test_func(self):
        return self.request.user.is_superuser

class TypAddView(UserPassesTestMixin, CreateView):
    model = Typ
    template_name = "events/typ_add_form.html"
    fields = ["name", "url"]
    success_url = reverse_lazy("typ-list")
    def test_func(self):
        return self.request.user.is_superuser

def settings_email(request):
    if request.method == 'POST':
        settings_email_form = EmailNotificationsForm(request.POST, instance=request.user)
        if settings_email_form.is_valid():
            settings_email_form.save()
        return redirect('/')
    else:
        settings_email_form = EmailNotificationsForm(instance=request.user)
    return render(request, "settings_email.html", context={"settings_email_form":settings_email_form})

def addUserToEvent(user, event):
    if not user in event.participants.all(): #Verhindern das durch wiederholtes POST Doppeleinträge erzeugt werden
        if not event.is_full():
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

def advanceEvent(request, e):
        if request.user.is_staff:
            e.staff = True

        e.no_participants = e.is_empty()
        e.full = e.is_full()

        if request.user in e.participants.all():
            e.subs = True

        if request.user == e.organizer:
            e.orga = True

        if request.user.is_authenticated: #Wir brauchen diese Info um Anmeldung/Abmeldung Schalter ein/auszublenden
            e.auth = True

        e.num_participants = len(e.participants.all()) + len(e.participants_txt.all())
        e.freeSlots = e.max_participants - e.num_participants
        e.missing_participants = e.min_participants - e.num_participants

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

def sendMail(d, plain, html, subject, participants = None, newEvent = False, changeEvent = False, newEventIcs = None):
    text = get_template(plain)
    html = get_template(html)
    subject = get_template(subject)

    from_email = settings.DEFAULT_FROM_EMAIL

    if participants == None:
        participants = get_user_model().objects.all()

    for user in participants:
        if user.email != None and len(user.email) > 0:
            if (user.email_notification_new_event and newEvent) or (user.email_notification_joined_event  and changeEvent):
                d["user_id"] = user.id
                d["username"] = user.username
                translation.activate(user.language)
                html_r = html.render(d)
                text_r = text.render(d)
                subject_r = subject.render(d).strip()
                translation.deactivate()
                msg = EmailMultiAlternatives(subject_r, text_r, from_email, [user.email])
                msg.attach_alternative(html_r, "text/html")
                if newEventIcs != None:
                    msg.attach("event.ics", newEventIcs, "text/calendar")
                msg.send()

def sendMailNewEvent(date, start_time, end_time, typ, organizer, event_id):
    d = {
        'date' : date,
        "start_time" : start_time ,
        "end_time" : end_time,
        "typ" : typ,
        "event_id" : event_id,
    }

    cal = ics.Calendar()
    event = ics.Event()
    event.name = str(typ)
    dt = datetime(date.year, date.month, date.day, start_time.hour, start_time.minute, tzinfo=pytz.timezone("Europe/Berlin"))
    event.begin = dt
    dt = datetime(date.year, date.month, date.day, end_time.hour, end_time.minute, tzinfo=pytz.timezone("Europe/Berlin"))
    event.end = dt
    event.location = settings.EMAIL_EVENT_LOCATION
    event.url = settings.EMAIL_SITE_URL + "/event/" + str(event_id) + "/show"
    cal.events.add(event)

    sendMail(d, 'email_new_event.txt', 'email_new_event.html', 'email_new_event.subject', newEvent = True, newEventIcs = cal.serialize())

def sendMailCancleEvent(date, start_time, end_time, typ, organizer, event_id, participants):
    d = {
        'date' : date,
        "start_time" : start_time ,
        "end_time" : end_time,
        "typ" : typ,
        "event_id" : event_id,
    }
    sendMail(d, 'email_cancle_event.txt', 'email_cancle_event.html', 'email_cancle_event.subject', participants, changeEvent = True)

def sendMailUncancleEvent(date, start_time, end_time, typ, organizer, event_id, participants):
    d = {
        'date' : date,
        "start_time" : start_time ,
        "end_time" : end_time,
        "typ" : typ,
        "event_id" : event_id,
    }
    sendMail(d, 'email_uncancle_event.txt', 'email_uncancle_event.html', 'email_uncancle_event.subject', participants, changeEvent = True)

def sendMailWillOpenEvent(date, start_time, end_time, typ, organizer, event_id, participants):
    d = {
        'date' : date,
        "start_time" : start_time ,
        "end_time" : end_time,
        "typ" : typ,
        "event_id" : event_id,
    }
    sendMail(d, 'email_will_open_event.txt', 'email_will_open_event.html', 'email_will_open_event.subject', participants, changeEvent = True)
    
def sendMailWillNotOpenEvent(date, start_time, end_time, typ, organizer, event_id, participants):
    d = {
        'date' : date,
        "start_time" : start_time ,
        "end_time" : end_time,
        "typ" : typ,
        "event_id" : event_id,
    }
    sendMail(d, 'email_will_not_open_event.txt', 'email_will_not_open_event.html', 'email_will_not_open_event.subject', participants, changeEvent = True)

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
                event.save()
                return redirect('/')
        else:
            event_form = EventForm()
    else:
        event_form = EventForm()
    return render(request, "event_modify.html", context={"event_form":event_form, "event_id" : event_id})

def event_add(request):
    if not request.user.is_authenticated:
        return redirect("/login?next={request.path}")

    event_form = EventForm()
    if request.method == "POST":
        event_form = EventForm(request.POST)
        if event_form.is_valid():
            event = event_form.save()
            if settings.EMAIL_NOTIFICATION_ENABLE:
                sendMailNewEvent(event.date, event.start_time, event.end_time, event.typ, event.organizer, event.id)
            return redirect('/')

    context = dict()
    context["event_form"] = event_form
    if len(Typ.objects.all()) == 0:
        context["empty_type"] = True
    return render(request, "event_add.html", context)

def settings_users_delete(request, user_id):
    if request.user.is_staff:
        user = get_user_model().objects.filter(id=user_id).get()
        if user != request.user:
            user.delete()
            return HttpResponse(status=200)

def settings_users(request):
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

    return render(request, "settings_users.html", {"users": get_user_model().objects.all()})

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

def event_participant_delete(request, event_id, participant_id):
    event = Event.objects.filter(id=event_id).get()
    if request.user.is_staff:
        user = get_user_model().objects.filter(id=participant_id).get()
        removeUserFromEvent(user, event)
    advanceEvent(request, event)
    return render(request, 'event.html', {'event': event})

def event_participant_txt_delete(request, event_id, participant_txt_id):
    event = Event.objects.filter(id=event_id).get()
    if request.user.is_staff:
        t = event.participants_txt.filter(id=participant_txt_id).delete()
        event.save()
    advanceEvent(request, event)
    return render(request, 'event.html', {'event': event})

def event_participant_txt_add(request, event_id):
    name = request.POST.get("username")
    event = Event.objects.filter(id=event_id).get()
    checkRet = username_check(name, event)
    if checkRet[0]:
        n = NameTxt(txt=name)
        n.save()
        if not event.is_full():
            jt = JoinedTxt(name_txt = n, event = event, date=datetime.now())
            jt.save()
    else:
        messages.error(request, checkRet[1])
    advanceEvent(request, event)
    return render(request, 'event.html', {'event': event})

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

def event_participant_txt_modify(request, event_id, participant_txt_id):
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
        
def event_delete(request, event_id):
    event = Event.objects.filter(id=event_id).get()
    advanceEvent(request, event)
    if request.user.is_staff and event.cancled == True and event.is_empty():
        event.delete()
        r = HttpResponse(status=200)
        r["HX-Refresh"] = "true"
        return r
    return render(request, 'event.html', {'event': event})

def event_follow_set(request, event_id):
    event = Event.objects.filter(id=event_id).get()
    addUserToEvent(request.user, event)
    advanceEvent(request, event)
    return render(request, 'event.html', {'event': event})

def event_follow_unset(request, event_id):
    event = Event.objects.filter(id=event_id).get()
    removeUserFromEvent(request.user, event)
    advanceEvent(request, event)
    return render(request, 'event.html', {'event': event})

def event_cancle_set(request, event_id):
    event = Event.objects.filter(id=event_id).get()
    advanceEvent(request, event)
    if request.user.is_staff:
        event.cancled = True
        event.save()
        if settings.EMAIL_NOTIFICATION_ENABLE:
            persons = event.participants.all() | get_user_model().objects.filter(id=event.organizer.id)
            sendMailCancleEvent(event.date, event.start_time, event.end_time, event.typ, event.organizer, event.id, persons)
    return render(request, 'event.html', {'event': event})

def event_cancle_unset(request, event_id):
    event = Event.objects.filter(id=event_id).get()
    advanceEvent(request, event)
    if request.user.is_staff:
        event.cancled = False
        event.save()
        if settings.EMAIL_NOTIFICATION_ENABLE:
            persons = event.participants.all() | get_user_model().objects.filter(id=event.organizer.id)
            sendMailUncancleEvent(event.date, event.start_time, event.end_time, event.typ, event.organizer, event.id, persons)
    return render(request, 'event.html', {'event': event})

def event_open_set(request, event_id):
    if request.user.is_staff:
        event = Event.objects.filter(id=event_id).get()
        event.organizer = request.user
        removeUserFromEvent(request.user, event)
        event.cancled = False
        event.save()
        advanceEvent(request, event)
        if settings.EMAIL_NOTIFICATION_ENABLE:
            persons = event.participants.all() | get_user_model().objects.filter(id=event.organizer.id)
            sendMailWillOpenEvent(event.date, event.start_time, event.end_time, event.typ, event.organizer, event.id, persons)
    return render(request, 'event.html', {'event': event})

def event_open_unset(request, event_id):
    if request.user.is_staff:
        event = Event.objects.filter(id=event_id).get()
        event.organizer = None
        event.save()
        advanceEvent(request, event)
        if settings.EMAIL_NOTIFICATION_ENABLE:
            persons = event.participants.all() | get_user_model().objects.filter(id=event.organizer.id)
            sendMailWillNotOpenEvent(event.date, event.start_time, event.end_time, event.typ, event.organizer, event.id, persons)
    return render(request, 'event.html', {'event': event})
