from models import User, Feedback, db
from flask import session
from app import app

db.drop_all()
db.create_all()

test1 = User.register(username='TestGuy', password='test', email='test@test.test', first_name='Testy', last_name='Testerson')

test2 = User.register(username='TestGal', password='test', email='test_gal@test.test', first_name='Testina', last_name='Testerson', isAdmin=True)

comment1 = Feedback(title='Testing', content='testing', username='TestGuy')

comment2 = Feedback(title='Test Test', content='testing', username='TestGal')

db.session.add_all([test1, test2, comment1, comment2])
db.session.commit()
session = ''