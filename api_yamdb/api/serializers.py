from mdb.models import Category, Comment, Genre, Review, Title, User
from rest_framework import serializers
from .fields import CreatableSlugRelatedField


class CreatableSlugRelatedField(serializers.SlugRelatedField):

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(id=data)
        except (TypeError, ValueError):
            self.fail('invalid')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'email', 'role',)
        model = User


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return obj.rating

    class Meta:
        fields = '__all__'
        model = Title


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Жанров"""
    class Meta:
        fields = '__all__'
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Категорий"""
    class Meta:
        fields = '__all__'
        model = Category


class ReviewSerializer(serializers.ModelSerializer):

    author = CreatableSlugRelatedField(
        queryset=User.objects.all(), required=False, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        model = Review


class CommentSerializer(serializers.ModelSerializer):

    author = CreatableSlugRelatedField(
        queryset=User.objects.all(), required=False, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date',)
        model = Comment
