from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .permissions import is_host
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm
from .forms import UserForm
import json

def loginView(request):
    page_name = 'Login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exists!')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'check username or password')
    context= {'page_name':page_name}
    return render(request, 'base/login_register.html', context)

def logoutView(request):
    logout(request) # clears the user session id, making it logout.
    return redirect('home')

def registerView(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Error occurred during registeration')
    context={'form': form}
    return render(request, 'base/login_register.html', context)

def home(request):
    # search handle
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)|
        Q(name__icontains=q)|
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    topics_count = topics.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {
        'rooms': rooms, 
        'topics': topics,
        'room_count': room_count,
        'topics_count': topics_count,
        'room_messages': room_messages
    }
    return render(request, 'base/home.html', context)

def userPorfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all() # rooms that user is present in
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        'user':user, 
        'rooms':rooms,
        'room_messages': room_messages,
        'topics':topics
    }
    return render(request, 'base/profile.html', context)

def room(request,pk):
    room = Room.objects.get(id=pk)
    
    participants = room.participants.all()
    # fetching all the messages that are specific to particular room.
    # below what we are doing is using message_set.all(),
    # we are fetching subquery to get all messages related to a particular room.
    room_messages = room.message_set.all()
    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room = room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room': room, 'room_messages':room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='user-login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host= request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')
    context = {"form": form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='user-login')
def upateRoom(request, pk):
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()
    form = RoomForm(instance=room)
    if not (is_host(request, room)):
        return HttpResponse('Action not allowed!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form':form, 'room_id': pk, 'topics':topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='user-login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if not (is_host(request, room)):
        return HttpResponse('Action not allowed!')
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/deletePage.html', {'obj':room})

@login_required(login_url='user-login')
def delete_user_message(request, pk):
    current_message = Message.objects.get(id=pk)
    if request.user != current_message.user:
        return HttpResponse("You'are not allowed")
    if request.method == "POST":
        current_message.delete()
        return redirect('home')
    return render(request, 'base/deletePage.html', {'obj': current_message})

@login_required(login_url='login')
def updateUser(request, pk):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/updateUserProfile.html', {'form':form})

def topicsView(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)

def recentActivityView(request):
    room_messages = Message.objects.all()
    context = {'room_messages': room_messages}
    return render(request, 'base/recentActivity.html', context)