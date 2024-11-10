from flask import Flask,render_template, url_for, session, redirect, g, request
from database import get_db,close_db
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm,SignupForm,FilterForm, Change_pswForm, CardForm
from functools import wraps
from datetime import date
# the date.today value is a different by a few hours from the sql date(CURRENT_DATE) because of different time zones

app = Flask(__name__)
app.config["SECRET_KEY"] = "my_key"
app.teardown_appcontext(close_db)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/all_slots",methods=["GET","POST"])
def all_slots():
    form = FilterForm()
    db = get_db()
    slots= None
    if form.validate_on_submit():
        floor = form.floor.data
        time1 = form.time1.data
        time2 = form.time2.data
        trainer = form.trainer.data
        if time1 == "" and time2 == "" :
            if floor == "both" and trainer == "All":
                slots= db.execute("""Select * from slots;""").fetchall()
            elif floor != "both" and trainer == "All":
                slots= db.execute("""Select * from slots where gym is ?;""", (floor,)).fetchall()
            elif floor == "both" and trainer != "All":
                slots= db.execute("""Select * from slots where trainer is ?;""", (trainer,)).fetchall()
            else:
                slots= db.execute("""Select * from slots where trainer is ? and gym is ?;""", (trainer,floor)).fetchall()
        elif time1 != "" and time2 == "":
            if floor == "both" and trainer == "All":
                slots= db.execute("""Select * from slots where time >= ? ;""", (time1,)).fetchall()
            elif floor != "both" and trainer == "All":
                slots= db.execute("""Select * from slots where gym is ? and time >= ?;""", (floor,time1)).fetchall()
            elif floor == "both" and trainer != "All":
                slots= db.execute("""Select * from slots where trainer is ? and time >= ?;""", (trainer,time1)).fetchall()
            else:
                slots= db.execute("""Select * from slots where trainer is ? and gym is ? and time >= ?;""", (trainer,floor,time1)).fetchall()
        else:
            if time1>time2:
                time2=24
            if time1=="" and time2 !="":
                time1=0
            if floor == "both" and trainer == "All":
                slots= db.execute("""Select * from slots where time >= ? and time <=? ;""", (time1,time2)).fetchall()
            elif floor != "both" and trainer == "All":
                slots= db.execute("""Select * from slots where gym is ? and time >= ? and time <= ?;""", (floor,time1,time2)).fetchall()
            elif floor == "both" and trainer != "All":
                slots= db.execute("""Select * from slots where trainer is ? and time >= ? and time <=?;""", (trainer,time1,time2)).fetchall()
            else:
                slots= db.execute("""Select * from slots where trainer is ? and gym is ? and time >= ? and time <= ?;""", (trainer,floor,time1,time2)).fetchall()
    return render_template("slots.html",form=form, slots=slots , captions="The available slots for today: ")

@app.route("/")
def index():
    return render_template("index.html")

@app.before_request
def load_logged_in_user():
    g.user = session.get("user_id", None)

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return view(*args, **kwargs)
    return wrapped_view


