from rest_framework import serializers
from .models import ChatRoom, Message, ChatRequest, ChatBotResponse


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'message_type', 'is_read', 'created_at']


class ChatRoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'user', 'is_active', 'created_at', 'updated_at', 'messages']


class ChatRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRequest
        fields = ['id', 'suggested_title', 'suggested_description', 'status', 'user_approved', 'created_at']


class ChatBotResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatBotResponse
        fields = ['id', 'keyword', 'response', 'action_type', 'is_active']
