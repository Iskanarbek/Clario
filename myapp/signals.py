from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProgress, DifficultyLevel

@receiver(post_save, sender=User)
def create_user_progress(sender, instance, created, **kwargs):
    if created:
        # Create level 1 if it doesn't exist
        level_1, created = DifficultyLevel.objects.get_or_create(level=1)
        UserProgress.objects.create(user=instance, current_level=level_1)

@receiver(post_save, sender=User)
def save_user_progress(sender, instance, **kwargs):
    # Ensure UserProgress exists for existing users
    if not hasattr(instance, 'userprogress'):
        level_1, created = DifficultyLevel.objects.get_or_create(level=1)
        UserProgress.objects.create(user=instance, current_level=level_1)