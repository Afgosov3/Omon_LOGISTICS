from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import DispatcherLoginSerializer

# Create your views here.


class DispatcherLoginView(APIView):
    """JWT login endpoint for main and regular dispatchers."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=DispatcherLoginSerializer,
        description="Login for main dispatcher and dispatcher users. Returns JWT tokens.",
        tags=["auth"],
    )
    def post(self, request, *args, **kwargs):
        serializer = DispatcherLoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role

        data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "full_name": user.get_full_name(),
            },
        }
        return Response(data, status=status.HTTP_200_OK)


class MeView(APIView):
    """Simple endpoint to verify JWT auth for dispatchers."""

    @extend_schema(tags=["auth"], description="Return current authenticated user profile.")
    def get(self, request, *args, **kwargs):
        user = request.user
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "role": getattr(user, "role", None),
                "full_name": user.get_full_name() if user.is_authenticated else "",
            }
        )
