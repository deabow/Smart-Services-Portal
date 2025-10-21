from __future__ import annotations

from rest_framework import serializers

from .models import Request, RequestAttachment, RequestStatus


class RequestAttachmentSerializer(serializers.ModelSerializer):
	class Meta:
		model = RequestAttachment
		fields = ("id", "file_path")


class RequestSerializer(serializers.ModelSerializer):
	attachments = RequestAttachmentSerializer(many=True, read_only=True)
	status_name = serializers.CharField(source="status.name", read_only=True)

	class Meta:
		model = Request
		fields = (
			"id",
			"user",
			"full_name",
			"phone",
			"address",
			"title",
			"description",
			"status",
			"status_name",
			"tracking_number",
			"created_at",
			"attachments",
		)
		read_only_fields = ("tracking_number", "created_at")

