from django.shortcuts import render
from django.contrib.auth import logout, login, authenticate
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def logoutView(request):
    logout(request)
    return redirect('awt:public_topics_list')

def registerView(request):
    if request.method!='POST':
        form = UserCreationForm()
    else:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()

            #Login the new user, picking username and password name here from the default django user creation form.
            user_login=authenticate(username=request.POST['username'], password=request.POST['password1'])
            login(request, user_login)
            return redirect('awt:secure_topics_list')
    context={'form':form}
    return render(request,'users/register.html', context)


    pass
