from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from math import log2

############################################################################################################################
# region Users

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', False)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)
    

class CV(models.Model):
    cv_id = models.AutoField(primary_key=True)
    cv_file = models.FileField(upload_to="cvs/")
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CV {self.cv_id}"


class User(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=50, unique=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True, default="profile_pictures/default_pp.jpg")
    last_connection = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(blank=True, null=True)
    
    cv = models.OneToOneField('CV', on_delete=models.SET_NULL, null=True, blank=True)
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    member_score = models.FloatField(default=0.0)
    member_clan_score = models.FloatField(default=0.0)
    rank = models.ForeignKey('Rank', on_delete=models.SET_NULL, null=True, blank=True)
    clan = models.ForeignKey('Clan', on_delete=models.SET_NULL, null=True, blank=True)
    is_clan_admin = models.BooleanField(default=False)
    have_calculatrice = models.BooleanField(default=False)
    
    achieved_riddles = models.ManyToManyField(
        'Riddle',
        blank=True,
        related_name='achieved_by_members',
        verbose_name="Énigmes réussies"
    )
    locked_riddles = models.ManyToManyField(
        'Riddle',
        blank=True,
        related_name='locked_by_members',
        verbose_name="Énigmes verrouillées"
    )

    achieved_coop_riddles = models.ManyToManyField(
        'Riddle',
        blank=True,
        related_name='achieved_by_coop_members',
        verbose_name="Énigmes coop réussies"
    )

    locked_coop_riddles = models.ManyToManyField(
        'Riddle',
        blank=True,
        related_name='locked_by_coop_members',
        verbose_name="Énigmes coop verrouillées"
    )

    revealed_clues = models.ManyToManyField(
        'Clue',
        blank=True,
        related_name='revealed_by_members',
        verbose_name="Indices utilisés"
    )
    
    def __str__(self):
        return f"{self.user.username} - Rank : {self.rank} - Score: {self.member_score}"
    
    def add_riddle_to_achieved(self, riddle):
        """Add a riddle to the list of achieved riddles."""
        self.achieved_riddles.add(riddle)

        all_riddles = Riddle.objects.all()
        for other_riddle in all_riddles:
            if riddle in other_riddle.riddle_dependance.all():
                if other_riddle in self.locked_riddles.all():
                    self.locked_riddles.remove(other_riddle)

        riddle_clues = Clue.objects.filter(riddle=riddle) # Get all clues of the riddle
        riddle_ids = riddle_clues.values_list('riddle_id', flat=True)
        revealed_riddle_clues = self.revealed_clues.filter(riddle__in=riddle_ids)
        revealed_clues_count = revealed_riddle_clues.count()

        # Calculate the percentage of points to add depending on the number of revealed clues
        if revealed_clues_count == 1:
            percentage = 0.75
        elif revealed_clues_count == 2:
            percentage = 0.5
        elif revealed_clues_count == 3:
            percentage = 0.25
        else:
            percentage = 1.0

        self.member_score += riddle.riddle_points * percentage
        self.update_rank_according_to_score()
        self.save()

    def add_coop_riddle_to_achieved(self, riddle):
        """Add a riddle to the list of achieved coop riddles."""
        self.achieved_coop_riddles.add(riddle)

        all_riddles = Riddle.objects.all()
        for other_riddle in all_riddles:
            if riddle in other_riddle.riddle_dependance.all():
                if other_riddle in self.locked_coop_riddles.all():
                    self.locked_coop_riddles.remove(other_riddle)

        riddle_clues = Clue.objects.filter(riddle=riddle)
        riddle_ids = riddle_clues.values_list('riddle_id', flat=True)
        revealed_riddle_clues = self.revealed_clues.filter(riddle__in=riddle_ids)
        revealed_clues_count = revealed_riddle_clues.count()

        if revealed_clues_count == 1:
            percentage = 0.75
        elif revealed_clues_count == 2:
            percentage = 0.5
        elif revealed_clues_count == 3:
            percentage = 0.25
        else:
            percentage = 1.0

        self.member_clan_score += riddle.riddle_points * percentage
        self.save()
        
    def update_rank_according_to_score(self):
        new_rank = (
            Rank.objects.filter(min_score__lte=self.member_score)
            .order_by("-min_score")  # tri descendant
            .first()
        )
        
        if new_rank and new_rank != self.rank:
            self.rank = new_rank
            self.save()

    def lock_riddle(self, riddle):
        """Add a riddle to the list of locked riddles."""
        if riddle not in self.achieved_riddles.all():
            self.locked_riddles.add(riddle)
    
    
