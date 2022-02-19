from rest_framework import viewsets, status
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import (IsAuthenticated, AllowAny,
                                        IsAuthenticatedOrReadOnly)

from django_filters.rest_framework import DjangoFilterBackend
from mdb.models import Category, Comment, Genre, Review, Title, User
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import PageNumberPagination

from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitlePostSerializer, TitleViewSerializer,
                          UserSerializer, 
                          GenreSerializer, ReviewSerializer,
                          UserSerializer)
from .permissions import IsStaffIsOwnerOrReadOnly, IsStaffOrReadOnly
import random


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitlePostSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ('name', 'year')
    search_fields = ('name', 'year', 'genre', 'category',)

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return TitleViewSerializer
        return TitlePostSerializer


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ('name', 'slug')


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ('name', 'slug')


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsStaffIsOwnerOrReadOnly, IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return Review.objects.filter(title_id=title.id)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(
            title_id=title.id, author_id=self.request.user.id
        )
        title.rating


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsStaffIsOwnerOrReadOnly, IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        return Comment.objects.filter(review_id=review.id)

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        serializer.save(
            review_id=review.id, author_id=self.request.user.id
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'username'

    @action(
        methods=['get', 'patch', ],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        user = User.objects.get(username=request.user.username)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    data=serializer.data, status=status.HTTP_200_OK)
            return Response(data=serializer.errors, status=status.HTTP_200_OK)


@api_view(['POST', ])
def signup(request):
    username = request.POST['username']
    email = request.POST['email']
    if not User.objects.filter(username=username).exists():
        user = User.objects.create(username=username, email=email)
    else:
        user = User.objects.filter(username=username).first()
    code = default_token_generator.make_token(user)
    send_mail(
        subject='Код подтверждения на Yamdb.ru',
        message=f'"confirmation_code": "{code}"',
        from_email='yamdb@yamdb.ru',
        recipient_list=[email, ],
        fail_silently=True
    )
    return Response(data={'email': email}, status=status.HTTP_200_OK)


@api_view(['POST', ])
def login(request):
    username = request.POST['username']
    confirmation_code = request.POST['confirmation_code']
    user = User.objects.filter(username=username).first()
    data = {'field_name': []}
    if user is None:
        data['field_name'].append('username')
        data['field_name'].append('email')
    if not default_token_generator.check_token(user, confirmation_code):
        data['field_name'].append('confirmation_code')
    if len(data['field_name']) != 0:
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
    token = RefreshToken.for_user(user)
    return Response(
        data={'token': str(token.access_token)}, status=status.HTTP_200_OK)
