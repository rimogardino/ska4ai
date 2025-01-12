from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from .forms import SubmissionForm
from .models import Submission
from challenges.models import get_challenge_model_class
from challenges.views import get_liked_by_user, get_challenge_likes_count, get_challenge_visuals
from visualprocessing.models import VisualsQueue
from userinteraction.models import Notification


def create_submission(request, challenge_type, challenge_id):
    challenge_model = get_challenge_model_class(challenge_type)
    challenge = challenge_model.objects.get(pk=challenge_id)
    challenge_visuals = get_challenge_visuals(challenge, challenge_type)

    # Check if user has already submitted a submission
    query_by_parent_challenge = Submission.query_by_parent_challenge(challenge, challenge_type)
    old_submission = Submission.objects.filter(query_by_parent_challenge, user=request.user)
    if old_submission.exists():
        return HttpResponse("<p>You have already submitted a submission for this challenge!</p>")

    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES)
        form.instance.user = request.user
        form.instance.challenge = challenge
        form.instance.file_type = request.FILES['visual'].content_type
        if form.is_valid():
            form.save()
            VisualsQueue.objects.create(visual=form.instance.visual.name, file_type=request.FILES['visual'].content_type)
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
    context = _submission_simple_info_context(request, submission_id)
    return render(request, 'submissions/submission_detail.html', 
                  context)


def submission_moderation(request, submission_id):
    context = _submission_simple_info_context(request, submission_id)
    return render(request, 'submissions/submission_moderation.html', 
                  context)


def _submission_simple_info_context(request, submission_id):
    submission  = get_object_or_404(Submission, pk=submission_id)
    likes_count = get_challenge_likes_count(submission.challenge, submission.challenge.challenge_type)
    liked_by_user = get_liked_by_user(request.user, submission.challenge, submission.challenge.challenge_type)
    challenge_visuals = get_challenge_visuals(submission.challenge, submission.challenge.challenge_type)
    context = {"submission": submission,
                   "likes_count": likes_count,
                   "liked_by_user": liked_by_user,
                   "challenge_visuals": challenge_visuals,
                   }
    return context


def approve_submission(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    submission.approve()
    _create_notification(request, submission, approve=True)
    message = f"<div style='color: green; padding:2rem;'>Submission {submission_id} has been approved</div>"
    html = render(request, 'home/mod_undo_submission_button.html', {
            'submission': submission,
            'message': message,
        })
    return HttpResponse(html)


def disapprove_submission(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    submission.disapprove()
    _create_notification(request, submission, approve=False)
    message = f"<div style='color: red; padding:2rem;'>Submission {submission_id}  has been disapproved</div>"
    html = render(request, 'home/mod_undo_submission_button.html', {
            'submission': submission,
            'message': message,
        })
    return HttpResponse(html)


def _create_notification(request, submission, approve=True):
    notification = Notification(user=submission.user)
    notification.save()
    notification_context = _submission_simple_info_context(request, submission.pk)
    notification_context['notification_id'] = notification.pk
    template = 'userinteraction/notification_messages/approved_submission.html'
    if not approve:
        template = 'userinteraction/notification_messages/disapproved_submission.html'
    notification.message = render_to_string(
                                            template,
                                            notification_context)
    notification.save()

def reset_submission_state(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    submission.reset_state()
    Notification.objects.filter(user=submission.user).order_by('-created_at').first().delete()
    context = _submission_simple_info_context(request, submission_id)
    return render(request, 'submissions/submission_moderation.html', 
                  context)


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
