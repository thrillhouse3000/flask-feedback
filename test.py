from unittest import TestCase
from flask import session, jsonify
from app import app
from models import db, User, Feedback

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_test'
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

test_user = {
    'username': 'Test',
    'password': 'test',
    'email': 'test@test.test',
    'first_name': 'Test',
    'last_name': 'Testerson'
}

test_user2 = {
    'username': 'Test2',
    'password': 'test2',
    'email': 'test2@test.test',
    'first_name': 'Test2',
    'last_name': 'Testerson',
    'isAdmin': False
}

test_comment = {
    'title': 'Test Title',
    'content': 'Test Content',
    'username': 'Test'
}

class UserViewsTestCase(TestCase):
    
    def setUp(self):
        User.query.delete()

        user = User.register(**test_user)
        db.session.add(user)
        db.session.commit()
        self.user = user
    
    def tearDown(self):

        db.session.rollback()

    def test_user_details(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = self.user.username
            res = client.get(f'/users/{self.user.username}')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h3>Test\'s Profile</h3>', html)
    
    def test_register_get(self):
        with app.test_client() as client:
            res = client.get(f'/register')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<form action="/register" method="POST" id="register-form">', html)

    def test_login_get(self):
        with app.test_client() as client:
            res = client.get(f'/login')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<form action="/login" method="POST" id="login-form">', html)
    



class UserRoutesTestCase(TestCase):
    
    def setUp(self):
        User.query.delete()

        user = User.register(**test_user)
        db.session.add(user)
        db.session.commit()
        self.user = user
    
    def tearDown(self):

        db.session.rollback()
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = ''
    
    def test_register_post(self):
        with app.test_client() as client:
            res = client.post('/register', json=test_user2)
            
            self.assertEqual(res.status_code, 200)
            self.assertEqual(User.query.count(), 2)
    
    def test_login_post(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = self.user.username
            res = client.post('/login', json={'username': 'Test', 'password': 'test'}, follow_redirects=True)
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn('Logged in as Test', html)

    def test_user_delete(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = self.user.username
            res = client.post(f'/users/{self.user.username}/delete', follow_redirects=True)
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn('Account deleted!', html)
            self.assertEqual(User.query.count(), 0)