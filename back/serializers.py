from rest_framework import serializers
from .models import User, Riddle, Clue, SoloRiddle

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }
        
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_picture', 'rank', 'created_at']
        read_only_fields = ['id', 'rank', 'created_at']
        
    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture']
        
class ClueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clue
        fields = ['clue_id', 'clue_text']
        
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