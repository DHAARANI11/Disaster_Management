from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Connection, Message, Room,Team

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'first_name',
            'last_name',
			'email',
		    'phone_no',
		    'adhaar_no',
		    'address',
		    'pincode',
		    'organization_name',
		    'profession',
		    'organization_address',
			'lattitude',
			'longitude',
		    'location',
		    'Org_pincode',
            'password'
        ]
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
    # Clean all values, set as lowercase
        username = validated_data['username'].lower()
        first_name = validated_data['first_name'].lower()
        last_name = validated_data['last_name'].lower()
        email = validated_data.get('email')
        phone_no = validated_data.get('phone_no')
        adhaar_no = validated_data.get('adhaar_no')
        address = validated_data.get('address')
        pincode = validated_data.get('pincode')
        organization_name = validated_data.get('organization_name')	
        organization_address=validated_data.get('organization_address')
        profession= validated_data.get('profession')
        lattitude=validated_data.get('lattitude')
        longitude=validated_data.get('longitude')
        location = validated_data.get('location')
        Org_pincode = validated_data.get('Org_pincode')

			

        # Create new user
        user = get_user_model().objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
			email=email,
			phone_no=phone_no,
			adhaar_no=adhaar_no,
			address=address,
			pincode=pincode,
			organization_address=organization_address,
			organization_name=organization_name,
			profession=profession,
			lattitude=lattitude,
			longitude=longitude,
			location=location,
			Org_pincode=Org_pincode
        )

        # Use set_password method
        user.set_password(validated_data['password'])

        user.save()
        return user



class UserSerializer(serializers.ModelSerializer):
	name = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = [
			'username',
            'name',
			'email',
			'phone_no',
			'adhaar_no',
			'address',
			'pincode',
			'organization_name',
			'profession',
			'organization_address',
			'lattitude',
			'longitude',
			'location',
			'Org_pincode',
			'thumbnail'
		]

	def get_name(self, obj):
		fname = obj.first_name.capitalize()
		lname = obj.last_name.capitalize()
		return fname + ' ' + lname

class SearchSerializer(UserSerializer):
	status = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = [
			'username',
			'name',
			'location',
			'profession',
			'thumbnail',
			'status'
		]
	
	def get_status(self, obj):
		if obj.pending_them:
			return 'pending-them'
		elif obj.pending_me:
			return 'pending-me'
		elif obj.connected:
			return 'connected'
		return 'no-connection'


class RequestSerializer(serializers.ModelSerializer):
	sender = UserSerializer()
	receiver = UserSerializer()

	class Meta:
		model = Connection
		fields = [
			'id',
			'sender',
			'receiver',
			'created'
		]


class FriendSerializer(serializers.ModelSerializer):
	friend = serializers.SerializerMethodField()
	preview = serializers.SerializerMethodField()
	updated = serializers.SerializerMethodField()
	
	class Meta:
		model = Connection
		fields = [
			'id',
			'friend',
			'preview',
			'updated'
		]

	def get_friend(self, obj):
		# If Im the sender
		if self.context['user'] == obj.sender:
			return UserSerializer(obj.receiver).data
		# If Im the receiver
		elif self.context['user'] == obj.receiver:
			return UserSerializer(obj.sender).data
		else:
			print('Error: No user found in friendserializer')

	def get_preview(self, obj):
		default = 'New connection'
		if not hasattr(obj, 'latest_text'):
			return default
		return obj.latest_text or default

	def get_updated(self, obj):
		if not hasattr(obj, 'latest_created'):
			date = obj.updated
		else:
			date = obj.latest_created or obj.updated
		return date.isoformat()


class MessageSerializer(serializers.ModelSerializer):
	is_me = serializers.SerializerMethodField()

	class Meta:
		model = Message
		fields = [
			'id',
			'is_me',
			'text',
			'created'
		]

	def get_is_me(self, obj):
		return self.context['user'] == obj.user


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['uuid', 'client', 'agent', 'messages', 'url', 'status', 'created_at']


class GroupMessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='user.username', read_only=True)
    is_sender = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'created', 'is_sender']

    def get_is_sender(self, obj):
        return self.context['user'].username == obj.user.username

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
			'username',
			'latitude',
			'longitude',
			'disaster_type',
		]