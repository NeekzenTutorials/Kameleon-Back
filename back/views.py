from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.hashers import make_password
from .models import User, Riddle, Member
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .serializers import UserDetailSerializer, UserUpdateSerializer, RiddleSerializer, MemberSerializer, SimpleRiddleSerializer


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

        riddle_id = data.get('riddle_id')
        user_response = data.get('response')

        # If riddle_id doesn't exist
        try:
            riddle = Riddle.objects.get(riddle_id=riddle_id)
        except Riddle.DoesNotExist:
            return Response({'error': 'Riddle not found'}, status=status.HTTP_404_NOT_FOUND)

        # If user already solved the riddle
        user_solved_riddles = user.solved_riddles.all()
        if riddle in user_solved_riddles:
            return Response({'is_solved': True, 'message': 'Riddle already solved'}, status=status.HTTP_200_OK)

        # Check if the response is correct
        if user_response == riddle.riddle_response:
            # Add the riddle to the user's solved riddles
            member = user.member
            member.add_riddle_to_achieved(riddle)
            return Response({'is_solved': True, 'message': 'Correct answer!'}, status=status.HTTP_200_OK)

        # If the response is incorrect
        return Response({'is_solved': False, 'message': 'Incorrect answer'}, status=status.HTTP_200_OK)