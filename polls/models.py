from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify  # Needed for slug generation
import uuid  # Needed for unique identifiers

class Poll(models.Model):
    question = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_closed = models.BooleanField(default=False)
    # Keeping this field as it was present in your migration history
    expires_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Automatically generate a unique slug from the question if one doesn't exist.
        This prevents the NoReverseMatch error during redirection.
        """
        if not self.slug:
            base_slug = slugify(self.question)
            # If slugify results in an empty string (e.g., non-latin characters), 
            # use a fallback name.
            if not base_slug:
                base_slug = "poll"
            # Append a short unique ID to ensure the slug is unique in the database.
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def total_votes(self):
        return sum(option.vote_count for option in self.options.all())

class Option(models.Model):
    poll = models.ForeignKey(Poll, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    vote_count = models.IntegerField(default=0)

class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    # Re-adding the user field from your models.py
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    device_id = models.CharField(max_length=255, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)