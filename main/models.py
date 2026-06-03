from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator

class UserManager(BaseUserManager):
    def create_user(self, email, phone, password=None):
        if not email:
            raise ValueError('Email обязателен!')
        user = self.model(email=self.normalize_email(email), phone = phone)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, phone, password=None):
        user = self.create_user(email, phone, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    phone_regex = RegexValidator(regex=r'^(\+7|8)?\d{10}$', 
                                 message='Номер телефона должен быть в формате: "+7(8)1234567890" (12-15 цифр)')
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    phone = models.CharField(unique=True, validators=[phone_regex], max_length=17)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('phone',)

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return self.is_admin
    
    @property
    def is_staff(self):
        return self.is_admin

class Status(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название статуса')
    
    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        ordering = ('pk',)

    def __str__(self):
        return self.name

class Announcement(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    update_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления')
    author = models.ForeignKey(User, on_delete=models.CASCADE, 
                               verbose_name='Автор объявления', related_name='announcements')
    status = models.ForeignKey(Status, on_delete=models.SET_DEFAULT, default=1, verbose_name='Статус')
    title = models.CharField(max_length=50, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ('status', '-update_at', '-created_at',)

    def __str__(self):
        return f'Объявление от {self.author} - {self.title}'
    
class Image(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    update_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления')
    author = models.ForeignKey(User, on_delete=models.CASCADE, 
                               verbose_name='Автор изображения', related_name='image_author')
    image = models.ImageField(upload_to='announcements/%Y/%m/%d/', verbose_name='Изображение')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, 
                                     verbose_name='Объявление', related_name='images')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        ordering = ('announcement', '-update_at', '-created_at',)

    def __str__(self):
        return f'Изображение #{self.pk} для объявления {self.announcement.title}'

