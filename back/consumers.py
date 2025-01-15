import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CoopInvitation

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "chat_room"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        username = data.get('username', 'Anonyme')
        message = data.get('message', '')

        # On envoie username et message dans le group_send
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': username,
                'message': message,
            }
        )

    async def chat_message(self, event):
        # event contient 'username' et 'message'
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'body': event['message']
        }))


class CoopConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
        else:
            self.member = user.member
            self.riddle_id = self.scope['url_route']['kwargs']['riddle_id']
            self.group_name = f"coop_{self.riddle_id}"

            # Ajouter le WebSocket au groupe coopératif
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()

            # Envoyer la liste des membres connectés
            members = await self.get_coop_members()
            await self.send(text_data=json.dumps({
                'type': 'init',
                'members': members
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Recevoir un message du groupe
    async def coop_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message
        }))

    # Méthode pour obtenir les membres coopératifs
    @database_sync_to_async
    def get_coop_members(self):
        invitations = CoopInvitation.objects.filter(
            riddle__riddle_id=self.riddle_id,
            status='accepted'
        )
        members = [invitation.invitee.user.username for invitation in invitations]
        return members

    # Gestion des notifications d'un nouveau membre
    async def member_joined(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'type': 'member_joined',
            'message': message,
            'username': username
        }))

    # Gestion des notifications d'un membre quittant
    async def member_left(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'type': 'member_left',
            'message': message,
            'username': username
        }))