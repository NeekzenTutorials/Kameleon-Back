from django.shortcuts import render
from django.contrib.auth import authenticate
from .models import User

def latest_users(request):
    result = None  # Result of authentification

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)  # Check if user exists
        result = user is not None

    # Send the 5 latest users to the template
    users = User.objects.order_by('-created_at')[:5]
    return render(request, 'latest_users.html', {'users': users, 'result': result})