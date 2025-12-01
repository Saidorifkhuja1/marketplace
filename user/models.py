import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

PHONE_REGEX = RegexValidator(
    regex=r"^\+998([0-9][0-9]|99)\d{7}$",
    message="Please provide a valid phone number",
)



class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, telegram_id=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email')
        if not name:
            raise ValueError('User must have a name')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            telegram_id=telegram_id,
            **extra_fields
        )
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        # Superuser uchun faqat email, name, password kerak
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'seller')
        extra_fields.setdefault('is_active', True)

        # Superuser uchun telegram_id ixtiyoriy (None bo'lishi mumkin)
        # Shuning uchun unique constraint muammosi bo'lmasligi uchun random telegram_id beramiz
        if 'telegram_id' not in extra_fields or extra_fields['telegram_id'] is None:
            # Admin uchun unique telegram_id (manfiy raqam ishlatamiz)
            import random
            extra_fields['telegram_id'] = -random.randint(1000000, 9999999)

        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('seller', 'SELLER'),
        ('client', 'CLIENT'),
    ]

    uid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=250)
    username = models.CharField(max_length=250, blank=True, null=True)
    phone_number = models.CharField(
        validators=[PHONE_REGEX],
        max_length=21,
        unique=True,
        blank=True,
        null=True
    )
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to='accounts/photos/', blank=True, null=True)
    telegram_id = models.BigIntegerField(unique=True, db_index=True, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']  # Faqat name kerak, email USERNAME_FIELD bo'lgani uchun avtomatik so'raladi

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return self.name or self.username or self.email

    @property
    def is_staff(self):
        return self.is_admin

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.is_active = True
        self.save()


class UserLoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    success = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Login History'
        verbose_name_plural = 'Login Histories'
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.user} - {self.login_time}"

