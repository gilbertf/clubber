from django.shortcuts import  render, redirect
from .forms import NewUserForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import update_session_auth_hash

from django.contrib.auth import authenticate, login

def login_request(request, user_id = None):
    if request.user.is_authenticated:
       if "next" in request.GET:
          next_page = request.GET['next']
          return HttpResponseRedirect(next_page)
       else:
          return redirect('/')
    else:
         if request.method == "POST":
             fm = AuthenticationForm(request=request, data=request.POST)
             if fm.is_valid():
                 username = fm.cleaned_data.get('username')
                 password = fm.cleaned_data.get('password')
                 user = authenticate(request,username=username, password=password)
                 if user is not None:
                     login(request, user)
                     if "next" in request.GET:
                        next_page = request.GET['next']
                        return HttpResponseRedirect(next_page)
                     else:
                        return redirect('/')
         else:
             fm = AuthenticationForm()
             if user_id != None:
                 user = get_user_model().objects.filter(id = user_id).get()
                 fm.fields["username"].initial = user.username
         return render(request, "registration/login.html", context={"form":fm})

from django.utils import translation    
def register_request(request):
    new_user_form = NewUserForm()
    new_user_form["language"].initial = translation.get_language()

    if request.method == 'POST':
        new_user_form = NewUserForm(request.POST)
        if new_user_form.is_valid():
            user = new_user_form.save()
            login(request, user)
            return redirect('/')
    return render(request, "registration/register.html", context={"new_user_form":new_user_form})

def password_change_request(request):
    if request.method == 'POST':
        change_form = PasswordChangeForm(request.user, request.POST)
        if change_form.is_valid():
            user = change_form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:       
        change_form = PasswordChangeForm(request.user)
    return render(request, "registration/password_change.html", context={"change_form":change_form})

def password_reset_request(request):
    if request.method == 'POST':
        reset_form = PasswordResetForm(request.POST)
        if reset_form.is_valid():
            reset_form.save(request=request)
            return redirect('/')
        else:
            messages.error(request, 'Please correct the error below.')
   
    else:
        reset_form = PasswordResetForm()
    return render(request, "registration/password_reset.html", context={"reset_form":reset_form})
