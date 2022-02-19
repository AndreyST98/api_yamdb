from rest_framework import viewsets, status
from rest_framework_simplejwt.tokens import AccessToken
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from django_filters.rest_framework import DjangoFilterBackend
from mdb.models import Category, Comment, Genre, Review, Title, User
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, TitleSerializer,
                          UserSerializer, SendCodeSerializer,
                          CheckConfirmationCodeSerializer)

from .permissions import IsStaffIsOwnerOrReadOnly, IsStaffOrReadOnly

import random


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsStaffOrReadOnly)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ('name', 'year')
    search_fields = ('name', 'year', 'genre', 'category',)


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsStaffOrReadOnly)
    filter_backends = [filters.SearchFilter]
    search_fields = ('name', 'slug')


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsStaffOrReadOnly)
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
    serializer = SendCodeSerializer(data=request.data)
    username = request.data.get('username', False)
    email = request.data.get('email', False)
    if serializer.is_valid():
        confirmation_code = ''.join(map(str, random.sample(range(10), 6)))
        user = User.objects.filter(username=username).exists()
        if not user:
            User.objects.create_user(username=username, email=email)
        User.objects.filter(username=username).update(
            confirmation_code=confirmation_code)
        mail_subject = 'Код подтверждения на yamdb.ru'
        message = f'Ваш код подтверждения: {confirmation_code}'
        send_mail(mail_subject, message, 'yamdb@yamdb.ru', [email])
        return Response(
            f'Код отправлен на адрес {email}', status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
def login(request):
    serializer = CheckConfirmationCodeSerializer(data=request.data)
    if serializer.is_valid():
        username = request.data.get('username')
        confirmation_code = serializer.data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if confirmation_code == user.confirmation_code:
            token = AccessToken.for_user(user)
            return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
        return Response({'confirmation_code': 'Неверный код подтверждения'},
                        status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
