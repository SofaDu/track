import datetime
import os
from flask import render_template, request, redirect, session, app, Flask, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'osijefoi\n\xec]/'

db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tel_number = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Integer, nullable=False)


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tel_number = db.Column(db.String(50), nullable=False)
    order_number = db.Column(db.String(50), nullable=False)
    date_of_creation = db.Column(db.String(10), nullable=False)

    updates = db.relationship('Update', backref='track', lazy=True)


class Update(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num_track = db.Column(db.String(50), db.ForeignKey('track.order_number'))
    status_track = db.Column(db.String(50), nullable=False)
    date_update_track = db.Column(db.String(10), nullable=False)





@app.route('/', methods=['POST', 'GET'])
def sign_in():
    print(session['tel_number'])
    print(session['isSignIn'])
    if session['tel_number']:
        return redirect('/track')

    users = Users.query.all()

    if request.method == "POST":
        tel_number: str = request.form.get('tel_number')
        password: str = request.form.get('password')
        print(tel_number + password)

        for user in users:
            if tel_number == user.tel_number and password == user.password:
                session.pop('tel_number')
                session['tel_number'] = tel_number
                session.pop('isSignIn')
                session['isSignIn'] = True
                session['role'] = user.role
                print(session['role'])
                # Track(tel_number=tel_number)
                print("Вошли")
                return redirect('/track')

    return render_template("sign_in.html",  isSignIn=session['isSignIn'], tel_number=session['tel_number'])


@app.route('/track', methods=['POST', 'GET'])
def index():
    print(session['tel_number'])
    print(session['isSignIn'])

    if 'isSignIn' not in session:
        session['isSignIn'] = False
        session['tel_number'] = None
        session['role'] = 0
        return render_template('sign_in.html')
    else:
    # orders = Track.query \ .join(Update, Track.order_number == Update.num_track) \ .add_columns(Track.id,
    # Track.order_number, Track.date_of_creation, Update.status_track, Update.date_update_track) \ .order_by(desc(
    # Track.id)).all() orders = Track.query.order_by(desc(Track.id)).all()
        tracks = Track.query.order_by(desc(Track.id)).all()
        updates = Update.query.all()
        users = Users.query.all()
        print(tracks)
        return render_template('index.html', tracks=tracks, updates=updates, users=users,
                               tel_number=session['tel_number'], role=session['role'])


@app.route('/add_order', methods=['POST', 'GET'])
def add_order():

    if request.method == 'POST':
        tel_number = session['tel_number']
        order_number = request.form.get('order_number')
        new_order = Track(tel_number=tel_number, order_number=order_number, date_of_creation=datetime.date.today())
        new_update = Update(num_track=order_number, status_track='Формирование',
                            date_update_track=datetime.date.today())
        if order_number != "":
            try:
                db.session.add(new_order)
                db.session.add(new_update)
                db.session.commit()
            except Exception as e:
                print(e)
        #print(new_order)
        #print(new_update)
        flash('Заказ успешно добавлен' + str(datetime.date.today()), 'success')
    return redirect("/track")


@app.route('/update_status/<string:id>', methods=['POST'])
def update_status(id):
    if request.method == 'POST':
        track = Track.query \
            .join(Track, Track.order_number == Update.num_track) \
            .add_columns(Track.order_number, Track.date_of_creation, Update.status_track, Update.date_update_track) \
            .filter_by(order_number=id).first_or_404()
        old_status = track.status_track
        new_status: str = request.form.get('status', '')
        new_update = Update(num_track=id, status_track=new_status,
                            date_update_track=datetime.date.today())
        if new_status != old_status:
            try:
        # Создаем новую запись в таблице Update
                db.session.add(new_update)
                db.session.commit()
                print(new_update)
            except Exception as e:
                print(e)
        flash(f'Статус заказа {track.order_number} обновлен. Старый статус: {old_status}, Новый статус: {new_status}', 'success')
    return redirect(url_for('index'))



@app.route('/exit')
def exit():
    session.pop('tel_number')
    session['tel_number'] = None
    session.pop('isSignIn')
    session['isSignIn'] = False
    session.pop('role')
    session['role'] = 0

    return redirect("/")


if __name__ == '__main__':
    # db.create_all()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
