from functools import wraps
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import get_object_or_404
from .models import Event, States
from challenges.models import get_challenge_model_class


def require_active_event(function=None, model_param='pk'):
    """
    Decorator to check if associated event is active.
    Can be used with or without parameters:
    
    @require_active_event
    def my_view(request, pk):
        pass
        
    @require_active_event(model_param='custom_param')
    def my_view(request, custom_param):
        pass
    """
    def actual_decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Get the model instance
            if 'event_id' in kwargs:
                # Assume that the model instance's primary key (id) is passed as a URL parameter
                event = get_object_or_404(Event, pk=kwargs['event_id'])
            elif "challenge_type" in kwargs and "challenge_id" in kwargs:
                challenge_type = kwargs["challenge_type"]
                challenge_id = kwargs["challenge_id"]
                challenge_model = get_challenge_model_class(challenge_type)
                challenge = challenge_model.objects.get(pk=challenge_id)
                event = challenge.event

            # Check if event exists and is active
            if event.state == States.CLOSED:
                return HttpResponse(status=200, content="<div style='color: red; font-size: 2rem;'>Event is closed!</div>")  # Silent success
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if function:
        return actual_decorator(function)
    return actual_decorator
