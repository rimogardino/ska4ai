from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from .forms import SubmissionForm
from .models import Submission
from challenges.models import get_challenge_model_class, Visual
from challenges.views import get_liked_by_user, get_challenge_likes_count, get_challenge_visuals
from userinteraction.models import ChallengeLike


def create_submission(request, challenge_type, challenge_id):
    challenge_model = get_challenge_model_class(challenge_type)
    challenge = challenge_model.objects.get(pk=challenge_id)
    challenge_visuals = get_challenge_visuals(challenge, challenge_type)

    # Check if user has already submitted a submission
    query_by_parent_challenge = Submission.query_by_parent_challenge(challenge, challenge_type)
    old_submission = Submission.objects.filter(query_by_parent_challenge, user=request.user)
    if old_submission.exists():
        return HttpResponse("<p>You have already submitted a submission for this challenge!</p>")
    print(request.method)
    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES)
        form.instance.user = request.user
        form.instance.challenge = challenge
        form.instance.file_type = request.FILES['visual'].content_type
        if form.is_valid():
            form.save()
            return HttpResponse("<p>Submission submitted successfully!</p>")
    else:
        form = SubmissionForm()
    context = {
        'form': form,
        'challenge': challenge,
        'visuals': challenge_visuals
    }
    # miaybe change to HttpResponse for consistency?
    return render(request, 'submissions/create_submission.html', context)


def submission_detail(request, submission_id):
    submission  = get_object_or_404(Submission, pk=submission_id)
    likes_count = get_challenge_likes_count(submission.challenge, submission.challenge.challenge_type) #ChallengeLike.objects.filter(challenge=submission.challenge).count()
    liked_by_user = get_liked_by_user(request.user, submission.challenge, submission.challenge.challenge_type)
    challenge_visuals = get_challenge_visuals(submission.challenge, submission.challenge.challenge_type) #Visual.objects.filter(Visual.query_by_parent_challenge(submission.challenge, submission.challenge.challenge_type))
    return render(request, 'submissions/submission_detail.html', 
                  {'submission': submission, 
                   'likes_count': likes_count,
                   'liked_by_user': liked_by_user,
                   'challenge_visuals': challenge_visuals,
                   })


def edit_submission(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.save()
            return redirect('submissions:submission_detail', submission.id)
    else:
        form = SubmissionForm(instance=submission)
    context = {
        'form': form
    }
    return render(request, 'submissions/create_submission.html', context)


def delete_submission(request, submission_id):  
    submission = get_object_or_404(Submission, pk=submission_id)
    submission.delete()
    return redirect('accounts:myprofile')
