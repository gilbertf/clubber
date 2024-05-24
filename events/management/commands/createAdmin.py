from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model

from events.models import Person

UserModel = get_user_model()
class Command(BaseCommand):
    def handle(self, *args, **options):
        numUsers = Person.objects.count()
        if numUsers == 0:
            print("Creation of admin account")
            user = input("Admin username:")
            password = input("Password:")
            mail = input("E-Mail Address:")
            
            user = UserModel.objects.create_user(user, password=password, email=mail)
            user.is_superuser = True
            user.is_staff = True
            user.email_notification_new_event = True
            user.email_notification_joined_event = True
            user.language = "de"
            user.save()
