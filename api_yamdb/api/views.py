from rest_framework import viewsets, status
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import (IsAuthenticated, 
                                        IsAuthenticatedOrReadOnly)

from django_filters.rest_framework import DjangoFilterBackend
from mdb.models import Category, Comment, Genre, Review, Title, User
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, 
                          UserSerializer, SendCodeSerializer,
                          CheckCodeSerializer, TitleGetSerializer, TitlePostSerializer)

import random
                         

from .permissions import IsStaffIsOwnerOrReadOnly, IsStaffOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ('name', 'year', 'genre', 'category',)
    search_fields = ('name', 'year', 'genre', 'category',)

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return TitleGetSerializer
        return TitlePostSerializer


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

@api_view(['POST'])
@permission_classes([AllowAny])
def send_code(request):
    serializer = SendCodeSerializer(data=request.data)
    email = request.data.get('email', False)
    username = request.data.get('username', False)
    if serializer.is_valid():
        confirmation_code = ''.join(map(str, random.sample(range(10), 6)))
        user = User.objects.filter(email=email).exists()
        if not user:
            User.objects.create(email=email,username=username)
        User.objects.filter(email=email).update(
            confirmation_code=make_password(
                confirmation_code, salt=None, hasher='default')
        )
        mail_subject = 'Код подтверждения на Yamdb.ru'
        message = f'Ваш код подтверждения: {confirmation_code}'
        send_mail(mail_subject, message, 'yamdb@yamdb.ru', [email])
        return Response(
            f'Код отправлен на адрес {email}', status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    serializer = CheckCodeSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.data.get('username')
        # email = serializer.data.get('email')
        confirmation_code = serializer.data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if check_password(confirmation_code, user.confirmation_code):
            token = AccessToken.for_user(user)
            return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
        return Response({'confirmation_code': 'Неверный код подтверждения'},
                        status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfo(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        return Response(
            'Вы не авторизованы', status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            'Вы не авторизованы', status=status.HTTP_401_UNAUTHORIZED)
