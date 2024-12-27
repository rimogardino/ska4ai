from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect, reverse
from django.forms import modelformset_factory
from events.models import Event
from .models import Visual, get_challenge_model_class
from .forms import get_challenge_form_class, VisualForm
from userinteraction.models import ChallengeLike
from submissions.models import Submission
import json
from pathlib import Path


home = Path.home()
with open(home / ".django_envs.json", "r") as f:
    django_envs = json.load(f)[0]


def create_challenge(request, event_id=None, errors=None):
    """
    Creates a new challenge based on the data provided in the request.

    :param request: The request object.
    :param event_id: The id of the event for which the challenge is being created.
    :param errors: A list of errors that occurred during the submission process.
    :return: A rendered page with the form to create a new challenge.
    """
    event = get_object_or_404(Event, pk=event_id)
    challenge_type = event.get_challenge_type_display()
    # Determine the form class based on the event type
    form_class = get_challenge_form_class(challenge_type)
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        print("visuals", request.FILES.getlist('files'))
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.event = event
            instance.save()
            files = request.FILES.getlist('files')
            for f in files:
                visual = Visual(file=f)
                visual.parent = instance
                visual.file_type = f.content_type
                visual.save()
            return redirect(reverse('challenges:challenge_detail',
                                    kwargs={'challenge_id':instance.id,
                                            'challenge_type': instance.challenge_type}))
    else:
        form = form_class()
    context = {"form": form, 
               "event_id": event_id, 
               "errors": errors, 
               "mapbox_api_key": django_envs['MAPBOX_API_KEY']}
    return render(request, "challenges/create_challenge.html", context)


def challenge_detail(request, challenge_type, challenge_id):
    challenge = get_challenge_model_class(challenge_type).objects.get(pk=challenge_id)
    visuals = get_challenge_visuals(challenge, challenge_type)
    likes_count = get_challenge_likes_count(challenge, challenge_type)
    liked_by_user = get_liked_by_user(request.user, challenge, challenge_type)
    submissions = _get_submissions(challenge, challenge_type)
    return render(request, "challenges/challenge_detail.html", 
                  {"challenge": challenge,
                   "visuals": visuals, 
                   "likes_count": likes_count,
                   "liked_by_user": liked_by_user,
                    "submissions": submissions,
                   })


def challenge_simple_info(request, challenge_type, challenge_id):
    print("challenge_simple_info", challenge_type, challenge_id)
    challenge = get_challenge_model_class(challenge_type).objects.get(pk=challenge_id)
    # Visuals
    visuals = get_challenge_visuals(challenge, challenge_type)
    # Likes count
    likes_count = get_challenge_likes_count(challenge, challenge_type)
    liked_by_user = get_liked_by_user(request.user, challenge, challenge_type)
    return render(request, "challenges/challenge_simple_info.html",
                  {"challenge": challenge,
                   "visuals": visuals,
                   "likes_count": likes_count,
                   "liked_by_user": liked_by_user,
                   })

def get_challenge_visuals(challenge, challenge_type):
    query_by_parent_challenge = Visual.query_by_parent_challenge(challenge, challenge_type)
    visuals = Visual.objects.filter(query_by_parent_challenge)
    return visuals

def get_challenge_likes_count(challenge, challenge_type):
    liked_challenges_query = ChallengeLike.query_by_parent_challenge(challenge, challenge_type)
    likes_count = ChallengeLike.objects.filter(liked_challenges_query).count()
    return likes_count

def get_liked_by_user(user, challenge, challenge_type):
    liked_challenges_query = ChallengeLike.query_by_parent_challenge(challenge, challenge_type)
    liked_by_user = False
    if user.is_authenticated:
        liked_by_user = ChallengeLike.objects.filter(liked_challenges_query, user=user).exists()
    return liked_by_user

def _get_submissions(challenge, challenge_type):
    query_by_parent_challenge = Submission.query_by_parent_challenge(challenge, challenge_type)
    submissions = Submission.objects.filter(query_by_parent_challenge)
    return submissions

def edit_challenge(request, challenge_type, challenge_id):
    model_class = get_challenge_model_class(challenge_type)
    challenge = model_class.objects.get(pk=challenge_id)
    query_by_parent_challenge = Visual.query_by_parent_challenge(challenge, challenge_type)
    VisualFormSet = modelformset_factory(Visual, form=VisualForm, extra=1, can_delete=True)
    main_form = get_challenge_form_class(model_class.__name__)
    if request.method == 'POST':
        main_form = main_form(request.POST, request.FILES, instance=challenge)
        visual_formset = VisualFormSet(request.POST,
                                       request.FILES,
                                       queryset=Visual.objects.filter(query_by_parent_challenge)
                                       )
        for form in visual_formset:
            form.instance.parent = challenge
        if main_form.is_valid() and visual_formset.is_valid():
            main_form.save()
            for form in visual_formset:
                if form.instance.id and form.cleaned_data.get('DELETE'):
                    form.save(commit=False).delete()
                elif form.has_changed():
                    form.save()
            visual_formset.save()
            return redirect('challenges:challenge_detail', challenge_type, challenge_id)
    else:
        main_form = main_form(instance=challenge)
        visual_formset = VisualFormSet(queryset=Visual.objects.filter(query_by_parent_challenge))
        #import pdb;pdb.set_trace()
    context = {
        'main_form': main_form,
        'visual_formset': visual_formset,
    }
    return render(request, 'challenges/edit_challenge.html', context)


def delete_challenge(request, challenge_type, challenge_id):
    challenge = get_challenge_model_class(challenge_type).objects.get(pk=challenge_id)
    challenge.delete()

    return redirect(reverse("index"))


