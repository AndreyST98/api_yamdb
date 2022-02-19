from reviews.models import Category, Comment, Genre, Review, Title, User
from rest_framework import serializers
from .fields import CreatableSlugRelatedField
from rest_framework.generics import get_object_or_404

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
    

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = Category

class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Жанров"""
    class Meta:
        model = Genre
        exclude = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Категорий"""
    class Meta:
        model = Category
        exclude = ('id',)


class ReviewSerializer(serializers.ModelSerializer):

    author = CreatableSlugRelatedField(
        queryset=User.objects.all(), required=False, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        model = Review
    
    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        request = self.context['request']
        if self.context['request'].method == 'POST':
            if Review.objects.filter(title=title, author=request.user).exists():
                raise serializers.ValidationError('Нельзя оставить больше одного ревью к одному произведению')
        return data

class CommentSerializer(serializers.ModelSerializer):

    author = CreatableSlugRelatedField(
        queryset=User.objects.all(), required=False, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date',)
        model = Comment


class TitleViewSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return obj.rating

    class Meta:
        fields = '__all__'
        model = Title


class TitlePostSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(slug_field='slug', many=True,
                                         queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())

    class Meta:
        fields = '__all__'
        model = Title

class SendCodeSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)


class CheckCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
