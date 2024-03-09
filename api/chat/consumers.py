import base64
import json

from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import  ContentFile
from django.db.models import Q, Exists, OuterRef
from django.db.models.functions import Coalesce
from django.utils.timesince import timesince
from .models import User, Connection, Message, Room
from geopy.distance import geodesic

from .serializers import (
	UserSerializer, 
	SearchSerializer, 
	RequestSerializer, 
	FriendSerializer,
	MessageSerializer,
	RoomSerializer
)


class ChatConsumer(WebsocketConsumer):

	
	def connect(self):
		user = self.scope['user']
		print(user, user.is_authenticated)

		if not user.is_authenticated:
			return
		# Save username to use as a group name for this user
		self.username = user.username
		# Join this user to a group with their username
		async_to_sync(self.channel_layer.group_add)(
			self.username, self.channel_name
		)
		self.accept()

	def disconnect(self, close_code):
		# Leave room/group
		async_to_sync(self.channel_layer.group_discard)(
			self.username, self.channel_name
		)

	#    Handle requests

	def receive(self, text_data):
		# Receive message from websocket
		data = json.loads(text_data)
		data_source = data.get('source')

		# Pretty print  python dict
		print('receive', json.dumps(data, indent=2))

		# Get friend list
		if data_source == 'friend.list':
			self.receive_friend_list(data)

		# Message List
		elif data_source == 'message.list':
			self.receive_message_list(data)

		# Message has been sent
		elif data_source == 'message.send':
			self.receive_message_send(data)

		# User is typing message
		elif data_source == 'message.type':
			self.receive_message_type(data)

		# Accept friend request
		elif data_source == 'request.accept':
			self.receive_request_accept(data)

		# Make friend request
		elif data_source == 'request.connect':
			self.receive_request_connect(data)

		# Get request list
		elif data_source == 'request.list':
			self.receive_request_list(data)

		# Search / filter users
		elif data_source == 'search':
			self.receive_search(data)

		# Thumbnail upload
		elif data_source == 'thumbnail':
			self.receive_thumbnail(data)



	def receive_friend_list(self, data):
		user = self.scope['user']
		# Latest message subquery
		latest_message = Message.objects.filter(
			connection=OuterRef('id')
		).order_by('-created')[:1]
		# Get connections for user
		connections = Connection.objects.filter(
			Q(sender=user) | Q(receiver=user),
			accepted=True
		).annotate(
			latest_text   =latest_message.values('text'),
			latest_created=latest_message.values('created')
		).order_by(
			Coalesce('latest_created', 'updated').desc()
		)
		serialized = FriendSerializer(
			connections, 
			context={ 
				'user': user 
			}, 
			many=True)
		# Send data back to requesting user
		self.send_group(user.username, 'friend.list', serialized.data)



	def receive_message_list(self, data):
		user = self.scope['user']
		connectionId = data.get('connectionId')
		page = data.get('page')
		page_size = 15
		try:
			connection = Connection.objects.get(id=connectionId)
		except Connection.DoesNotExist:
			print('Error: couldnt find connection')
			return
		# Get messages
		messages = Message.objects.filter(
			connection=connection
		).order_by('-created')[page * page_size:(page + 1) * page_size]
		# Serialized message
		serialized_messages = MessageSerializer(
			messages,
			context={ 
				'user': user 
			}, 
			many=True
		)
		# Get recipient friend
		recipient = connection.sender
		if connection.sender == user:
			recipient = connection.receiver
		
		# Serialize friend
		serialized_friend = UserSerializer(recipient)

		# Count the total number of messages for this connection
		messages_count = Message.objects.filter(
			connection=connection
		).count()

		next_page = page + 1 if messages_count > (page + 1 ) * page_size else None

		data = {
			'messages': serialized_messages.data,
			'next': next_page,
			'friend': serialized_friend.data
		}
		# Send back to the requestor
		self.send_group(user.username, 'message.list', data)



	def receive_message_send(self, data):
		user = self.scope['user']
		connectionId = data.get('connectionId')
		message_text = data.get('message')
		try:
			connection = Connection.objects.get(id=connectionId)
		except Connection.DoesNotExist:
			print('Error: couldnt find connection')
			return
		
		message = Message.objects.create(
			connection=connection,
			user=user,
			text=message_text
		)

		# Get recipient friend
		recipient = connection.sender
		if connection.sender == user:
			recipient = connection.receiver

		# Send new message back to sender
		serialized_message = MessageSerializer(
			message,
			context={
				'user': user
			}
		)
		serialized_friend = UserSerializer(recipient)
		data = {
			'message': serialized_message.data,
			'friend': serialized_friend.data
		}
		self.send_group(user.username, 'message.send', data)

		# Send new message to receiver
		serialized_message = MessageSerializer(
			message,
			context={
				'user': recipient
			}
		)
		serialized_friend = UserSerializer(user)
		data = {
			'message': serialized_message.data,
			'friend': serialized_friend.data
		}
		self.send_group(recipient.username, 'message.send', data)



	def receive_message_type(self, data):
		user = self.scope['user']
		recipient_username = data.get('username')
		data = {
			'username': user.username
		}
		self.send_group(recipient_username, 'message.type', data)



	def receive_request_accept(self, data):
		username = data.get('username')
		# Fetch connection object
		try:
			connection = Connection.objects.get(
				sender__username=username,
				receiver=self.scope['user']
			)
		except Connection.DoesNotExist:
			print('Error: connection  doesnt exists')
			return
		# Update the connection
		connection.accepted = True
		connection.save()
		
		serialized = RequestSerializer(connection)
		# Send accepted request to sender
		self.send_group(
			connection.sender.username, 'request.accept', serialized.data
		)
		# Send accepted request to receiver
		self.send_group(
			connection.receiver.username, 'request.accept', serialized.data
		)

		# Send new friend object to sender
		serialized_friend = FriendSerializer(
			connection,
			context={
				'user': connection.sender
			}
		)
		self.send_group(
			connection.sender.username, 'friend.new', serialized_friend.data)

		# Send new friend object to receiver
		serialized_friend = FriendSerializer(
			connection,
			context={
				'user': connection.receiver
			}
		)
		self.send_group(
			connection.receiver.username, 'friend.new', serialized_friend.data)



	def receive_request_connect(self, data):
		username = data.get('username')
		# Attempt to fetch the receiving user
		try:
			receiver = User.objects.get(username=username)
		except User.DoesNotExist:
			print('Error: User not found')
			return
		# Create connection
		connection, _ = Connection.objects.get_or_create(
			sender=self.scope['user'],
			receiver=receiver
		)
		# Serialized connection
		serialized = RequestSerializer(connection)
		# Send back to sender
		self.send_group(
			connection.sender.username, 'request.connect', serialized.data
		)
		# Send to receiver
		self.send_group(
			connection.receiver.username, 'request.connect', serialized.data
		)



	def receive_request_list(self, data):
		user = self.scope['user']
		# Get connection made to this  user
		connections = Connection.objects.filter(
			receiver=user,
			accepted=False
		)
		serialized = RequestSerializer(connections, many=True)
		# Send requests lit back to this userr
		self.send_group(user.username, 'request.list', serialized.data)


		
	def receive_search(self, data):
		query = data.get('query')
		# Get users from query search term
		users = User.objects.filter(
			Q(username__istartswith=query)   |
			Q(first_name__istartswith=query) |
			Q(last_name__istartswith=query)|
			Q(location__istartswith=query)|
			Q(profession__istartswith=query)
		).exclude(
			username=self.username
		).annotate(
			pending_them=Exists(
				Connection.objects.filter(
					sender=self.scope['user'],
					receiver=OuterRef('id'),
					accepted=False
				)
			),
			pending_me=Exists(
				Connection.objects.filter(
					sender=OuterRef('id'),
					receiver=self.scope['user'],
					accepted=False
				)
			),
			connected=Exists(
				Connection.objects.filter(
					Q(sender=self.scope['user'], receiver=OuterRef('id')) |
					Q(receiver=self.scope['user'], sender=OuterRef('id')),
					accepted=True
				)
			)
		)
		# serialize results
		serialized = SearchSerializer(users, many=True)
		# Send search results back to this user
		self.send_group(self.username, 'search', serialized.data)



	def receive_thumbnail(self, data):
		user = self.scope['user']
		# Convert base64 data  to django content file
		image_str = data.get('base64')
		image = ContentFile(base64.b64decode(image_str))
		# Update thumbnail field
		filename = data.get('filename')
		user.thumbnail.save(filename, image, save=True)
		# Serialize user
		serialized = UserSerializer(user)
		# Send updated user data including new thumbnail 
		self.send_group(self.username, 'thumbnail', serialized.data)


	#   Catch/all broadcast to client helpers

	def send_group(self, group, source, data):
		response = {
			'type': 'broadcast_group',
			'source': source,
			'data': data
		}
		async_to_sync(self.channel_layer.group_send)(
			group, response
		)

	def broadcast_group(self, data):
		'''
		data:
			- type: 'broadcast_group'
			- source: where it originated from
			- data: what ever you want to send as a dict
		'''
		#data.pop('type')
		'''
		return data:
			- source: where it originated from
			- data: what ever you want to send as a dict
		'''
		self.send(text_data=json.dumps(data))
