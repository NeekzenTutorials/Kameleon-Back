# seed_data.py

import os
import django
from django.core.files import File

# Configurer Django pour accéder au projet
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kameleon_back.settings")
django.setup()

from back.models import Rank

def populate_ranks_with_images():
    ranks = [
        {"rank_name": "Cochon", "rank_image": "images/ranks/cochon.png"},
        {"rank_name": "Hibou", "rank_image": "images/ranks/hibou.png"},
        {"rank_name": "Pieuvre", "rank_image": "images/ranks/pieuvre.png"},
        {"rank_name": "Phasme", "rank_image": "images/ranks/phasme.png"},
        {"rank_name": "Poisson pierre", "rank_image": "images/ranks/poisson-pierre.png"},
        {"rank_name": "Panda Ghilie", "rank_image": "images/ranks/panda-ghillie.png"},
        {"rank_name": "Kameleon", "rank_image": "images/ranks/kameleon.png"},
    ]

    for rank_data in ranks:
        # Vérifie si le Rank existe déjà
        rank, created = Rank.objects.get_or_create(rank_name=rank_data["rank_name"])
        
        # Associe l'image si elle existe
        if created or not rank.rank_image:
            image_path = rank_data["rank_image"]
            if os.path.exists(image_path):
                with open(image_path, "rb") as img_file:
                    rank.rank_image.save(
                        os.path.basename(image_path),
                        File(img_file),
                        save=True
                    )
                print(f"Added image to rank: {rank.rank_name}")
            else:
                print(f"Image not found for rank: {rank.rank_name}")
        else:
            print(f"Rank already exists with image: {rank.rank_name}")

if __name__ == "__main__":
    populate_ranks_with_images()
