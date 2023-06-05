from rest_framework .views import APIView
from django.http import HttpResponse
from . serializers import UserSerializer, LoginSerializer
from user_app. models import User
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from rest_framework import status

# Create your views here.


class Home(APIView):
    def get(self, request):
        return HttpResponse("test")


class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = User.objects.get(email=serializer.data['email'])
            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user_id': user.pk,
                    'email': user.email
                })
            return Response(serializer.data)
        else:
            return Response("User Already Exists")


class LoginView(APIView):
    def post(self, request):
        email = self.request.data["email"]
        password = self.request.data["password"]
        user = User.objects.get(email=email)
        if user.check_password(password):
            serializer = LoginSerializer(user)
            return Response(serializer.data)
        return Response("You have not signed up! Please sign up first.", status=status.HTTP_401_UNAUTHORIZED)
