from django.contrib.auth import get_user_model
from django.utils import translation
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import Template, Context
from django.utils.html import strip_tags
from .model_configuration import Configuration

class MailConf:
    def NewEvent():
        configuration = Configuration.get_solo()
        return Mail(
            Template(configuration.email_new_event_subject),
            Template(configuration.email_new_event_txt),
            allUsers = True,
            newEventNotification = True
        )
        
    def EventFullyBooked():
        onfiguration = Configuration.get_solo()
        return Mail(
            Template(configuration.email_fully_booked_subject),
            Template(configuration.email_fully_booked_txt),
            allOrganizers = True,
            modifyEventNotification = True
        )
        
    def EventSufficientParticipantsMissingOrganizer():
        configuration = Configuration.get_solo()
        return Mail(
            Template(configuration.email_sufficient_participants_missing_organizer_subject),
            Template(configuration.email_sufficient_participants_missing_organizer_txt),
            allOrganizers = True,
            modifyEventNotification = True
        )
    
    def EventCancle():
        configuration = Configuration.get_solo()
        return Mail(
            Template(configuration.email_cancle_subject),
            Template(configuration.email_cancle_txt),
            eventParticipants = True,
            eventOrganizer = True,
            modifyEventNotification = True
        )
    
    def EventConfirmedOpen():
        configuration = Configuration.get_solo()
        return Mail(
            Template(configuration.email_confirm_open_subject),
            Template(configuration.email_confirm_open_txt),
            eventParticipants = True,
            eventOrganizer = True,
            modifyEventNotification = True
        )
    
    def EventPendingOpen():
        configuration = Configuration.get_solo()
        return Mail(
            Template(configuration.email_pending_open_subject),
            Template(configuration.email_pending_open_txt),
            eventParticipants = True,
            eventOrganizer = True,
            modifyEventNotification = True
        )

class Mail:
    def __init__(self, subject, txt, allUsers = False, allOrganizers = False, eventParticipants = False, eventOrganizer = False, newEventNotification = False, modifyEventNotification = False):
        self.subject = subject
        self.txt = txt
        self.allUsers = allUsers
        self.allOrganizers = allOrganizers
        self.eventParticipants = eventParticipants
        self.eventOrganizer = eventOrganizer
        self.newEventNotification = newEventNotification
        self.modifyEventNotification = modifyEventNotification
    
    def persons(self, event):
        persons = get_user_model().objects.none()

        if self.allUsers:
            persons |= get_user_model().objects.all()
        if self.allOrganizers:
            persons |= get_user_model().objects.filter(is_staff=True)
        if self.eventParticipants:
            persons |= event.participants.all()
        if self.eventOrganizer and event.organizer != None:
            persons |= get_user_model().objects.filter(id=event.organizer.id)

        return persons
 
def sendMail(event, mail, newEventIcs = None):
    if mail == None:
        return

    if mail.txt == "" or mail.subject == "":
        print("Skipping send mail due to missing mail txt")
        return
       
    d = Context({
        'date' : event.date,
        "start_time" : event.start_time ,
        "end_time" : event.end_time,
        "typ" : event.typ,
        "event_id" : event.id,
        "EMAIL_SITE_URL": settings.EMAIL_SITE_URL,
    })

    s = "Sending mail to"
    if mail.allUsers:
        s += " allUsers"
    if mail.allOrganizers:
        s += " allOrganizers"
    if mail.eventParticipants:
        s += " eventParticipants"
    if mail.eventOrganizer:
        s += " eventOrganizer"
    print(s)

    from_email = settings.DEFAULT_FROM_EMAIL

    persons = mail.persons(event)

    mailMsgs = []
    for user in persons:
        if not (user.email_notification_new_event and mail.newEventNotification) and not (user.email_notification_joined_event and mail.modifyEventNotification):
            continue
        if user.email != None and len(user.email) > 0:
            d["user_id"] = user.id
            d["username"] = user.username

            translation.activate(user.language)
            html_r = mail.txt.render(d)
            subject_r = mail.subject.render(d).strip()
            translation.deactivate()

            txt_r = strip_tags(html_r)
            mailMsg = EmailMultiAlternatives(subject_r, txt_r, from_email, [user.email])
            mailMsg.attach_alternative(html_r, "text/html")

            if newEventIcs != None:
                mailMsg.attach("event.ics", newEventIcs, "text/calendar")
            mailMsgs.append(mailMsg)

    if len(mailMsgs) > 0:
        try:
            connection = mailMsg.get_connection()
            connection.send_messages(mailMsgs)
        except Exception as e:
            print("Error sending mail", e)
