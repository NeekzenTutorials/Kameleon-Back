from rest_framework import serializers
from .models import User, Riddle, Clue, Member, Clan, CV, CoopInvitation, MemberRiddleStats

class UserSerializer(serializers.ModelSerializer):
    cv_url = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'profile_picture',
            'created_at',
            'is_staff',
            'cv_url',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def get_cv_url(self, obj):
        """
        Retourne l'URL du fichier CV associé, ou None si aucun CV n'est présent.
        """
        if obj.cv and obj.cv.cv_file:
            return obj.cv.cv_file.url
        return None
        
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'profile_picture',
            'created_at',
            'is_staff',
        ]
        read_only_fields = ['id', 'created_at']
        
    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'profile_picture',
            'created_at',
            'is_staff',
        ]
        
class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    achieved_riddles = serializers.SerializerMethodField()
    locked_riddles = serializers.SerializerMethodField()
    achieved_coop_riddles = serializers.SerializerMethodField()
    locked_coop_riddles = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            'user',
            'member_score',
            'member_clan_score',
            'achieved_riddles',
            'locked_riddles',
            'achieved_coop_riddles',
            'locked_coop_riddles',
            'have_calculatrice',
        ]

    def get_achieved_riddles(self, obj):
        return obj.achieved_riddles.values_list('riddle_id', flat=True)

    def get_locked_riddles(self, obj):
        return obj.locked_riddles.values_list('riddle_id', flat=True)

    def get_achieved_coop_riddles(self, obj):
        return obj.achieved_coop_riddles.values_list('riddle_id', flat=True)

    def get_locked_coop_riddles(self, obj):
        return obj.locked_coop_riddles.values_list('riddle_id', flat=True)
        
class ClueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clue
        fields = ['clue_id', 'clue_text']
        
class SimpleRiddleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Riddle
        fields = ['riddle_id', 'riddle_type', 'riddle_theme', 'riddle_difficulty']
        
class RiddleDependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Riddle
        fields = [
            'riddle_id',
            'riddle_theme',
            'riddle_points',
        ]

class RiddleSerializer(serializers.ModelSerializer):
    clues = ClueSerializer(many=True, read_only=True, source='clue_set')
    dependance = RiddleDependencySerializer(many=True, read_only=True, source='riddle_dependance')

    class Meta:
        model = Riddle
        fields = [
            'riddle_id',
            'riddle_type',
            'riddle_variable',
            'riddle_response',
            'riddle_difficulty',
            'riddle_theme',
            'riddle_points',
            'riddle_path',
            'dependance',
            'clues',
        ]
    
class ClanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clan
        fields = [
            'clan_id',
            'clan_name',
            'clan_bio',
            'clan_pci',
            'clan_members_count',
            'clan_members_max_count',
            'clan_elo',
            'created_at',
        ]
        read_only_fields = ['clan_id', 'clan_members_count', 'clan_elo', 'created_at']

class CVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = ['cv_id', 'cv_file', 'upload_date']
        
class CoopInvitationSerializer(serializers.ModelSerializer):
    inviter_username = serializers.CharField(source='inviter.user.username', read_only=True)
    invitee_username = serializers.CharField(source='invitee.user.username', read_only=True)
    riddle_type = serializers.CharField(source='riddle.riddle_type', read_only=True)

    class Meta:
        model = CoopInvitation
        fields = ['id', 'riddle', 'riddle_type', 'inviter', 'inviter_username', 'invitee', 'invitee_username', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

class RiddleStatsSerializer(serializers.ModelSerializer):
    member_username = serializers.ReadOnlyField(source='member.user.username')
    riddle_name = serializers.ReadOnlyField(source='riddle.riddle_type')

    class Meta:
        model = MemberRiddleStats
        fields = [
            'id',
            'member',
            'riddle',
            'try_count',
            'errors_count',
            'resolution_count',
            'first_resolved_at',
            'is_resolved',
            'member_username',
            'riddle_name',
        ]