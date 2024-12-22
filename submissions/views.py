from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from .forms import SubmissionForm
from .models import Submission
from challenges.models import get_challenge_model_class, Visual
from userinteraction.models import ChallengeLike

# Create your views here.
def create_submission(request, challenge_type, challenge_id):
    challenge_model = get_challenge_model_class(challenge_type)
    challenge = challenge_model.objects.get(pk=challenge_id)
    challenge_visuals = Visual.objects.filter(Visual.query_by_parent_challenge(challenge, challenge_type))

    if request.method == "POST":
        print("we postin boys", request.POST)
        form = SubmissionForm(request.POST, request.FILES)
        form.instance.user = request.user
        form.instance.challenge = challenge
        if form.is_valid():
            submission = form.save()
            return HttpResponse("<p>Submission submitted successfully!</p>")
    else:
        form = SubmissionForm()
    context = {
        'form': form,
        'challenge': challenge,
        'visuals': challenge_visuals
    }
    return render(request, 'submissions/create_submission.html', context)

def submission_detail(request, submission_id):
    submission  = get_object_or_404(Submission, pk=submission_id)
    likes_count = ChallengeLike.objects.filter(liked_challenge=submission.challenge).count()
    challenge_visuals = Visual.objects.filter(Visual.query_by_parent_challenge(submission.challenge, submission.challenge.challenge_type))
    return render(request, 'submissions/submission_detail.html', 
                  {'submission': submission, 
                   'likes_count': likes_count,
                   'challenge_visuals': challenge_visuals})

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
