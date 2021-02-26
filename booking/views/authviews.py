from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse


@login_required
def landing(request):
    if request.user.type == 'admin':
        pass
        #return HttpResponseRedirect(reverse('admin:index'))
    #elif request.user.type == 'register':
        
    return HttpResponseRedirect(reverse('index'))

def logout_view(request):
    print("test1")
    logout(request)
    return HttpResponseRedirect(reverse('login'))
