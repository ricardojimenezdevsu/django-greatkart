"""A dummy docstring."""
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required

from .forms import RegistrationForm
from .models import Account

# Create your views here.


def register(request):
    """A dummy docstring."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )
            user.phone_number = phone_number
            user.save()
            messages.success(request, 'Registrated successfuly')
            return redirect('register')
    else:
        form = RegistrationForm()

    context = {
        'form': form
    }
    return render(request, 'account/register.html', context)


def loging(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid email/password')
            return redirect('loging')
    return render(request, 'account/loging.html')

@login_required(login_url = 'loging')
def logout(request):
    """A dummy docstring."""
    auth.logout(request)
    return redirect('loging')
