from django.shortcuts import render
from .forms import UserRegisterForm
from django.contrib import messages
from django.shortcuts import redirect

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
                form.save()
                messages.success(request, f"Your account has been created! You can login now")
                return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'account/register.html', {'form':form})
 