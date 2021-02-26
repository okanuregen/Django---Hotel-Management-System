from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User

from datetime import datetime, date, timedelta
import random
# Create your views here.
from accounts.models import *
from room.models import *
from hotel.models import *
from .forms import *


@login_required(login_url='login')
def home(request):
    role = str(request.user.groups.all()[0])
    if role != "guest":
        return redirect("employee-profile", pk=request.user.id)
    else:
        return redirect("guest-profile", pk=request.user.id)


@login_required(login_url='login')
def events(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    events = Event.objects.all()

    # eventAttendees = EventAttendees.objects.filter(guest = request.user.guest, event = )

    attendedEvents = None
    if role == 'guest':
        attendedEvents = EventAttendees.objects.filter(
            guest=request.user.guest)

    if request.method == "POST":
        if "filter" in request.POST:
            if (request.POST.get("type") != ""):
                events = events.filter(
                    eventType__contains=request.POST.get("type"))

            if (request.POST.get("name") != ""):
                events = events.filter(
                    location__contains=request.POST.get("location"))

            if (request.POST.get("fd") != ""):
                events = events.filter(
                    startDate__gte=request.POST.get("fd"))

            if (request.POST.get("ed") != ""):
                events = events.filter(
                    endDate__lte=request.POST.get("ed"))

            context = {
                "role": role,
                "events": events,
                "type": request.POST.get("type"),
                "location": request.POST.get("location"),
                "fd": request.POST.get("fd"),
                "ed": request.POST.get("ed")
            }
            return render(request, path + "events.html", context)

        if 'Save' in request.POST:
            n = request.POST.get('id-text')
            temp = EventAttendees.objects.get(id=request.POST.get('id-2'))
            temp.numberOfDependees = n
            temp.save()

        if 'attend' in request.POST:  # attend button clicked
            attendedEvents = EventAttendees.objects.filter(
                guest=request.user.guest)
            tempEvent = events.get(id=request.POST.get('id'))
            # print("query set**",attendedEvents)
            # print("**object***",tempEvent)
            # print(tempEvent in attendedEvents)
            check = False
            for t in attendedEvents:
                if t.event.id == tempEvent.id:
                    check = True
                    break
            if not check:  # event not in the query set
                a = EventAttendees(event=tempEvent, guest=request.user.guest)
                a.save()
                return redirect('events')  # refresh page

        elif 'remove' in request.POST:  # remove button clicked
            tempEvent = events.get(id=request.POST.get('id'))
            EventAttendees.objects.filter(
                event=tempEvent, guest=request.user.guest).delete()
            return redirect('events')  # refresh page

    context = {
        "role": role,
        'events': events,
        'attendedEvents': attendedEvents,
        "type": request.POST.get("type"),
        "location": request.POST.get("location"),
        "fd": request.POST.get("fd"),
        "ed": request.POST.get("ed")
    }
    return render(request, path + "events.html", context)


@login_required(login_url='login')
def createEvent(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    form = createEventForm()
    if request.method == "POST":
        form = createEventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('events')

    context = {
        'form': form,
        "role": role
    }
    return render(request, path + "createEvent.html", context)


@login_required(login_url='login')
def deleteEvent(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    event = Event.objects.get(id=pk)
    if request.method == "POST":
        event.delete()
        return redirect('events')

    context = {
        "role": role,
        'event': event

    }
    return render(request, path + "deleteEvent.html", context)


@ login_required(login_url='login')
def event_profile(request, id):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    tempEvent = Event.objects.get(id=id)
    attendees = EventAttendees.objects.filter(event=tempEvent)

    context = {
        "role": role,
        "attendees": attendees,
        "event": tempEvent
    }
    return render(request, path + "event-profile.html", context)


@ login_required(login_url='login')
def event_edit(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    event = Event.objects.get(id=pk)
    form1 = editEvent(instance=event)

    context = {
        "role": role,
        "event": event,
        "form": form1,
    }

    if request.method == "POST":
        form1 = editEvent(request.POST, instance=event)
        if form1.is_valid:
            form1.save()
            return redirect("events")

    return render(request, path + "event-edit.html", context)


@ login_required(login_url='login')
def announcements(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    announcements = Announcement.objects.all()
    context = {
        "role": role,
        'announcements': announcements
    }

    if request.method == "POST":
        if 'sendAnnouncement' in request.POST:  # send button clicked
            sender = request.user.employee

            announcement = Announcement(
                sender=sender, content=request.POST.get('textid'))

            announcement.save()
            return redirect('announcements')

        if "filter" in request.POST:
            if (request.POST.get("id") != ""):
                announcements = announcements.filter(
                    id__contains=request.POST.get("id"))

            if (request.POST.get("content") != ""):
                announcements = announcements.filter(
                    content__contains=request.POST.get("content"))

            if (request.POST.get("name") != ""):
                users = User.objects.filter(
                    Q(first_name__contains=request.POST.get("name")) | Q(last_name__contains=request.POST.get("name")))
                employees = Employee.objects.filter(user__in=users)
                announcements = announcements.filter(sender__in=employees)

            if (request.POST.get("date") != ""):
                announcements = announcements.filter(
                    date=request.POST.get("date"))

        context = {
            "role": role,
            'announcements': announcements,
            "id": request.POST.get("id"),
            "name": request.POST.get("name"),
            "content": request.POST.get("content"),
            "date": request.POST.get("date")
        }
        return render(request, path + "announcements.html", context)

    return render(request, path + "announcements.html", context)


@login_required(login_url='login')
def deleteAnnouncement(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    announcement = Announcement.objects.get(id=pk)
    if request.method == "POST":
        announcement.delete()
        return redirect('announcements')

    context = {
        "role": role,
        'announcement': announcement

    }
    return render(request, path + "deleteAnnouncement.html", context)


@ login_required(login_url='login')
def storage(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    storage = Storage.objects.all()
    context = {
        "role": role,
        'storage': storage
    }
    if request.method == "POST":
        if 'add' in request.POST:
            item = Storage(itemName=request.POST.get("itemName"), itemType=request.POST.get(
                "itemType"), quantitiy=request.POST.get("quantitiy"))
            item.save()
            storage = Storage.objects.all()

        elif 'save' in request.POST:
            id = request.POST.get("id")
            storages = Storage.objects.get(id=id)
            storages.quantitiy = request.POST.get("quantitiy")
            storages.save()

        if "filter" in request.POST:
            if (request.POST.get("id") != ""):
                storage = storage.filter(
                    id__contains=request.POST.get("id"))

            if (request.POST.get("name") != ""):
                storage = storage.filter(
                    itemName__contains=request.POST.get("name"))

            if (request.POST.get("type") != ""):
                storage = storage.filter(
                    itemType__contains=request.POST.get("type"))

        context = {
            "role": role,
            "storage": storage,
            "id": request.POST.get("id"),
            "name": request.POST.get("name"),
            "type": request.POST.get("type"),
            "q": request.POST.get("q"),

        }
        return render(request, path + "storage.html", context)

    return render(request, path + "storage.html", context)


@login_required(login_url='login')
def deleteStorage(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    storage = Storage.objects.get(id=pk)
    if request.method == "POST":
        storage.delete()
        return redirect('storage')

    context = {
        "role": role,
        'storage': storage

    }
    return render(request, path + "deleteStorage.html", context)


@login_required(login_url='login')
def food_menu(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    print(request.POST)
    if request.method == "POST":
        if 'add' in request.POST:
            foodmenu = FoodMenu(menuItems=request.POST.get("menuItems"), startDate=request.POST.get(
                "startDate"), endDate=request.POST.get("endDate"))
            foodmenu.save()

    food_menu = FoodMenu.objects.all()
    context = {
        "role": role,
        'food_menu': food_menu
    }
    return render(request, path + "food-menu.html", context)


@login_required(login_url='login')
def deleteFoodMenu(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    food_menu = FoodMenu.objects.get(pk=pk)
    if request.method == "POST":
        food_menu.delete()
        return redirect('food-menu')

    context = {
        "role": role,
        'food_menu': food_menu

    }
    return render(request, path + "deleteFoodMenu.html", context)


@login_required(login_url='login')
def food_menu_edit(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    print(request.POST)
    food_menu = FoodMenu.objects.get(pk=pk)
    form1 = editFoodMenu(request.POST, instance=food_menu)
    if request.method == "POST":
        if form1.is_valid():
            form1.save()
            return redirect("food-menu")

    context = {
        "role": role,
        'food_menu': food_menu
    }
    return render(request, path + "food-menu-edit.html", context)


@ login_required(login_url='login')
def error(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    context = {
        "role": role
    }
    return render(request, path + "error.html", context)


@login_required(login_url='login')
def payment(request):
    role = str(request.user.groups.all()[0])
    path = role

    # create random string:
    # generating the random code to be sent to the email
    import random
    import string
    code = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase)
                   for _ in range(10))

    context = {
        "role": role,
        "code": code

    }

    def send(request, receiver, code):
        subject = "Payment Verification"
        text = """ 
            Dear {guestName},
            Please Copy Paste This Code in the verification Window:

            {code}

            Please ignore this email, if you didn't initiate this transaction!
        """
        # placing the code and user name in the email bogy text
        email_text = text.format(
            guestName=receiver.user.first_name + " " + receiver.user.last_name, code=code)

        # seting up the email
        message_email = 'hms@support.com'
        message = email_text
        receiver_name = receiver.user.first_name + " " + receiver.user.last_name

        # send email
        send_mail(
            receiver_name + " " + subject,  # subject
            message,  # message
            message_email,  # from email
            [receiver.user.email],  # to email
            fail_silently=False,  # for user in users :
            # user.email
        )

        messages.success(
            request, 'Verification email Was Successfully Sent')

        # do something ???
        return render(request, path + "/verify.html", context)
    if role == "guest":
        send(request, request.user.guest, code)
    elif role == "receptionist":
        send(request, Booking.objects.all().last().guest, code)

    return render(request, path + "/payment.html", context)


@login_required(login_url='login')
def verify(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    if request.method == "POST":
        tempCode = request.POST.get("tempCode")
        if "verify" in request.POST:
            realCode = request.POST.get("realCode")

            if realCode == tempCode:
                messages.success(request, "Successful Booking")
            else:
                Booking.objects.all().last().delete()
                messages.warning(request, "Invalid Code")

            return redirect("rooms")
    context = {
        "role": role,
        "code": tempCode

    }
    return render(request, path + "verify.html", context)
