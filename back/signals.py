from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Member, Riddle

@receiver(post_save, sender=User)
def create_member_for_user(sender, instance, created, **kwargs):
    if created:
        member = Member.objects.create(user=instance)
        # Set all riddles in locked_riddles
        riddles_to_lock = Riddle.objects.exclude(id=2) # Exclude the first riddle (id=2)
        member.locked_riddles.set(riddles_to_lock)