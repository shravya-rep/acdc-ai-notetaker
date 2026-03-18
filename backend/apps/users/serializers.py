from rest_framework import serializers
from .models import User, UserPreference


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ["skip_patterns", "reminder_days_before", "email_recaps"]


class UserSerializer(serializers.ModelSerializer):
    preferences = UserPreferenceSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "microsoft_id", "preferences"]
        read_only_fields = ["id", "microsoft_id"]
