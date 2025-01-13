from django.shortcuts import render
from django.http import HttpResponse
from events.models import Event

def event_info(request, event_id):
    event = Event.objects.get(id=event_id)
    html = render(request, 'events/info.html', {'event': event})
    return HttpResponse(html)
