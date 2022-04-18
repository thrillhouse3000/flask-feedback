from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secretsecret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

debug = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    """Show home page"""
    comments = Feedback.query.all()
    return render_template('home.html', comments=comments)

@app.route('/register', methods=['GET', 'POST'])
def handle_registration():
    """Render and handle user registration form"""
    if 'user_id' in session:
        flash('You are already logged in.', 'danger')
        return redirect('/')
    else:
        form = UserForm()
        if form.validate_on_submit():
            data = {k:v for k, v in form.data.items() if k != 'csrf_token'}
            new_user = User.register(**data)
            db.session.add(new_user)
            try:
                db.session.commit()
            except IntegrityError:
                form.username.errors.append('Username is already in use. Please choose a different one.')
                return render_template('register.html', form=form)
            session['user_id'] = new_user.username
            if new_user.isAdmin == True:
                session['isAdmin'] = True
            else:
                session['isAdmin'] = False  
            flash ('Account created!', 'success')
            return redirect(f'/users/{new_user.username}')
        return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def handle_login():
    """Render and handle user login form"""
    if 'user_id' in session:
        flash('You are already logged in.', 'danger')
        return redirect('/')
    else:
        form = LoginForm()
        if form.validate_on_submit():
            data = {k:v for k, v in form.data.items() if k != 'csrf_token'}
            user = User.authenticate(**data)

            if user:
                flash(f'Welcome back {user.username}!', 'primary')
                session['user_id'] = user.username
                if user.isAdmin == True:
                    session['isAdmin'] = True
                else:
                    session['isAdmin'] = False
                return redirect(f'/users/{user.username}')
            else:
                form.username.errors = ['Invalid Username/Password.']
        return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
def handle_logout():
    """remove user_id from session"""
    session.pop('user_id')
    flash('Successfully logged out!', 'success')
    return redirect('/')


@app.route('/users/<username>')
def show_user_details(username):
    """render user details page"""
    user = User.query.get_or_404(username)

    if user.username != session['user_id'] and session['isAdmin'] != True:
        flash('Not authorized to do that.', 'danger')
        return redirect('/')
    else:
        return render_template('user_details.html', user=user)

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def handle_add_feedback_form(username):
    """render and handle feedback addition"""
    user = User.query.get_or_404(username)

    if session['user_id'] != user.username:
        flash('Not authorized to do that.', 'danger')
        return redirect('/')
    else:
        form = FeedbackForm()
        if form.validate_on_submit():
            data = {k:v for k, v in form.data.items() if k != 'csrf_token'}
            new_feedback = Feedback(**data, username=username)
            db.session.add(new_feedback)
            db.session.commit()
            flash('Comment added!', 'success')
            return redirect(f'/users/{username}')
    return render_template('/add_feedback.html', form=form, username=username)


@app.route('/feedback/<int:feedback_id>/update', methods=['GET','POST'])
def handle_update_feedback_form(feedback_id):
    """render and handle feedback update form"""
    comment = Feedback.query.get_or_404(feedback_id)

    if session['user_id'] != comment.username and session['isAdmin'] == False:
        flash('Not authorized to do that.', 'danger')
        return redirect('/')
    else:
        
        form = FeedbackForm(obj=comment)

        if form.validate_on_submit():
            comment.title = form.title.data
            comment.content = form.content.data
            db.session.commit()
            flash('Comment updated!', 'success')
            return redirect(f'/users/{comment.username}')
    return render_template('/update_feedback.html', form=form, comment=comment)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Delete user from DB and all associated comments"""
    user = User.query.get_or_404(username)

    if session['user_id'] != user.username and session['isAdmin'] == False:
        flash('Not authorized to do that', 'danger')
        return redirect('/')
    else:
        db.session.delete(user)
        db.session.commit()
        session.pop('user_id')
        flash('Account deleted!', 'success')
        return redirect('/')

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_comment(feedback_id):
    """delete a comment"""
    comment = Feedback.query.get_or_404(feedback_id)

    if session['user_id'] != comment.username and session['isAdmin'] == False:
        flash('Not authorized to do that.', 'danger')
        return redirect('/')
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted!', 'success')
        return redirect(f'/users/{comment.username}')