class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"Recruteur : {self.user.username}"
    

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"Admin : {self.user.username}"
    
# endregion    
########################################################################################################
# region Rank
    
    
class Rank(models.Model):
    rank_id = models.AutoField(primary_key=True)
    rank_name = models.CharField(max_length=50)
    rank_image = models.ImageField(upload_to="rank_images/", blank=True, null=True)
    
    min_score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.rank_name
    
# endregion
########################################################################################################
# region Riddle

class Riddle(models.Model):
    
    RIDDLE_MODE_CHOICES = [
        ('solo', 'Solo'),
        ('coop', 'Coop'),
    ]
    
    riddle_id = models.AutoField(primary_key=True)
    riddle_type = models.CharField(max_length=50)
    riddle_variable = models.TextField()
    riddle_response = models.JSONField()
    riddle_difficulty = models.IntegerField()
    riddle_theme = models.CharField(max_length=100)
    riddle_points = models.IntegerField()
    riddle_path = models.CharField(max_length=50, blank=True, null=True)
    riddle_dependance = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='dependent_riddles',
        verbose_name="Dépendances de l'énigme"
    )
    riddle_mode = models.CharField(
        max_length=10,
        choices=RIDDLE_MODE_CHOICES,
        default='solo',
    )

    def __str__(self):
        return f"Riddle {self.riddle_id} ({self.riddle_theme})"
    

class MemberRiddleStats(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="riddle_stats")
    riddle = models.ForeignKey(Riddle, on_delete=models.CASCADE, related_name="member_stats")
    try_count = models.PositiveIntegerField(default=0, verbose_name="Nombre d'essais")
    errors_count = models.PositiveIntegerField(default=0, verbose_name="Nombre d'erreurs")
    solve_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de résolutions")
    first_solved_at = models.DateTimeField(null=True, blank=True, verbose_name="Première résolution")
    is_solved = models.BooleanField(default=False, verbose_name="Résolue")

    class Meta:
        unique_together = ("member", "riddle")  # Un membre ne peut avoir qu'une seule entrée par énigme
        verbose_name = "Statistiques Membre-Énigme"
        verbose_name_plural = "Statistiques Membre-Énigmes"

    def __str__(self):
        return f"{self.member.user.username} - {self.riddle.riddle_id} (Résolue : {self.is_solved})"

    def mark_solved(self):
        """Marque l'énigme comme résolue et met à jour les statistiques associées."""
        if not self.is_solved:
            self.is_solved = True
            self.first_solved_at = now()
        self.solve_count += 1
        self.save()

    def increment_errors(self):
        """Incrémente le compteur d'erreurs."""
        self.errors_count += 1
        self.save()

    def increment_tries(self):
        """Incrémente le compteur d'essais."""
        self.try_count += 1
        self.save()
    

class Clue(models.Model):
    clue_id = models.AutoField(primary_key=True)
    clue_text = models.TextField()
    riddle = models.ForeignKey('Riddle', on_delete=models.CASCADE)

    def __str__(self):
        return f"Clue {self.clue_id} for Riddle {self.riddle.riddle_id}"
    

