import os
from os import path
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId
from forms import LoginForm, RegisterForm, CreateWorkoutForm
if path.exists("env.py"):
    import env

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get('MONGO_URI')
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
# Secret Key value generated via secrets python module.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
users = mongo.db.users
get_workouts = mongo.db.workouts


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/fundamentals')
def show_fundamentals():
    return render_template('fundamentals.html', fundamentals=mongo.db.fundamental_movements.find())


@app.route('/public-workouts')
def show_public_workouts():
    return render_template('public-workouts.html', workouts=mongo.db.workouts.find())


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        found_username = users.find_one({'username': request.form['username']})

        if found_username:
            if bcrypt.check_password_hash(found_username['password'], request.form.get('password').encode('utf-8')):
                session['username'] = request.form.get('username')
                session['logged-in'] = True
                return redirect(url_for('my_workouts'))
            else:
                flash(f'Username or Password incorrect. Please try again.', 'danger')
                return redirect(url_for('login'))

    return render_template('login.html', title='Login', form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        found_username = users.find_one({'username': request.form['username']})

        if not found_username:

            hashed_pw = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            users.insert_one({'username': register_form.username.data,
                              'password': hashed_pw})
            session['username'] = request.form.get('username')
            return redirect(url_for('index'))
        else:
            flash(f'Duplicate value detected for username. Please try another username.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html', title='Register', form=register_form)


@app.route('/logout')
def logout():
    session.clear()
    flash(f'Thank you for using Oly-Track. See you soon.', 'primary')
    return redirect(url_for('index'))


@app.route('/create-workout')
def create_workout():
    return render_template('create-workout.html')


@app.route('/my-workouts')
def my_workouts():
    return render_template('my-workouts.html')


@app.route('/workout-view/<workout_id>', methods=['GET', 'POST'])
def workout_view(workout_id):

    my_workout = get_workouts.find_one({'_id': ObjectId(workout_id)})
    return render_template('workout-view.html', workout=my_workout)


@app.route('/edit-workout')
def edit_workout():
    return render_template('edit-workout.html')


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=os.environ.get('PORT'),
            debug=True)