from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

############################################################################################################################
# region Users

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")
        
        email = self.normalize_email(email)
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
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    last_connection = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    rank = models.ForeignKey('Rank', on_delete=models.SET_NULL, null=True, blank=True)
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
    
    def __str__(self):
        return f"{self.user.username} - Score: {self.member_score}"
    
    
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

    def __str__(self):
        return self.rank_name
    
# endregion
########################################################################################################
# region Riddle

class Riddle(models.Model):
    
    RIDDLE_MODE_CHOICES = [
        ('solo', 'Solo'),
        ('versus', 'Versus'),
    ]
    
    riddle_id = models.AutoField(primary_key=True)
    riddle_type = models.CharField(max_length=50)
    riddle_variable = models.TextField()
    riddle_response = models.TextField()
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
    

class Clue(models.Model):
    clue_id = models.AutoField(primary_key=True)
    clue_text = models.TextField()
    riddle = models.ForeignKey('Riddle', on_delete=models.CASCADE)

    def __str__(self):
        return f"Clue {self.clue_id} for Riddle {self.riddle.riddle_id}"



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
    clan_name = models.CharField(max_length=100)
    clan_elo = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.clan_name

# endregion
########################################################################################################
# region Play

class Resolve(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    riddle = models.ForeignKey(Riddle, on_delete=models.CASCADE)
    clue_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} resolved Riddle {self.riddle.riddle_id}"


class Compete(models.Model):
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE)
    riddle = models.ForeignKey(Riddle, on_delete=models.CASCADE)
    clue_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Clan {self.clan.clan_name} competes on Riddle {self.riddle.riddle_id}"
    
# endregion