class Resolve(models.Model):
    resolve_id = models.AutoField(primary_key=True)
    member = models.ForeignKey('Member', on_delete=models.CASCADE, related_name="resolves", null=True, blank=True)
    riddle = models.ForeignKey('Riddle', on_delete=models.CASCADE, related_name="resolves", null=True, blank=True)
    time_used = models.DurationField()  # Durée utilisée pour résoudre l'énigme
    attempts = models.PositiveIntegerField(default=0)  # Nombre d'essais
    completed_at = models.DateTimeField(blank=True, null=True)  # Date de résolution (si résolue)
    is_successful = models.BooleanField(default=False)  # Statut de réussite

    def __str__(self):
        return f"Resolve: {self.member.user.username} -> {self.riddle.riddle_id}"

    def mark_successful(self):
        """
        Marque cette résolution comme réussie, enregistre la date et met à jour les données liées.
        """
        self.is_successful = True
        self.completed_at = now()
        self.save()
        
        # Ajouter l'énigme aux énigmes résolues du membre
        self.member.add_riddle_to_achieved(self.riddle)


class SoloRiddle(models.Model):
    riddle = models.OneToOneField(Riddle, on_delete=models.CASCADE, primary_key=True)
    riddle_image = models.ImageField(upload_to="solo_riddles/", blank=True, null=True)

    def __str__(self):
        return f"Solo Riddle {self.riddle.riddle_id}"



class VersusRiddle(models.Model):
    riddle = models.OneToOneField(Riddle, on_delete=models.CASCADE, primary_key=True)
    versus_nb_step = models.IntegerField()

    def __str__(self):
        return f"Versus Riddle {self.riddle.riddle_id}"
    
    
class VersusRiddleImage(models.Model):
    image_id = models.AutoField(primary_key=True)
    image_path = models.ImageField(upload_to="versus_riddles/")
    image_step = models.IntegerField()
    riddle = models.ForeignKey(VersusRiddle, on_delete=models.CASCADE)

    def __str__(self):
        return f"Image {self.image_id} for Versus Riddle {self.riddle.riddle_id}"

    

class HasImage(models.Model):
    riddle = models.ForeignKey(Riddle, on_delete=models.CASCADE)
    image = models.ForeignKey(VersusRiddleImage, on_delete=models.CASCADE)

    def __str__(self):
        return f"Riddle {self.riddle.riddle_id} has Image {self.image.image_id}"

# endregion
########################################################################################################
# region Clan

class Clan(models.Model):
    clan_id = models.AutoField(primary_key=True)
    clan_name = models.CharField(max_length=100, unique=True)
    clan_bio = models.TextField(blank=True, null=True)
    clan_pci = models.ImageField(upload_to="clan_pictures/", blank=True, null=True)
    clan_members_count = models.PositiveIntegerField(default=0)
    clan_members_max_count = models.PositiveIntegerField(default=10)
    clan_elo = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.clan_name
    
    def update_elo(self):
        """
        Met à jour l'élo du clan en fonction des scores des membres.
        """
        members = self.Member.objects.filter(clan=self)  # Récupérer les membres liés à ce clan
        members_count = members.count()
        if members_count == 0:
            self.clan_elo = 0.0  # Aucun membre, pas d'élo
        else:
            total_score = sum(member.member_score for member in members)
            self.clan_elo = (total_score / members_count) * log2(members_count + 1)
        self.save()
    
class CoopInvitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Rejetée'),
    ]

    riddle = models.ForeignKey('Riddle', on_delete=models.CASCADE, related_name='coop_invitations')
    inviter = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='sent_coop_invitations')
    invitee = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='received_coop_invitations')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('riddle', 'invitee')  # Empêche les invitations multiples pour le même riddle et invitee

    def __str__(self):
        return f"Invitation de {self.inviter.user.username} à {self.invitee.user.username} pour {self.riddle.riddle_type} ({self.status})"

# endregion
########################################################################################################
# region Play


class Compete(models.Model):
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE)
    riddle = models.ForeignKey(Riddle, on_delete=models.CASCADE)
    clue_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Clan {self.clan.clan_name} competes on Riddle {self.riddle.riddle_id}"
    
# endregion




