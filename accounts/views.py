from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserRegistrationSerializer, UserLoginSerializer
from .models import CustomUser


# ── HTML VIEW ──────────────────────────────────────────────────────────────
def register_page(request):
    """Render registration page & handle form POST."""
    if request.user.is_authenticated:
        return redirect('questionnaire')

    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Account created.")
            return redirect('questionnaire')
        else:
            for field, errs in serializer.errors.items():
                for err in errs:
                    messages.error(request, f"{field}: {err}")

    return render(request, 'accounts/register.html')


def login_page(request):
    """Render login page & handle form POST."""
    if request.user.is_authenticated:
        return redirect('questionnaire')

    if request.method == 'POST':
        serializer = UserLoginSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('questionnaire')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/login.html')


def logout_view(request):
    """Log out and redirect to login."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ── REST API ────────────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {'message': 'User registered successfully.', 'role': user.role},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        return Response({'message': 'Login successful.', 'username': user.username, 'role': user.role})
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    logout(request)
    return Response({'message': 'Logged out successfully.'})
