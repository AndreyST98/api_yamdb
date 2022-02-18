from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg


class User(AbstractUser):
    bio = models.TextField(
        'Биография',
        blank=True
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    confirmation_code = models.CharField(max_length=6, default='000000')
    USERNAME_FIELD = 'username'
    USER_ROLE = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    )

    role = models.CharField(max_length=9, choices=USER_ROLE, default='user')


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class Title(models.Model):
    name = models.CharField(max_length=200, verbose_name='Произведение')
    year = models.IntegerField(null=True, blank=True, verbose_name='Год')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
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
         constraints = [ 
            models.UniqueConstraint( 
                fields=['author', 'title'], name='unique.review' 
            ) 
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
