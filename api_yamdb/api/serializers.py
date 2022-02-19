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
    

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = Category

class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return obj.rating

class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Жанров"""
    class Meta:
        fields = '__all__'
        model = Genre


class TitleGetSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    genre = GenreSerializer(required=True, many=True)
    category = CategorySerializer(required = True)

    def get_rating(self, obj):
        return obj.rating
    
    class Meta:
        fields = '__all__'
        model = Title
        depth = 1

class TitlePostSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True, required=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug', required=True
    )

    
    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):

    author = CreatableSlugRelatedField(
        queryset=User.objects.all(), required=False, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        model = Review
    
    def validate(self, data): 
        if data['following'].id == self.context['request'].user.id: 

            raise serializers.ValidationError( 

                'нельзя подписаться на самого себя') 

        return data 

class CommentSerializer(serializers.ModelSerializer):

    author = CreatableSlugRelatedField(
        queryset=User.objects.all(), required=False, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date',)
        model = Comment


class SendCodeSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)


class CheckCodeSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
