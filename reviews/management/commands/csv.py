import csv

from django.core.management.base import BaseCommand

from reviews.models import Title, Review, Genre, Category, Comment, User


class Command(BaseCommand):
    def handle(self, *args, **options):
        Category.objects.all().delete()
        User.objects.all().delete()
        Title.objects.all().delete()
        Genre.objects.all().delete()
        Comment.objects.all().delete()
        with open(
            'static\\data\\category.csv', 'r', encoding='utf-8'
        ) as cg_csv:
            reader = csv.DictReader(cg_csv)
            for row in reader:
                category = Category(**row)
                category.save()
        self.stdout.write(self.style.SUCCESS('Successfully import categories'))
        with open(
            'static\\data\\users.csv', 'r', encoding='utf-8'
        ) as users_csv:
            reader = csv.DictReader(users_csv)
            for row in reader:
                user = User(**row)
                user.save()
        self.stdout.write(self.style.SUCCESS('Successfully import users'))
        with open(
            'static\\data\\genre.csv', 'r', encoding='utf-8'
        ) as genre_csv:
            reader = csv.DictReader(genre_csv)
            for row in reader:
                genre = Genre(**row)
                genre.save()
        self.style.SUCCESS('Successfully import genres')
        with open(
            'static\\data\\titles.csv', 'r', encoding='utf-8'
        ) as titles_csv:
            reader = csv.DictReader(titles_csv)
            for row in reader:
                row['category'] = Category.objects.get(id=row['category'])
                title = Title(**row)
                title.genre
                title.save()
        self.stdout.write(self.style.SUCCESS('Successfully import titles'))
        with open(
            'static\\data\\review.csv', 'r', encoding='utf-8'
        ) as review_csv:
            reader = csv.DictReader(review_csv)
            for row in reader:
                row['author'] = User.objects.get(id=row['author'])
                review = Review(**row)
                review.save()
        self.stdout.write(self.style.SUCCESS('Successfully import reviews'))
        with open(
            'static\\data\\comments.csv', 'r', encoding='utf-8'
        ) as com_csv:
            reader = csv.DictReader(com_csv)
            for row in reader:
                row['author'] = User.objects.get(id=row['author'])
                comment = Comment(**row)
                comment.save()
        self.stdout.write(self.style.SUCCESS('Successfully import comments'))
        with open(
            'static\\data\\genre_title.csv', 'r', encoding='utf-8'
        ) as genre_title_csv:
            reader = csv.DictReader(genre_title_csv)
            for row in reader:
                title = Title.objects.get(id=row['title_id'])
                title.genre.add(Genre.objects.get(id=row['genre_id']))
                title.save()
        self.stdout.write(self.style.SUCCESS(
            'Successfully import genre_title')
        )
