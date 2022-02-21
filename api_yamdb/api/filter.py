from django_filters import rest_framework as filter
from reviews.models import Title


class TitlesFilter(filter.FilterSet):
    genre = filter.CharFilter(
        field_name='genre__slug',
    )
    category = filter.CharFilter(
        field_name='category__slug',
    )
    year = filter.NumberFilter(
        field_name='year',
    )
    name = filter.CharFilter(
        lookup_expr="contains",
    )

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']
