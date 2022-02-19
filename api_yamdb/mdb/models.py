import datetime

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg

now = datetime.datetime.now()


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **kwargs):
        if not username:
            raise ValueError('Нужно указать название учётной записи')
        if username == 'me':
            raise ValueError('Такую учётную запись нельзя создать')
        if not email:
            raise ValueError('Не заполнен e-mail')
        user = self.model(username=username, **kwargs)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **kwargs):
        if not username:
            raise ValueError('Нужно указать название учётной записи')
        if username == 'me':
            raise ValueError('Такую учётную запись нельзя создать')
        if not password:
            raise ValueError('Не заполнен пароль')
        user = self.model(
            username=username, is_staff=True, is_superuser=True, **kwargs)
        user.set_password(password)
        user.save()
        return user


class User(AbstractUser):
    bio = models.TextField(
        'Биография',
        blank=True
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    confirmation_code = models.CharField(max_length=4, default='0000')
    USERNAME_FIELD = 'username'
    USER_ROLE = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    )
    password = models.CharField(default='password', max_length=128)
    role = models.CharField(max_length=9, choices=USER_ROLE, default='user')

    objects = CustomUserManager()


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(models.Model):
    """Модель категорий произведений."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    name = models.CharField(max_length=200, verbose_name='Произведение')
    year = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(int(now.year))],
        default=None, null=True, blank=True, verbose_name='Год')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    # rating = models.IntegerField(blank=True, null=True, verbose_name='Рейтинг')
    genre = models.ManyToManyField(Genre, verbose_name='Жанр')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Категория')
    

    @property
    def rating(self):
        avg_score = self.reviews.all().aggregate(Avg('score'))
        return avg_score['score__avg']


class Review(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews')
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)])
    pub_date = models.DateTimeField(auto_now_add=True)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews')

    class Meta:
        # эта команда и не даст повторно голосовать
        unique_together = ('author', 'title')


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments")
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments")
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)
