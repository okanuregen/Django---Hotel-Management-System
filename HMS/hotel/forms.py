from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from .models import *


class editFoodMenu(ModelForm):
    class Meta:
        model = FoodMenu
        fields = ["menuItems", "startDate", "endDate"]


class editEvent(ModelForm):
    class Meta:
        model = Event
        fields = ["eventType", "location",
                  "startDate", "endDate", "explanation"]


class createEventForm(ModelForm):
    class Meta:
        model = Event
        fields = ["eventType", "location",
                  "startDate", "endDate", "explanation"]


class createAnnouncementForm(ModelForm):
    class Meta:
        model = Announcement
        fields = '__all__'


class createItem(ModelForm):
    class Meta:
        model = Storage
        fields = ["itemName", "itemType", "quantitiy"]
