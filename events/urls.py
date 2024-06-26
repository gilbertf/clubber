from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.events_list, name="events_list"),
    path("events/list/intern", views.events_list_intern, name="events_list_intern"),
    path("event/<int:event_id>/show", views.events_list, name="events_list_show"),
    path("event/add", views.event_add, name="event_add"),
    path("event/modify", views.event_modify, name="event_modify"),
    path("users/list", views.users_list, name="users_list"),
    path("user/<int:user_id>/delete", views.user_delete, name="user_delete"),
    path("user/settings", views.UserSettingsView.as_view(), name="user_settings"),
    path("join/<int:user_id>/<int:event_id>", views.event_join, name="event_join"),
    path("impressum", TemplateView.as_view(template_name='impressum.html'), name="impressum"),
    path("event/<int:event_id>/open/set", views.eventOrganizerSet, name="event_open_set"),
    path("event/<int:event_id>/open/unset", views.eventOrganizerClear, name="event_open_unset"),
    path("event/<int:event_id>/cancle", views.eventCancle, name="event_cancle_set"),
    path("event/<int:event_id>/cancle/unset", views.eventCancleUndo, name="event_cancle_unset"),
    path("event/<int:event_id>/follow/set", views.eventParticipantAdd, name="event_follow_set"),
    path("event/<int:event_id>/follow/unset", views.eventParticipantRemove, name="event_follow_unset"),
    path("event/<int:event_id>/delete", views.eventDelete, name="event_delete"),
    path("event/<int:event_id>/replicate", views.eventReplicate, name="event_replicate"),
    path("event/<int:event_id>/participant__txt/<int:participant_txt_id>/modify", views.eventParticipantTxtModify, name="event_participant_txt_modify"),
    path("event/<int:event_id>/participant_txt/<int:participant_txt_id>/delete", views.adminEventParticipantTxtRemove, name="event_participant_txt_delete"),
    path("event/<int:event_id>/participant_txt/add", views.eventParticipantTxtAdd, name="event_participant_txt_add"),
    path("event/<int:event_id>/participant/<int:participant_id>/delete", views.adminEventParticipantRemove, name="event_participant_delete"),
    path("typ/list", views.TypListView.as_view(), name="typ_list"),
    path("typ/<int:pk>/delete", views.TypDeleteView.as_view(), name="typ_delete"),
    path("typ/<int:pk>/modify", views.TypModifyView.as_view(), name="typ_modify"),
    path("typ/add", views.TypAddView.as_view(), name="typ_add"),
    path("location/list", views.LocationListView.as_view(), name="location_list"),
    path("location/<int:pk>/delete", views.LocationDeleteView.as_view(), name="location_delete"),
    path("location/<int:pk>/modify", views.LocationModifyView.as_view(), name="location_modify"),
    path("location/add", views.LocationAddView.as_view(), name="location_add"),
    path("configuration", views.ConfigurationModifyView.as_view(), name="configuration_modify"),

]
