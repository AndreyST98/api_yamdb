import random
import uuid

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from reviews.models import Category, Comment, Genre, Review, Title, User

from .filter import TitlesFilter
from .permissions import (IsAdminOrReadOnly, IsStaffIsOwnerOrReadOnly,
                          IsStaffOrReadOnly)
from .serializers import (CategorySerializer, CheckCodeSerializer,
                          CommentSerializer, GenreSerializer, ReviewSerializer,
                          SendCodeSerializer, TitlePostSerializer,
                          TitleViewSerializer, UserSerializer)


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitlePostSerializer
    queryset = Title.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter

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
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ('name', 'slug')
    lookup_field = 'slug'


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    # pagination_class = PageNumberPagination
    permission_classes = [IsStaffIsOwnerOrReadOnly, IsStaffOrReadOnly]

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
@permission_classes([AllowAny])
def signup(request):
    username = request.data.get('username')
    email = request.data.get('email')
    confirmation_code = str(uuid.uuid4())
    User.objects.create(username=username, email=email,
                        confirmation_code=confirmation_code)
    send_mail(
        subject='Код подтверждения на Yamdb.ru',
        message=f'"confirmation_code": "{confirmation_code}"',
        from_email='yamdb@yamdb.ru',
        recipient_list=[email, ],
        fail_silently=True
    )
    return Response(data={'email': email}, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')
    user = get_object_or_404(User.objects.filter(username=username,
                             confirmation_code=confirmation_code))
    token = RefreshToken.for_user(user)
    return Response(
        data={'token': str(token.access_token)}, status=status.HTTP_200_OK)
