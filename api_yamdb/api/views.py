import uuid

from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Comment, Genre, Review, Title, User
from .filter import TitlesFilter
from .permissions import IsAdmin, IsAdminOrReadOnly, IsStaffIsOwnerOrReadOnly
from .serializers import (CategorySerializer, CheckCodeSerializer,
                          CommentSerializer, GenreSerializer, ReviewSerializer,
                          SendCodeSerializer, TitlePostSerializer,
                          TitleViewSerializer, UserSerializer,
                          UserSerializerRead)
from .mixins import CustomViewSet
from api_yamdb.settings import ADMIN_EMAIL


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitlePostSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return TitleViewSerializer
        return TitlePostSerializer


class GenreViewSet(CustomViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ('name', 'slug')
    lookup_field = 'slug'


class CategoryViewSet(CustomViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsStaffIsOwnerOrReadOnly, IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(
            title_id=title.id, author_id=self.request.user.id
        )


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
    permission_classes = [IsAuthenticated, IsAdmin]
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'username'

    @action(
        methods=['get', 'patch', ],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(
                data=serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserSerializerRead(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([AllowAny])
def signup(request):
    serializer = SendCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    if username == 'me':
        return Response(
            'Такую учётную запись нельзя создать',
            status=status.HTTP_400_BAD_REQUEST)
    user_byemail = User.objects.filter(email=email)
    user_byname = User.objects.filter(username=username)
    if user_byemail.exists() or user_byname.exists():
        return Response(
            status=status.HTTP_400_BAD_REQUEST)
    confirmation_code = str(uuid.uuid4())
    User.objects.create(
        username=username,
        email=email,
        confirmation_code=confirmation_code)
    send_mail(
        subject='Код подтверждения на Yamdb.ru',
        message=f'"confirmation_code": "{confirmation_code}"',
        from_email=ADMIN_EMAIL,
        recipient_list=[email, ],
        fail_silently=True
    )
    return Response(
        data={'email': email, 'username': username},
        status=status.HTTP_200_OK
    )


@api_view(['POST', ])
@permission_classes([AllowAny])
def login(request):
    serializer = CheckCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User.objects.filter(username=username))
    if user.confirmation_code != confirmation_code:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    token = AccessToken.for_user(user)
    return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
