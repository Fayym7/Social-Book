import json
from channels.db import database_sync_to_async
from channels.consumer import AsyncConsumer
from channels.layers import get_channel_layer
from asyncc.models import Thread, ChatMessage
from urllib.parse import parse_qs
from django.db.models import Q
from django.contrib.auth.models import User

channel_layer =get_channel_layer()



class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self,event):
        print('connected',event)
        user = self.scope['user']
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        receiver = query_params.get('receiver', None)
        receiver = ' '.join([str(elem) for elem in receiver])
        print(receiver)
        receiver=await self.get_user_by_username(receiver)
        thread_id=await self.get_thread_id(user,receiver)
        chat_room = f'user_chatroom_{thread_id}'
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name,
        )
        await self.send(
            {
            'type':'websocket.accept'
            }
        )
        
        
    async def websocket_receive(self, event):
        print('receive', event)
        received_data = json.loads(event['text'])
        msg = received_data.get('message')
        sent_by_id = received_data.get('sent_by')
        send_to_id = received_data.get('send_to')
        thread_id = received_data.get('thread_id')

       # if not thread_id and self.scope['user']:
            #thread_id = await self.create_new_thread(sent_by_user,send_to_user)
            #thread_obj = await self.get_thread(thread_id)

        if not msg:
            print('Error:: empty message')
            return False

        sent_by_user = await self.get_user_object(sent_by_id)
        send_to_user = await self.get_user_object(send_to_id)
        thread_obj = await self.get_thread(thread_id)
        if not sent_by_user:
            print('Error:: sent by user is incorrect')
        if not send_to_user:
            print('Error:: send to user is incorrect')
        

        await self.create_chat_message(thread_obj, sent_by_user, msg)

        #other_user_chat_room = f'user_chatroom_{send_to_id}'
        self_user = self.scope['user']
        response = {
            'message': msg,
            'sent_by': self_user.id,
            'thread_id': thread_id
        }

        # await self.channel_layer.group_send(
        #     other_user_chat_room,
        #     {
        #         'type': 'chat_message',
        #         'text': json.dumps(response)
        #     }
        # )

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )



    async def websocket_disconnect(self,event):
        print('disconnect',event)

    async def chat_message(self, event):
        print('chat_message', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_thread(self, thread_id):
        qs = Thread.objects.filter(id=thread_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    # @database_sync_to_async
    # def create_new_thread(self,sender,receiver):
    #     thread=Thread.objects.create(first_person=sender,second_person=receiver)
    #     return thread.id

    @database_sync_to_async
    def get_thread_id(self,user,receiver):
        thread = Thread.objects.get((Q(first_person=user) | Q(second_person=user)) &(Q(first_person=receiver) | Q(second_person=receiver) ))
        return thread.id

    @database_sync_to_async
    def create_chat_message(self, thread, user, msg):
        ChatMessage.objects.create(thread=thread, user=user, message=msg)

    @database_sync_to_async
    def get_user_by_username(self,receive):
        user=User.objects.get(username=receive)
        return user