from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, SignUpSerializer,TeamSerializer
from .models import User, Team
from django.db.models import Q
from geopy.distance import geodesic
import logging


def get_auth_for_user(user):
	tokens = RefreshToken.for_user(user)
	return {
		'user': UserSerializer(user).data,
		'tokens': {
			'access': str(tokens.access_token),
			'refresh': str(tokens),
		}
	}


class SignInView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		username = request.data.get('username')
		password = request.data.get('password')
		if not username or not password:
			return Response(status=400)
		
		user = authenticate(username=username, password=password)
		if not user:
			return Response(status=401)

		user_data = get_auth_for_user(user)

		return Response(user_data)


class SignUpView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		new_user = SignUpSerializer(data=request.data)
		new_user.is_valid(raise_exception=True)
		user = new_user.save()

		user_data = get_auth_for_user(user)

		return Response(user_data)


class Team(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        target_location = 'dharmapuri'
        target_disaster_type = 'earthquake'
        severity_level = 'low'
        target_latitude = 12.09650
        target_longitude = 79.273400
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

        return JsonResponse({'team_members': team_members})


