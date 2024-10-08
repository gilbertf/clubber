from django.contrib.auth import get_user_model
from django.utils import translation
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import Template, Context
from django.utils.html import strip_tags
from .model_configuration import Configuration
from django.utils.translation import gettext as _

class MailConf:
    def NewEvent():
        configuration = Configuration.get_solo()
        return Mail(
            Template(configuration.email_new_event_subject_de),
            Template(configuration.email_new_event_subject_en),
            Template(configuration.email_new_event_txt_de),
            Template(configuration.email_new_event_txt_en),
            allUsers = True,
            newEventNotification = True
        )
        
    def EventFullyBooked():
        configuration = Configuration.get_solo()
        return Mail(
            Template(configuration.email_fully_booked_subject_de),
            Template(configuration.email_fully_booked_subject_en),
            Template(configuration.email_fully_booked_txt_de),
            Template(configuration.email_fully_booked_txt_en),
            allOrganizers = True,
            modifyEventNotification = True
        )
        
    def EventSufficientParticipantsMissingOrganizer():
        configuration = Configuration.get_solo()
        return Mail(
            Template(configuration.email_sufficient_participants_missing_organizer_subject_de),
            Template(configuration.email_sufficient_participants_missing_organizer_subject_en),
            Template(configuration.email_sufficient_participants_missing_organizer_txt_de),
            Template(configuration.email_sufficient_participants_missing_organizer_txt_en),
            allOrganizers = True,
            modifyEventNotification = True
        )
    
    def EventCancle():
        configuration = Configuration.get_solo()
        return Mail(
            Template(configuration.email_cancle_subject_de),
            Template(configuration.email_cancle_subject_en),
            Template(configuration.email_cancle_txt_de),
            Template(configuration.email_cancle_txt_en),
            eventParticipants = True,
            eventOrganizer = True,
            modifyEventNotification = True
        )
    
    def EventConfirmedOpen():
        configuration = Configuration.get_solo()
        return Mail(
            Template(configuration.email_confirm_open_subject_de),
            Template(configuration.email_confirm_open_subject_en),
            Template(configuration.email_confirm_open_txt_de),
            Template(configuration.email_confirm_open_txt_en),
            eventParticipants = True,
            eventOrganizer = True,
            modifyEventNotification = True
        )
    
    def EventPendingOpen():
        configuration = Configuration.get_solo()
        return Mail(
            Template(configuration.email_pending_open_subject_de),
            Template(configuration.email_pending_open_subject_en),
            Template(configuration.email_pending_open_txt_de),
            Template(configuration.email_pending_open_txt_en),
            eventParticipants = True,
            eventOrganizer = True,
            modifyEventNotification = True
        )

class Mail:
    def __init__(self, subject_de, subject_en, txt_de, txt_en, allUsers = False, allOrganizers = False, eventParticipants = False, eventOrganizer = False, newEventNotification = False, modifyEventNotification = False):
        self.subject_de = subject_de
        self.subject_en = subject_en
        self.txt_de = txt_de
        self.txt_en = txt_en
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

    if (mail.txt_de == "" and mail.txt_en == "") or (mail.subject_de == "" and mail.subject_en == ""):
        print("Skipping send mail due to missing mail txt")
        return
       
    d = Context({
        'date' : event.date,
        "start_time" : event.start_time,
        "end_time" : event.end_time,
        "typ" : event.typ,
        "event_id" : event.id,
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

    from_email = settings.DEFAULT_FROM_EMAIL

    persons = mail.persons(event)

    mailMsgs = []
    for user in persons:
        if not (user.email_notification_new_event and mail.newEventNotification) and not (user.email_notification_joined_event and mail.modifyEventNotification):
            continue
        if user.email != None and len(user.email) > 0:
            translation.activate(user.language)
            
            d["user_id"] = user.id
            d["username"] = user.username
            d["joint_event_url"] = settings.EMAIL_SITE_URL + "/join/" + str(user.id) + "/" + str(event.id)
            d["show_event_url"] = settings.EMAIL_SITE_URL + "/event/" + str(event.id) + "/show"
            d["date_weekday"] = _(event.date.strftime('%A'))

            if user.language == "en":
                if mail.txt_en != "":
                    html_r = mail.txt_en.render(d)
                elif mail.txt_de != "":
                    html_r = mail.txt_de.render(d)

                if mail.subject_en != "":
                    subject_r = mail.subject_en.render(d).strip()
                elif mail.subject_de != "":
                    subject_r = mail.subject_de.render(d).strip()

            if user.language == "de":
                if mail.txt_de != "":
                    html_r = mail.txt_de.render(d)
                elif mail.txt_en != "":
                    html_r = mail.txt_en.render(d)   

                if mail.subject_de != "":
                    subject_r = mail.subject_de.render(d).strip()
                elif mail.subject_en != "":
                    subject_r = mail.subject_en.render(d).strip()  

            translation.deactivate()

            txt_r = strip_tags(html_r)
            mailMsg = EmailMultiAlternatives(subject_r, txt_r, from_email, [user.email])
            mailMsg.attach_alternative(html_r, "text/html")

            if newEventIcs != None:
                mailMsg.attach("event.ics", newEventIcs, "text/calendar")
            mailMsgs.append(mailMsg)
            print(txt_r)

    if len(mailMsgs) > 0:
        try:
            connection = mailMsg.get_connection()
            connection.send_messages(mailMsgs)
        except Exception as e:
            print("Error sending mail", e)
