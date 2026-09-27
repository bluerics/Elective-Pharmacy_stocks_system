
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Account
from .serializers import AccountSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):

        username = request.data.get('username')
        password = request.data.get('password')



        if not username or not password:
            return Response(
                {
                    'error': 'Username and password are required.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


        user = authenticate(
            username=username,
            password=password
        )


        if user is None:
            return Response(
                {
                    'error': 'Invalid username or password.'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )


        if not user.is_active:
            return Response(
                {
                    'error': 'Account is inactive.'
                },
                status=status.HTTP_403_FORBIDDEN
            )


        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'message': 'Login successful',

                'refresh': str(refresh),

                'access': str(refresh.access_token),

                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'role': user.role
                }
            },
            status=status.HTTP_200_OK
        )


class AccountView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):


        if request.user.role != 'ADMIN':
            return Response(
                {
                    'error': 'Only administrators can access accounts.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        accounts = Account.objects.all()

        serializer = AccountSerializer(
            accounts,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):


        if request.user.role != 'ADMIN':
            return Response(
                {
                    'error': 'Only administrators can create accounts.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AccountSerializer(
            data=request.data
        )

        if serializer.is_valid():

            account = serializer.save()

            return Response(
                AccountSerializer(account).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = AccountSerializer(
            request.user
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
