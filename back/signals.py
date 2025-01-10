from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Member, Riddle, Rank

@receiver(post_save, sender=User)
def create_member_for_user(sender, instance, created, **kwargs):
    if created:
        member = Member.objects.create(user=instance)
        
        try:
            rank_cochon = Rank.objects.filter(rank_name="cochon").first()
            if rank_cochon:
                member.rank = rank_cochon
                member.save()
            else:
                # Optionnel : journaliser ou gérer le cas où le rang "cochon" n'existe pas
                print("Rank 'cochon' introuvable. Aucun rang attribué au membre.")
        except Rank.DoesNotExist:
            pass
        
        # Set all riddles in locked_riddles
        riddles_to_lock = Riddle.objects.exclude(riddle_id=2) # Exclude the first riddle (id=2)
        member.locked_riddles.set(riddles_to_lock)