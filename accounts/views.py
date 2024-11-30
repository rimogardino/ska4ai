from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView
from challenges.models import get_challenge_model_class
from submissions.models import Submission
from .forms import SignUpForm

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "accounts/signup.html"


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save the user
            form.save()
            # Redirect to home page or any other page after signup
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})



@login_required
def myprofile(request):
    challenges = get_challenge_model_class('CH').objects.filter(user=request.user)
    spots = get_challenge_model_class('SP').objects.filter(user=request.user)
    all_challenges = [*spots, *challenges]
    submissions = Submission.objects.filter(user=request.user)
    print("all_challenges", all_challenges)
    context = {
        "all_challenges": all_challenges,
        "submissions": submissions
        }
    return render(request, 'accounts/myprofile.html', context)