from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm

# Create your views here.
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                if hasattr(user, 'profile') and user.profile.ready:
                    login(request, user)
                    messages.success(request, "Tizimga xush kelibsiz")
                    return redirect('home')
                else:
                    messages.error(request, "Siz to'lov qilishingiz kerak!")
            else:
                messages.error(request, "Login yoki parol xato!")
        # form yaroqsiz bo‘lsa, pastdagi renderga tushadi
    else:
        form = LoginForm()

    context = {
        "form": form
    }

    return render(request, 'accounts/login.html', context)


def user_logout(request):
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect('login')