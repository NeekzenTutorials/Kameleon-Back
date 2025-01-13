from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .serializers import UserDetailSerializer, UserUpdateSerializer, RiddleSerializer, MemberSerializer, SimpleRiddleSerializer, ClanSerializer, CVSerializer
from .models import User, Riddle, Member, Clue, Clan, CV
import requests


class SignUpView(APIView):
    def post(self, request):
        data = request.data
        try:

            # Check email format
            email = data.get('email')
            try:
                validate_email(email)
            except ValidationError:
                return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.create(
                username=data['username'],
                email=email,
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
    
class MemberCoopRiddlesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        member = get_object_or_404(Member, user=user)

        achieved_coop_riddles = SimpleRiddleSerializer(member.achieved_coop_riddles.all(), many=True).data
        locked_coop_riddles = SimpleRiddleSerializer(member.locked_coop_riddles.all(), many=True).data

        return Response({
            "achievedCoopRiddles": achieved_coop_riddles,
            "lockedCoopRiddles": locked_coop_riddles
        })
    
class SoloRiddleListView(generics.ListAPIView):
    """
    Vue pour lister toutes les énigmes.
    """
    queryset = Riddle.objects.filter(riddle_mode='solo')
    serializer_class = RiddleSerializer
    permission_classes = [IsAuthenticated] 

class CoopRiddleListView(generics.ListAPIView):
    """
    Vue pour lister toutes les énigmes.
    """
    queryset = Riddle.objects.filter(riddle_mode='coop')
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
    
class MemberDashboardView(APIView):
    """
    Send the following data:
    - score_solo
    - clan_name (ou None)
    - rank_image_url
    - rank_name
    - achieved_riddles_count
    - bio
    - riddle_theme_distribution (ex: {"cryptographie": 80, "mathématique": 20})
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        member = get_object_or_404(Member, user=user)

        score_solo = member.member_score

        clan_name = getattr(member, "clan", None)
        if clan_name:
            clan_name = str(clan_name)

        rank_image_url = None
        if member.rank and member.rank.rank_image:
            rank_image_url = member.rank.rank_image.url

        rank_name = member.rank.rank_name if member.rank else None

        achieved_riddles_count = member.achieved_riddles.count()

        bio = user.bio

        theme_counts = (
            member.achieved_riddles
            .values("riddle_theme")
            .annotate(count=Count("riddle_theme"))
        )
        # Calcul du total
        total_riddles = sum(item["count"] for item in theme_counts)
        theme_distribution = {}
        if total_riddles > 0:
            for item in theme_counts:
                theme = item["riddle_theme"]
                count = item["count"]
                percentage = round((count / total_riddles) * 100, 2)
                theme_distribution[theme] = percentage
        else:
            pass

        data = {
            "score_solo": score_solo,
            "clan_name": clan_name,  # ou None
            "rank_image_url": rank_image_url,  # ou None
            "rank_name": rank_name,            # ou None
            "achieved_riddles_count": achieved_riddles_count,
            "bio": bio,
            "riddle_theme_distribution": theme_distribution,  # ex: {"cryptographie": 80, "math": 20}
        }

        return Response(data, status=status.HTTP_200_OK)
    
class CreateClanView(APIView):
    """
    View pour permettre à un utilisateur de créer un clan.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ClanSerializer(data=request.data)
        if serializer.is_valid():
            # Enregistrer le clan
            clan = serializer.save()

            user = request.user
            try:
                member = Member.objects.get(user=user)
            except Member.DoesNotExist:
                member = Member.objects.create(user=user)

            member.clan = clan
            member.is_clan_admin = True
            member.save()

            return Response(
                {
                    "message": f"Clan '{clan.clan_name}' créé avec succès!",
                    "clan": ClanSerializer(clan).data,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class JoinClanView(APIView):
    """
    View pour permettre à un utilisateur de rejoindre un clan.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            member = Member.objects.get(user=user)
        except Member.DoesNotExist:
            member = Member.objects.create(user=user)

        clan_name = request.data.get("clan_name")
        try:
            clan = Clan.objects.get(clan_name=clan_name)
        except Clan.DoesNotExist:
            return Response({"error": "Clan not found."}, status=status.HTTP_404_NOT_FOUND)

        member.clan = clan
        clan.clan_members_count += 1
        member.save()

        return Response(
            {
                "message": f"Vous avez rejoint le clan '{clan_name}' avec succès!",
                "clan": ClanSerializer(clan).data,
            },
            status=status.HTTP_200_OK
        )
    
class ClanListView(generics.ListAPIView):
    """
    Vue pour lister tous les clans.
    """
    queryset = Clan.objects.all()
    serializer_class = ClanSerializer
    permission_classes = [IsAuthenticated]

class UploadCVView(APIView):
    """
    Vue pour uploader un CV pour l'utilisateur connecté.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Vérifier si le membre a un rang spécifique
        member = getattr(user, "member", None)  # Récupérer le membre lié à l'utilisateur
        if not member or not member.rank or member.rank.name != "poisson pierre":
            return Response(
                {"error": "Vous devez avoir le rang 'poisson pierre' pour uploader un CV."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Vérifier si un fichier est présent dans la requête
        if 'cv' not in request.FILES:
            return Response({"error": "Aucun fichier n'a été fourni."}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['cv']

        # Vérifier si un CV est déjà associé à l'utilisateur
        if user.cv:
            user.cv.cv_file.delete()  # Supprimer l'ancien fichier
            user.cv.delete()

        # Créer et associer le nouveau CV
        cv = CV.objects.create(cv_file=file)
        user.cv = cv
        user.save()

        return Response({"message": "CV uploadé avec succès !", "cv_id": cv.cv_id}, status=status.HTTP_201_CREATED)
    
class GetCVView(RetrieveAPIView):
    """
    Vue pour récupérer le CV de l'utilisateur connecté.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CVSerializer

    def get_object(self):
        user = self.request.user
        if not user.cv:
            raise Response({"error": "Aucun CV n'est associé à cet utilisateur."}, status=status.HTTP_404_NOT_FOUND)
        return user.cv

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
    
class IsCoopRiddleSolved(APIView):
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
        member_achieved_riddles = member.achieved_coop_riddles.all()
        if riddle in member_achieved_riddles:
            return Response({'is_solved': True, 'message': 'Riddle already solved'}, status=status.HTTP_200_OK)

        # Check if the response is correct
        if user_response == riddle.riddle_response:
            # Add the riddle to the user's solved riddles
            member.add__coop_riddle_to_achieved_coop(riddle)
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