@app.route("/signup",methods=["GET","POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user_id=form.user_id.data
        password=form.password.data
        amount=0
        db= get_db()
        conflict_user = db.execute("""Select * from users
                            Where user_id = ?;""",(user_id,)).fetchone()
        if conflict_user is not None:
            form.user_id.errors.append("Username is already taken. Please try a different one.")
        else:
            db.execute("""INSERT INTO users(user_id, password) 
                       Values (?,?);""",(user_id, generate_password_hash(password)))
            db.commit()
            return redirect( url_for("login"))
    return render_template("signup.html",form=form)
    
@app.route("/login",methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id=form.user_id.data
        password=form.password.data
        db=get_db()
        user = db.execute("""Select * from users where user_id = ?;""",(user_id,)).fetchone()
        if user is None:
            form.user_id.errors.append("This username doesn't exist")
        elif not check_password_hash(user["password"], password):
            form.password.errors.append("Incorrect password")
        else:
            session.clear()
            session["user_id"] = user_id
            return redirect(url_for("index"))
    return render_template("login.html", form=form)

@app.route("/slot/<int:slot_id>")
def slot(slot_id):
    db= get_db()
    slot=db.execute("""Select * from slots where slot_id = ?;""", (slot_id,)).fetchone()
    return render_template("slot.html", slot=slot)

@app.route("/book/<int:slot_id>")
@login_required
def book(slot_id):
    user_id=session['user_id']
    day=date.today()
    db=get_db()
    if "bookings" not in session:
        session["bookings"]={"slot_id":[]}
    if slot_id not in session["bookings"]["slot_id"]:
        if len(session["bookings"]["slot_id"]) < 3:
            session["bookings"]["slot_id"].append(slot_id)
            db=get_db()
            slot=db.execute("""Select * from slots where slot_id=?;""", (slot_id,)).fetchone()
            user_id=session["user_id"]
            time=slot["time"]
            floor=slot["gym"]
            trainer=slot["trainer"]
            _date=slot["date"]
            db.execute("""INSERT INTO bookings (user_id,slot_id,time,gym,trainer,date)
                       Values (?,?,?,?,?,?);""", (user_id,slot_id,time,floor,trainer,day))
            db.commit()
        
    else:
        return redirect( url_for("bookings"))
    session.modified= True
    return redirect( url_for("bookings"))


@app.route("/cancel/<int:slot_id>")
def cancel(slot_id):
    db= get_db()
    slot=db.execute("""Select * from slots where slot_id = ?;""", (slot_id,)).fetchone()
    return render_template("cancel.html", slot=slot)

@app.route("/cancelling/<int:slot_id>")
def cancelling(slot_id):
    user_id=session['user_id']
    db=get_db()
    cursor=db.cursor()
    cursor.execute("""Delete from bookings where slot_id=? and user_id=?;""", (slot_id,user_id))
    db.commit()
    return redirect( url_for("bookings"))


@app.route("/history")
@login_required
def history():
    user_id=session['user_id']
    db=get_db()
    slots=db.execute("""Select * from bookings where user_id= ?;""", (user_id,)).fetchall()
    return render_template("history.html",history=slots)

@app.route("/logout")
def logout():
    session.clear()
    return redirect( url_for("index") )

@app.route("/card",methods=["GET","POST"])
@login_required
def card():
    form= CardForm()
    amount=form.amount.data
    user_id=session['user_id']
    db=get_db()
    card=db.execute("""Select * from card where user_id=?;""",(user_id,)).fetchone()
    if card is None:
        amount1=0
        points=0
        db.execute("""Insert into card(user_id,amount)
               Values (?,?);""", (user_id,amount1))
        db.commit()
        card=db.execute("""Select * from card where user_id=?;""",(user_id,)).fetchone()
        card_id=card['card_id']
        db.execute("""Insert into card_points(card_id,user_id,points)
                       Values(?,?,?)""", (card_id,user_id,points))
        db.commit()
    return render_template("card.html",form=form,amount=amount)


@app.route("/card_details")
def card_details():
    user_id=session['user_id']
    db=get_db()
    card=db.execute("""Select * from card where user_id=?;""", (user_id,)).fetchone()
    cardid=card['card_id']
    amount=card['amount']
    card_id=db.execute("""Select * from card_points where user_id=?;""", (user_id,)).fetchone()
    points=card_id['points']
    return render_template("card_details.html",amount=amount,points=points, cardid=cardid)

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/password_change",methods=["GET","POST"])
def password_change():
    form = Change_pswForm()
    if form.validate_on_submit():
        user_id=form.user_id.data
        password=form.password.data
        db=get_db()
        cursor=db.cursor()
        user = db.execute("""Select * from users where user_id = ?;""",(user_id,)).fetchone()
        if user is None:
            form.user_id.errors.append("This username doesn't exist")
        else:
            cursor.execute("""Update users set password = ?
                       where user_id=?;""",(generate_password_hash(password),user_id))
            db.commit()
            return redirect(url_for("login"))
    return render_template("pswchange.html", form=form)

@app.route("/today_bookings")
@login_required
def bookings():
    user_id=session['user_id']
    day=date.today()# the date.today value is a different by a few hours from the sql date(CURRENT_DATE) because of different time zones
    print(day)
    db=get_db()
    slots=db.execute("""SELECT * from bookings where user_id=? and date=?;""",(user_id,day)).fetchall()
    return render_template("bookings.html",bookings=slots)

@app.route("/citations")
def citations():
    return render_template("citations.html")
