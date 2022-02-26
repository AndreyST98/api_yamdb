from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validator


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **kwargs):
        if not username:
            raise ValueError('Нужно указать название учётной записи')
        if username == 'me':
            raise ValueError('Такую учётную запись нельзя создать')
        if not email:
            raise ValueError('Не заполнен e-mail')
        user = self.model(username=username, email=email, **kwargs)
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
        user.role = user.ADMIN
        user.set_password(password)
        user.save()
        return user


class User(AbstractUser):

    DEFAULT_USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    USER_ROLES = [
        (DEFAULT_USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    ]

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
    password = models.CharField(default='password', max_length=128)
    role = models.CharField(
        max_length=9, choices=USER_ROLES, default=DEFAULT_USER)

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    objects = CustomUserManager()


class Genre(models.Model):
    """Модель жанров произведений."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'genre'
        verbose_name_plural = 'genres'


class Category(models.Model):
    """Модель категорий произведений."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'


class Title(models.Model):
    name = models.CharField(verbose_name='name',
                            db_index=True, max_length=100)
    year = models.IntegerField('composition_year',
                               validators=[validator],
                               default=None)
    description = models.TextField(
        null=True, blank=True, verbose_name='description')
    genre = models.ManyToManyField(Genre, related_name='titles', blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'


class Review(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews')
    score = models.IntegerField(
        validators=[
            MinValueValidator(1, message='Меньше одного балла ставить нельзя'),
            MaxValueValidator(10, message='Больше 10 ставить нельзя')])
    pub_date = models.DateTimeField(auto_now_add=True)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews')

    class Meta:
        ordering = ('pub_date',)
        constraints = [models.UniqueConstraint(
                       fields=['author', 'title'], name='unique.review')
                       ]


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
