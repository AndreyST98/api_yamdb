from rest_framework import serializers

from mdb.models import Category, Comment, Genre, Review, Title, User
from .fields import CreatableSlugRelatedField


class CreatableSlugRelatedField(serializers.SlugRelatedField):
    
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(id=data)
        except (TypeError, ValueError):
            self.fail('invalid')

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = User


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return obj.rating

    class Meta:
        fields = '__all__'
        model = Title


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Genre


class CategorySerializer(serializers.ModelSerializer):

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
    review = serializers.PrimaryKeyRelatedField(
        queryset=Review.objects.all(), required=False
    )

    class Meta:
        fields = '__all__'
        model = Comment