'''
	@sync_to_async 
	def get_room(self):
		self.room = Room.objects.get(uuid=self.room_name)

    
	@sync_to_async
	def set_room_closed(self):
		self.room = Room.objects.get(uuid=self.room_name)
		self.room.status = Room.CLOSED
		self.room.save()

    
	@sync_to_async
	def create_message(self, sent_by, message, agent):
		message = Message.objects.create(body=message, sent_by=sent_by)
	    
		if agent:
			message.created_by = User.objects.get(pk=agent)
			message.save()
		self.room.messages.add(message)
    
	    
		return message


'''

class TeamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # Receive the message from the client (if needed)
        data = json.loads(text_data)

        # Get the team data based on the received message
        team_data = await self.get_team_data(data)

        # Send the team data back to the client
        await self.send_team_data(team_data)

    @sync_to_async
    def get_team_data(self, data):
        target_location = data.get('target_location')
        target_disaster_type = data.get('target_disaster_type')
        severity_level = data.get('severity_level')
        target_latitude = data.get('target_latitude')
        target_longitude = data.get('target_longitude')

        users = User.objects.filter()

        if severity_level == 'low':
            if target_disaster_type == 'earthquake':
                needed_professions = {
                    'doctor': 2,
                    'nurse': 5,
                    'police': 5,
                    'ambulance': 3,
                    'rescue_worker': 2,
                    'engineer': 2,
                    'geologist': 2
                }
                min_threshold_distance = 10
        elif severity_level == 'medium':
            needed_professions = {
                'doctor': 4,
                'nurse': 10,
                'police': 8,
                'ambulance': 5,
                'rescue_worker': 7
            }
            min_threshold_distance = 20
        elif severity_level == 'high':
            needed_professions = {
                'doctor': 6,
                'nurse': 15,
                'police': 12,
                'ambulance': 8,
                'rescue_worker': 9
            }
            min_threshold_distance = 30
        else:
            needed_professions = {
                'doctor': 3,
                'nurse': 8,
                'police': 6,
                'ambulance': 4
            }
            min_threshold_distance = 10

        team_members = []
        threshold_distance = min_threshold_distance
        for profession, count in needed_professions.items():
            users_of_profession = users.filter(profession=profession)[:count]
            for user in users_of_profession:
                user_latitude = user.latitude
                user_longitude = user.longitude
                distance = geodesic((target_latitude, target_longitude), (user_latitude, user_longitude)).kilometers
                if distance <= threshold_distance:
                    team_members.append({
                        'name': user.username,
                        'location': user.location,
                        'profession': user.profession,
                        'phone_no': user.phone_no
                    })
            else:
                threshold_distance *= 10

        return team_members

    async def send_team_data(self, team_data):
        await self.send(text_data=json.dumps({'team_members': team_data}))


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.username = self.scope['user'].username
        self.location = self.scope['user'].profile.location  # Assuming location data is stored in the user's profile

        # Join room/group based on location
        await self.channel_layer.group_add(
            f"{self.group_name}_{self.location}",
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room/group
        await self.channel_layer.group_discard(
            f"{self.group_name}_{self.location}",
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']

        if message_type == 'send_message':
            await self.send_group_message(data['message'])

    async def send_group_message(self, message):
        # Broadcast message to everyone in the group
        await self.channel_layer.group_send(
            f"{self.group_name}_{self.location}",
            {
                'type': 'group_message',
                'message': message,
                'username': self.username
            }
        )

    async def group_message(self, event):
        # Send message to WebSocket
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'type': 'group_message',
            'message': message,
            'username': username
        }))

