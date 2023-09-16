from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # get named fields from the form data
            username = form.cleaned_data.get('username')
            # password input field is named 'password'
            raw_passwd = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_passwd)
            login(request, user)
            return redirect('polls:index')
        else:
            # display a message in signup.html
            print(form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # create a user form and display it the signup page
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})