from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.events_list, name="events_list"),
    path("event/<int:event_id>/show", views.events_list, name="events_list_show"),
    path("event/add", views.event_add, name="event_add"),
    path("event/modify", views.event_modify, name="event_modify"),
    path("user/list", views.user_list, name="user_list"),
    path("user/<int:user_id>/delete", views.user_delete, name="user_delete"),
    path("email", views.settings_email, name="settings_email"),
    path("join/<int:user_id>/<int:event_id>", views.event_join, name="event_join"),
    path('impressum', TemplateView.as_view(template_name='impressum.html')),
    path("event/<int:event_id>/open/set", views.eventOrganizerSet, name="event_open_set"),
    path("event/<int:event_id>/open/unset", views.eventOrganizerClear, name="event_open_unset"),
    path("event/<int:event_id>/cancle", views.eventCancle, name="event_cancle_set"),
    path("event/<int:event_id>/cancle/unset", views.eventCancleUndo, name="event_cancle_unset"),
    path("event/<int:event_id>/follow/set", views.eventParticipantAdd, name="event_follow_set"),
    path("event/<int:event_id>/follow/unset", views.eventParticipantRemove, name="event_follow_unset"),
    path("event/<int:event_id>/delete", views.eventDelete, name="event_delete"),
    path("event/<int:event_id>/participant__txt/<int:participant_txt_id>/modify", views.eventParticipantTxtModify, name="event_participant_txt_modify"),
    path("event/<int:event_id>/participant_txt/<int:participant_txt_id>/delete", views.adminEventParticipantTxtRemove, name="event_participant_txt_delete"),
    path("event/<int:event_id>/participant_txt/add", views.eventParticipantTxtAdd, name="event_participant_txt_add"),
    path("event/<int:event_id>/participant/<int:participant_id>/delete", views.adminEventParticipantRemove, name="event_participant_delete"),
    path("typ/list", views.TypListView.as_view(), name="typ-list"),
    path("typ/<int:pk>/delete", views.TypDeleteView.as_view(), name="typ-delete"),
    path("typ/<int:pk>/modify", views.TypModifyView.as_view(), name="typ-modify"),
    path("typ/add", views.TypAddView.as_view(), name="typ_add"),
]
