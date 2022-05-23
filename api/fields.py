from rest_framework import serializers


class CreatableSlugRelatedField(serializers.SlugRelatedField):

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(id=data)
        except (TypeError, ValueError):
            self.fail('invalid')
