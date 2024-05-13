from django.contrib.auth import get_user_model
from django.utils import translation
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

class Mail:
    def __init__(self, templateName, allUsers = False, allOrganizers = False, eventParticipants = False, eventOrganizer = False, newEventNotification = False, modifyEventNotification = False):
        self.templateName = templateName
        self.allUsers = allUsers
        self.allOrganizers = allOrganizers
        self.eventParticipants = eventParticipants
        self.eventOrganizer = eventOrganizer
        self.newEventNotification = newEventNotification
        self.modifyEventNotification = modifyEventNotification
    
    def mails(self, event):
        mails = get_user_model().objects.none()

        if self.allUsers:
            mails |= get_user_model().objects.all()
        if self.allOrganizers:
            mails |= get_user_model().objects.filter(is_staff=True)
        if self.eventParticipants:
            mails |= event.participants.all()
        if self.eventOrganizer and event.organizer != None:
            mails |= get_user_model().objects.filter(id=event.organizer.id)

        for user in mails:
            if not (user.email_notification_new_event and self.newEventNotification) and not (user.email_notification_joined_event and self.modifyEventNotification):
                mails.remove(user)

        return mails
 
Mail.NewEvent = Mail("email/new_event", allUsers = True, newEventNotification = True)
Mail.EventFullyBooked = Mail("email/event_fully_booked", allOrganizers = True, modifyEventNotification = True)
Mail.EventSufficientParticipantsMissingOrganizer = Mail("email/event_sufficient_participants_missing_organizer", allOrganizers = True, modifyEventNotification = True)
Mail.EventCancle = Mail("email/event_cancle", eventParticipants = True, eventOrganizer = True, modifyEventNotification = True)
Mail.EventConfirmedOpen = Mail("email/event_confirmed_open", eventParticipants = True, eventOrganizer = True, modifyEventNotification = True)
Mail.EventPendingOpen = Mail("email/event_pending_open", eventParticipants = True, eventOrganizer = True, modifyEventNotification = True)

def sendMail(event, mail, newEventIcs = None):
    d = {
        'date' : event.date,
        "start_time" : event.start_time ,
        "end_time" : event.end_time,
        "typ" : event.typ,
        "event_id" : event.id,
        "EMAIL_SITE_URL": settings.EMAIL_SITE_URL,
    }
    
    text = get_template(mail.templateName + ".txt")
    html = get_template(mail.templateName + ".html")
    subject = get_template(mail.templateName + ".subject")

    from_email = settings.DEFAULT_FROM_EMAIL

    mails = mail.mails(event)

    mailMsgs = []
    for user in mails:
        if user.email != None and len(user.email) > 0:
            d["user_id"] = user.id
            d["username"] = user.username

            translation.activate(user.language)
            html_r = html.render(d)
            text_r = text.render(d)
            subject_r = subject.render(d).strip()
            translation.deactivate()

            mailMsg = EmailMultiAlternatives(subject_r, text_r, from_email, [user.email])
            mailMsg.attach_alternative(html_r, "text/html")
            if newEventIcs != None:
                mailMsg.attach("event.ics", newEventIcs, "text/calendar")
            mailMsgs.append(mailMsg)

    if len(mailMsgs) > 0:
        connection = mailMsg.get_connection()
        connection.send_messages(mailMsgs)