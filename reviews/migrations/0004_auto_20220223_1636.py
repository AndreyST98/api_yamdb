# Generated by Django 2.2.16 on 2022-02-23 09:36

from django.db import migrations, models
import reviews.models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_auto_20220223_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.IntegerField(default=None, validators=[reviews.models.validator], verbose_name='min_year'),
        ),
    ]
