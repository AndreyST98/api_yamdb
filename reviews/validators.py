from django.core.exceptions import ValidationError
from django.utils import timezone


def validator(composition_year):
    if composition_year > int(timezone.now().year):
        raise ValidationError('Извините, ваш год из будущего')
