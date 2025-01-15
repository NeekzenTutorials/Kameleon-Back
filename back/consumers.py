import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CoopInvitation, Member

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
    
    @database_sync_to_async
    def get_member(self, username):
        return Member.objects.get(user__username=username)
    
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
        else:
            self.member = await self.get_member(user.username)
            self.riddle_id = self.scope['url_route']['kwargs']['riddle_id']
            self.group_name = f"coop_{self.riddle_id}"

            # Joindre le groupe
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()

            # ---- Déterminer si l'utilisateur est déjà "accepted" dans la coop
            # (Optionnel, dépend de la logique métier) : 
            # par exemple, on peut vérifier si l'invitation est acceptée, etc.
            # S’il n’est pas "accepted", on peut décider de le déconnecter.

            # Récupérer tous les membres existants en base
            members_usernames = await self.get_coop_members()

            # Notifier que l'utilisateur vient de se connecter
            # On veut diffuser la liste actualisée à tout le monde
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "member_joined",
                    "username": user.username
                }
            )

            # Envoyer la liste des membres connectés uniquement au nouvel arrivant
            # y compris le rôle (chef ou membre)
            await self.send(text_data=json.dumps({
                'type': 'init',
                'members': members_usernames
            }))
    
    async def receive(self, text_data):
        """
        Reçoit un message du front. Par exemple:
          {
            "action": "start_game"
          }
        """
        data = json.loads(text_data)
        action = data.get("action")

        if action == "start_game":
            # Optionnel : vérifier si l'utilisateur est le chef
            # - On récupère la liste en BDD
            # - On compare le username
            # S'il est "chef", on envoie l'événement start_game
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'start_game',
                    'message': f"Le jeu est lancé par {self.scope['user'].username} !"
                }
            )

    async def disconnect(self, close_code):
        user = self.scope['user']
        if not user.is_anonymous:
            # Notifier le groupe qu'un membre a quitté
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'member_left',
                    'username': user.username
                }
            )

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Réception d'un message "coop_message" depuis le groupe
    async def coop_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message
        }))

    # --------- NOUVEAU : gestion de "start_game" -----------
    async def start_game(self, event):
        """
        Notifie tous les membres du groupe que l’énigme commence.
        """
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'start_game',
            'message': message
        }))

    # Méthode pour obtenir les membres coopératifs validés en BDD
    @database_sync_to_async
    def get_coop_members(self):
        invitations = CoopInvitation.objects.filter(
            riddle__riddle_id=self.riddle_id,
            status='accepted'
        )
        # On peut renvoyer une liste de dicos {username, role}
        # Par exemple, le premier "accepted" est "chef", le reste "membre"
        # => C’est une décision métier ; on peut stocker la notion de "chef"
        #    autrement si souhaité.
        members = []
        accepted_users = [inv.invitee.user for inv in invitations]
        for idx, user in enumerate(accepted_users):
            role = "Chef" if idx == 0 else "Membre"
            members.append({"username": user.username, "role": role})
        return members

    # --------- Gestion des événements de groupe -----------
    async def member_joined(self, event):
        username = event['username']

        # Récupère la liste complète des membres en base,
        # afin d’inclure ce nouveau membre s’il est "accepted".
        members = await self.get_coop_members()

        # Notifier *tous* les sockets du groupe
        await self.send(text_data=json.dumps({
            'type': 'member_joined',
            'username': username,
            'members': members,
        }))

    async def member_left(self, event):
        username = event['username']
        # On récupère la liste des membres restants
        members = await self.get_coop_members()

        await self.send(text_data=json.dumps({
            'type': 'member_left',
            'username': username,
            'members': members,
        }))
        
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
        else:
            self.group_name = f"user_{user.id}"
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': message
        }))