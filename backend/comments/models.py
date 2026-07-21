from django.db import models

from PIL import Image

class Comment(models.Model):
    user_name = models.CharField(
        max_length=100,
    )

    email = models.EmailField()

    home_page = models.URLField(
        blank=True,
    )

    text = models.TextField()

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(
        blank=True,
    )

    image = models.ImageField(
        upload_to="comments/images/",
        null=True,
        blank=True,
    )

    text_file = models.FileField(
        upload_to="comments/files/",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.user_name}: {self.text[:50]}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.image:
            return

        image = Image.open(self.image.path)

        if image.width > 320 or image.height > 240:
            image.thumbnail(
                (320, 240),
                Image.Resampling.LANCZOS,
            )

            image.save(self.image.path)
