import jwt
from channels.auth import get_user
from channels.db import database_sync_to_async
from django.conf import settings
from .models import User
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class RiddleConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        print(f"Attempting to connect to riddle {self.scope['url_route']['kwargs']['riddle_id']}")
        # Récupérer le nom de la salle à partir de l'URL
        self.riddle_id = self.scope['url_route']['kwargs']['riddle_id']
        self.room_group_name = f"riddle_{self.riddle_id}"
        
        # Récupérer le token JWT depuis l'en-tête
        self.token = self.scope['headers'][1][1].decode('utf-8').split(' ')[1]  # Exemple : "Bearer <token>"
        print(f"Token received: {self.token}")
        
        # Vérifier le token et récupérer l'utilisateur
        self.user = await self.get_user_from_token(self.token)
        
        if self.user is None:
            await self.close()  # Si l'utilisateur n'est pas authentifié, fermer la connexion
            return

        # Rejoindre le groupe
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        print(f"Connected to riddle {self.riddle_id}")

    async def disconnect(self, close_code):
        # Quitter le groupe
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Recevoir un message du WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Ajouter le pseudo de l'utilisateur
        user_message = f"{self.user.username}: {message}"

        # Envoyer le message au groupe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': user_message
            }
        )

    async def chat_message(self, event):
        # Recevoir un message du groupe et l'envoyer au WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload['user_id'])
            return user
        except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
            return None
