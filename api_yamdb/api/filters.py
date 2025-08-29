from django_filters import CharFilter, FilterSet

from reviews.models import Title


class TitleFilters(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    category = CharFilter(field_name='category__slug',)
    genre = CharFilter(field_name='genre__slug',)

    class Meta:
        model = Title
        fields = ('name', 'year', 'category', 'genre')
