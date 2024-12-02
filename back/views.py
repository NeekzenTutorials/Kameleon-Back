from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from .models import User
from django.contrib.auth import authenticate

class SignUpView(APIView):
    def post(self, request):
        data = request.data
        try:
            user = User.objects.create(
                username=data['username'],
                email=data['email'],
                password=make_password(data['password'])
            )
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class LogInView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')

        # Authentifier l'utilisateur
        user = authenticate(username=username, password=password)

        if user is not None:
            # Générer un token JWT
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User logged in successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)