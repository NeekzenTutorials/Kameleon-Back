from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from .serializers import UserDetailSerializer, UserUpdateSerializer, RiddleSerializer, MemberSerializer, SimpleRiddleSerializer
from .models import User, Riddle, Member, Clue


class SignUpView(APIView):
    def post(self, request):
        data = request.data
        try:
            user = User.objects.create(
                username=data['username'],
                email=data['email'],
                password=make_password(data['password']),
                is_active=False
            )

            token = default_token_generator.make_token(user)
            activation_link = f"{settings.BACKEND_URL}/activate/{user.id}/{token}"

            send_mail(
                subject='Activate Your Account',
                message=f"Hi {user.username},\n\nClick the link below to activate your account:\n{activation_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[data['email']],
                fail_silently=False,
            )

            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class ActivateAccountView(APIView):
    def get(self, request, user_id, token):
        user = get_object_or_404(User, id=user_id)
        
        if default_token_generator.check_token(user, token):
            user.is_active = True  # Activate account
            user.save()
            return Response({'message': 'Account activated successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        
class LogInView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')

        # Authentifier l'utilisateur
        user = authenticate(username=username, password=password)

        if user is not None:
            if not user.is_active:
                return Response({'error': 'Account is not active. Please verify your email to activate your account.'},
                                status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user) # Generate authentification token
            return Response({
                'message': 'User logged in successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] 

    def put(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MemberDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        member = request.user.member
        serializer = MemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class MemberRiddlesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        member = get_object_or_404(Member, user=user)

        achieved_riddles = SimpleRiddleSerializer(member.achieved_riddles.all(), many=True).data
        locked_riddles = SimpleRiddleSerializer(member.locked_riddles.all(), many=True).data

        return Response({
            "achievedRiddles": achieved_riddles,
            "lockedRiddles": locked_riddles
        })
    
class RiddleListView(generics.ListAPIView):
    """
    Vue pour lister toutes les énigmes.
    """
    queryset = Riddle.objects.all()
    serializer_class = RiddleSerializer
    permission_classes = [IsAuthenticated] 

class RiddleDetailView(generics.RetrieveAPIView):
    """
    Vue pour récupérer les détails d'une énigme spécifique.
    """
    queryset = Riddle.objects.all()
    serializer_class = RiddleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'riddle_id'

# Gameplay views

class IsRiddleSolved(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        user = request.user
        member = user.member

        riddle_id = data.get('riddle_id')
        user_response = data.get('response')

        # If riddle_id doesn't exist
        try:
            riddle = Riddle.objects.get(riddle_id=riddle_id)
        except Riddle.DoesNotExist:
            return Response({'error': 'Riddle not found'}, status=status.HTTP_404_NOT_FOUND)

        # If user already solved the riddle
        member_achieved_riddles = member.achieved_riddles.all()
        if riddle in member_achieved_riddles:
            return Response({'is_solved': True, 'message': 'Riddle already solved'}, status=status.HTTP_200_OK)

        # Check if the response is correct
        if user_response == riddle.riddle_response:
            # Add the riddle to the user's solved riddles
            member.add_riddle_to_achieved(riddle)
            return Response({'is_solved': True, 'message': 'Correct answer!'}, status=status.HTTP_200_OK)

        # If the response is incorrect
        return Response({'is_solved': False, 'message': 'Incorrect answer'}, status=status.HTTP_200_OK)
    
class GetClue(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        riddle_id = request.data.get('riddle_id')
        clue_number = request.data.get('clue')

        try:
            riddle = Riddle.objects.get(riddle_id=riddle_id)
        except Riddle.DoesNotExist:
            return Response({'error': 'Riddle not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if clue exists
        clue = Clue.objects.filter(riddle=riddle).order_by('clue_id')[clue_number - 1] if clue_number in [1, 2, 3] else None

        if not clue:
            return Response({'error': 'Invalid clue number.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user has already used this hint
        member = user.member
        if clue in member.revealed_clues.all():
            return Response({'hint': clue.clue_text}, status=status.HTTP_200_OK)

        # Save the clue in the member's revealed clues
        member.revealed_clues.add(clue)

        return Response({'hint': clue.clue_text}, status=status.HTTP_200_OK)