import json

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from .models import Message

User = get_user_model()


class BaseConsumer(AsyncWebsocketConsumer):
    async def update_presence(self, username, action):
        pass

    async def connect(self):
        self.room_name = 'chat'
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.update_presence(self.scope['user'].username, 'logged in')

    async def disconnect(self, close_code):
        # Leave room group
        await self.update_presence(self.scope['user'].username, 'leave chat')

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'id': str(message.id),
            'author': message.author.username,
            'content': message.content,
            'created_at': str(message.created_at)
        }


class ChatConsumer(BaseConsumer):
    @database_sync_to_async
    def get_system_user(self):
        user, created = User.objects.get_or_create(username='system')
        if created:
            user.set_password('')
            user.save()
        return user

    @database_sync_to_async
    def save_message(self, author, content):
        return Message.objects.create(author=author, content=content)

    @database_sync_to_async
    def get_members(self):
        return [x.username for x in User.objects.filter(is_logged=True)]

    async def update_presence(self, username, action):
        system_user = await self.get_system_user()
        content = f'{username} {action}'
        message = await self.save_message(system_user, content)
        members = await self.get_members()
        content = {
            'type': 'update_presence',
            'message': self.message_to_json(message),
            'members': members,
            'username': self.scope['user'].username
        }
        await self.send_group_message(content)

    async def init_chat(self, data):
        content = {
            'type': 'init_chat',
            'channel_name': self.channel_name,
            'username': self.scope['user'].username
        }
        await self.send_message(content)

    async def add_message(self, data):
        author = self.scope.get('user')

        content = data.get('data')
        mention_user = mention_message = ''

        if '@' in content and len(content) > 1:
            s = content.split('@')[1]
            mention_user = s.split(' ')[0]
            mess = ' '.join(s.split(' ')[1:])

            mention_message = f'{author.username} say - {mess}'

        if mention_user == author.username:
            mention_message = mention_user = ''

        message = await self.save_message(author, content)

        content = {
            'type': 'add_message',
            'message': self.message_to_json(message),
            'mention_user': mention_user,
            'mention_message': mention_message,
        }
        await self.send_group_message(content)

    async def fetch_messages(self, data):
        queryset = Message.objects.filter(
            pk__lte=data['text']['data']['last_message_id']
        ).order_by("-created_at")[:10]

        count_messages = len(queryset)

        previous_message_id = -1
        if count_messages > 0:
            last_message_id = queryset[count_messages - 1].id
            previous_message = Message.objects.filter(
                pk__lt=last_message_id
            ).order_by("-pk").first()

            if previous_message:
                previous_message_id = previous_message.id

        chat_messages = reversed(queryset)
        cleaned_chat_messages = list()
        for item in chat_messages:
            cleaned_item = {'user': item.author.username, 'message': item.content}
            cleaned_chat_messages.append(cleaned_item)

        content = {
            'type': 'fetch_messages',
            'messages': cleaned_chat_messages,
            'previous_id': previous_message_id
        }
        await self.send_message(content)

    commands = {
        'add_message': add_message,
        'init_chat': init_chat,
        'fetch_messages': fetch_messages,
    }

    async def receive(self, text_data):
        data = json.loads(text_data)
        cmd = data.get('command')
        func = self.commands.get(cmd)

        if func:
            await func(self, data)

    async def send_message(self, message):
        await self.send(text_data=json.dumps(message))

    async def send_group_message(self, message):
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
