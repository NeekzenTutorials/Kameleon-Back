from django.shortcuts import render
from django.contrib.auth import authenticate
from .models import User

def latest_users(request):
    result = None  # Variable pour stocker le résultat de l'authentification

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)  # Vérifie les identifiants
        result = user is not None  # True si utilisateur trouvé, sinon False

    # Récupérer les 5 derniers utilisateurs créés
    users = User.objects.order_by('-created_at')[:5]
    return render(request, 'latest_users.html', {'users': users, 'result': result})