from django.core.management.base import BaseCommand
import csv, sqlite3


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        con = sqlite3.connect("db.sqlite3") 
        cur = con.cursor()
        with open('static\\data\\category.csv','r', encoding='utf-8') as fin: 
            dr = csv.DictReader(fin) 
            to_db = [(i['id'], i['name'], i['slug']) for i in dr]
        cur.executemany("INSERT INTO mdb_category (id, name, slug) VALUES (?, ?, ?);", to_db)
        self.stdout.write(self.style.SUCCESS('Successfully import categories'))
        with open('static\\data\\comments.csv','r', encoding='utf-8') as fin: 
            dr = csv.DictReader(fin) 
            to_db = [(i['id'], i['review_id'], i['text'], i['author'], i['pub_date']) for i in dr]
        cur.executemany("INSERT INTO mdb_comment (id, review_id, text, author_id, pub_date) VALUES (?, ?, ?, ?, ?);", to_db)
        self.stdout.write(self.style.SUCCESS('Successfully import comments'))
  
        with open('static\\data\\genre_title.csv','r', encoding='utf-8') as fin: 
            dr = csv.DictReader(fin) 
            to_db = [(i['id'], i['title_id'], i['genre_id']) for i in dr]
        cur.executemany("INSERT INTO mdb_title_genre (id, title_id, genre_id) VALUES (?, ?, ?);", to_db)
   
        self.stdout.write(self.style.SUCCESS('Successfully import genre_title'))

        with open('static\\data\\genre.csv','r', encoding='utf-8') as fin: 
            dr = csv.DictReader(fin) 
            to_db = [(i['id'], i['name'], i['slug']) for i in dr]
        cur.executemany("INSERT INTO mdb_genre (id, name, slug) VALUES (?, ?, ?);", to_db)
        self.stdout.write(self.style.SUCCESS('Successfully import genres'))

        with open('static\\data\\review.csv','r', encoding='utf-8') as fin: 
            dr = csv.DictReader(fin) 
            to_db = [(i['id'], i['title_id'], i['text'], i['author'], i['score'], i['pub_date']) for i in dr]
        cur.executemany("INSERT INTO mdb_review (id, title_id, text, author_id, score, pub_date) VALUES (?, ?, ?, ?, ?, ?);", to_db)
        self.stdout.write(self.style.SUCCESS('Successfully import reviews'))
        with open('static\\data\\titles.csv','r', encoding='utf-8') as fin: 
            dr = csv.DictReader(fin) 
            to_db = [(i['id'], i['name'], i['year'], i['category']) for i in dr]
        cur.executemany("INSERT INTO mdb_title (id, name, year, category_id) VALUES (?, ?, ?, ?);", to_db)
        self.stdout.write(self.style.SUCCESS('Successfully import titles'))
       

        with open('static\\data\\users.csv','r', encoding='utf-8') as fin: 
            dr = csv.DictReader(fin) 
            to_db = [(i['id'], i['username'], i['email'], i['role'], i['bio'], i['first_name'], i['last_name'], i['password'], i['is_superuser'], i['is_staff'], i['is_active'], i['date_joined']) for i in dr]
        cur.executemany("INSERT INTO mdb_user (id, username, email, role, bio, first_name, last_name, password, is_superuser, is_staff, is_active, date_joined) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)
        con.commit()
        con.close()
        self.stdout.write(self.style.SUCCESS('Successfully import users'))
