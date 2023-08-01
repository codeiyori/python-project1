from django.shortcuts import render
from user.models import User

# Create your views here.
def hello(request):
    context = {}

    login_session = request.session.get('login_session', '')

    if login_session == '':
        context['login_session'] = False
    else:
        context['login_session'] = True

    return render(request, 'home/index.html', context)
