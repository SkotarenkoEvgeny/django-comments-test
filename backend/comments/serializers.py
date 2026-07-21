import re
import xml.etree.ElementTree as ET
from io import BytesIO

import bleach
from rest_framework import serializers
from PIL import Image
from django.core.cache import cache
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import Comment


ALLOWED_TAGS = {
    "a",
    "code",
    "i",
    "strong",
}

ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
}

ALLOWED_PROTOCOLS = {
    "http",
    "https",
    "mailto",
}


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    captcha_id = serializers.CharField(
        write_only=True,
    )

    captcha_value = serializers.CharField(
        write_only=True,
    )

    class Meta:
        model = Comment

        fields = [
            "id",
            "user_name",
            "email",
            "home_page",
            "text",
            "parent",
            "replies",
            "image",
            "text_file",
            "captcha_id",
            "captcha_value",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "replies",
        ]

    def validate_user_name(self, value):
        if not re.fullmatch(r"[A-Za-z0-9]+", value):
            raise serializers.ValidationError(
                "User Name can contain only Latin letters and numbers"
            )
        return value

    def validate_text(self, value):
        try:
            root = ET.fromstring(
                f"<root>{value}</root>"
            )

        except ET.ParseError as error:
            raise serializers.ValidationError(
                f"Invalid XHTML: {error}"
            )

        for element in root.iter():
            if element.tag == "root":
                continue

            if element.tag not in ALLOWED_TAGS:
                raise serializers.ValidationError(
                    f"HTML-tag <{element.tag}> is forbidden."
                    f"Allowed tags are: "
                    f"{', '.join(sorted(ALLOWED_TAGS))}."
                )

            allowed_attributes = ALLOWED_ATTRIBUTES.get(
                element.tag,
                set(),
            )

            for attribute in element.attrib:

                if attribute not in allowed_attributes:
                    raise serializers.ValidationError(
                        f'Атрибут "{attribute}" is forbidden.'
                        f"for tag <{element.tag}>."
                    )

        cleaned_value = bleach.clean(
            value,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols=ALLOWED_PROTOCOLS,
            strip=True,
        )

        if cleaned_value != value:
            raise serializers.ValidationError(
                "The text contains potentially unsafe HTML."
            )

        return cleaned_value


    def get_replies(self, obj):
        replies = obj.replies.all().order_by("created_at")

        return CommentSerializer(
            replies,
            many=True,
            context=self.context,
        ).data


    def validate_image(self, value):
        allowed_formats = {
            "JPEG",
            "PNG",
            "GIF",
        }

        try:
            image = Image.open(value)
            image.verify()
        except Exception:
            raise serializers.ValidationError(
                "Invalid image file."
            )

        if image.format not in allowed_formats:
            raise serializers.ValidationError(
                "Only JPG, GIF and PNG images are allowed."
            )

        value.seek(0)

        return value


    def resize_image(self, value):

        image = Image.open(value)

        image_format = image.format

        if image_format == "GIF":
            value.seek(0)
            return value

        if (
                image.width <= 320
                and image.height <= 240
        ):
            value.seek(0)
            return value


        image.thumbnail(
            (320, 240),
            Image.Resampling.LANCZOS,
        )

        if (
                image_format == "JPEG"
                and image.mode not in ("RGB", "L")
        ):
            image = image.convert("RGB")

        output = BytesIO()

        image.save(
            output,
            format=image_format,
        )

        output.seek(0)

        return InMemoryUploadedFile(
            output,
            "ImageField",
            value.name,
            value.content_type,
            output.getbuffer().nbytes,
            None,
        )

    def validate_text_file(self, value):
        max_size = 100 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "TXT file must not exceed 100 KB."
            )

        if not value.name.lower().endswith(".txt"):
            raise serializers.ValidationError(
                "Only TXT files are allowed."
            )

        return value

    def create(self, validated_data):
        captcha_id = validated_data.pop(
            "captcha_id"
        )

        validated_data.pop(
            "captcha_value"
        )

        image = validated_data.get(
            "image"
        )

        if image:
            validated_data["image"] = (
                self.resize_image(image)
            )

        comment = Comment.objects.create(
            **validated_data
        )

        cache.delete(
            f"captcha:{captcha_id}"
        )

        return comment

    def validate(self, attrs):
        captcha_id = attrs.get("captcha_id")
        captcha_value = attrs.get("captcha_value")

        expected_value = cache.get(
            f"captcha:{captcha_id}"
        )

        if expected_value is None:
            raise serializers.ValidationError({
                "captcha_value": (
                    "CAPTCHA expired or does not exist."
                )
            })

        if captcha_value != expected_value:
            raise serializers.ValidationError({
                "captcha_value": (
                    "Invalid CAPTCHA."
                )
            })

        return attrs