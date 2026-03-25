from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User, UserRole


class DispatcherLoginSerializer(serializers.Serializer):
    """Login serializer for main_dispatcher and dispatcher users.

    Accepts email and password, returns nothing itself; view will issue JWT.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        request = self.context.get("request")

        user = authenticate(request=request, email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.", code="authorization")

        if user.role not in (UserRole.DISPATCHER, UserRole.MAIN_DISPATCHER):
            raise serializers.ValidationError("User is not a dispatcher.", code="authorization")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.", code="authorization")

        attrs["user"] = user
        return attrs

