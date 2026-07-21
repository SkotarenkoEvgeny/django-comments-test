from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment
from .serializers import CommentSerializer
from .pagination import CommentPagination
from .captcha import generate_captcha
from .tasks import test_task


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = (
        Comment.objects
        .filter(parent__isnull=True)
    )

    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    filter_backends = [
        filters.OrderingFilter,
    ]

    ordering_fields = [
        "user_name",
        "email",
        "created_at",
    ]

    ordering = [
        "-created_at",
    ]

    def perform_create(self, serializer):
        request = self.request

        ip_address = request.META.get(
            "REMOTE_ADDR"
        )

        user_agent = request.META.get(
            "HTTP_USER_AGENT",
            "",
        )

        comment = serializer.save(
            ip_address=ip_address,
            user_agent=user_agent,
        )

        test_task.delay(comment_id=comment.id)

        channel_layer = get_channel_layer()

        async_to_sync(
            channel_layer.group_send
        )(
            "comments",
            {
                "type": "comment_created",
                "comment": CommentSerializer(
                    comment
                ).data,
            },
        )


class CaptchaView(APIView):

    def get(self, request):
        captcha = generate_captcha()

        return Response(captcha)


class ProfileView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
        })

