from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from .models import Thread
from django.contrib.auth.models import User

@login_required
def messages_page(request):
    receiver=request.GET.get('receiver')
    receive=User.objects.get(username=receiver)
    print(receive.id)
    thread = Thread.objects.filter((Q(first_person=request.user) | Q(second_person=request.user)) &(Q(first_person=receive) | Q(second_person=receive))).prefetch_related('chatmessage_thread').first()
    if thread is None:
        thread=Thread.objects.create(first_person=request.user,second_person=receive)
    context = {
       'thread': thread,
       'other_person':receive
    }
    print(thread)
    response=render(request, 'msg.html', context)
    response.set_cookie('thread_id',thread.id)

    return response