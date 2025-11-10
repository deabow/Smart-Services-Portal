from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, min_length=8)
	national_id = serializers.CharField(max_length=14, min_length=14)

	class Meta:
		model = User
		fields = ("id", "username", "email", "full_name", "phone", "address", "national_id", "password")
	
	def validate_national_id(self, value):
		if not value.isdigit():
			raise serializers.ValidationError("الرقم القومي يجب أن يحتوي على أرقام فقط")
		if len(value) != 14:
			raise serializers.ValidationError("الرقم القومي يجب أن يكون 14 رقم")
		return value

	def create(self, validated_data):
		password = validated_data.pop("password")
		user = User(**validated_data)
		user.set_password(password)
		user.save()
		return user


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ("id", "username", "email", "full_name", "phone", "address", "national_id")

