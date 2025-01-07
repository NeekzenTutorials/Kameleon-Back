from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Member

@receiver(post_save, sender=User)
def create_member_for_user(sender, instance, created, **kwargs):
    if created:
        Member.objects.create(user=instance)