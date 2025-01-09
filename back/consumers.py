import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "chat_room"
        
        # Rejoindre le groupe
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Accepter la connexion WebSocket sans vérification de token
        await self.accept()

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
        
        # Diffuser le message à tout le monde dans la room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        # Réception d’un message de la room, on le renvoie au client WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
