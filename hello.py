from flask import Flask, render_template,request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import tweepy
import smtplib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///friends.db'

db = SQLAlchemy(app)


class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.id

subscribers = []

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    names = ["John", "Mary", "Wes", "Sally"]
    return render_template("about.html", names=names)

@app.route('/subscribe')
def subscribe():
    title = "Subscribe To My Email Newsletter"
    return render_template("subscribe.html", title=title)

@app.route('/form', methods=["POST"])
def form():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")

    message = "You have been subscribed to my email newsletter"
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("eriche9187@gmail.com", "heze20062339")
    server.sendmail("eriche9187@gmail.com", email, message)

    if not first_name or not last_name or not email:
        error_statement = "All Form Fields Required..."
        return render_template("subscribe.html", error_statement=error_statement,
        first_name=first_name, last_name=last_name, email=email)
    
    subscribers.append(f"{first_name} {last_name} | {email} ")
    title = "Thank you!"
    return render_template("form.html", title=title, subscribers=subscribers)

@app.route('/friends', methods=['POST', 'GET'])
def friends():
    title="My Friends list"

    if request.method == "POST":
        friend_name = request.form['name']
        new_friend = Friends(name=friend_name)

        try:
            db.session.add(new_friend)
            db.session.commit()
            return redirect('/friends')
        except:
            return "There was an error adding your friend..."
    else:
        friends = Friends.query.order_by(Friends.date_created)
        return render_template("friends.html", title=title, friends=friends)

@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    friend_to_update = Friends.query.get_or_404(id)
    if request.method == "POST":
        friend_to_update.name = request.form['name']
        try:
            db.session.commit()
            return redirect('/friends')
        except:
            return "There was an error updating your friend..."
    else:
        return render_template('update.html', friend_to_update=friend_to_update)

@app.route('/delete/<int:id>')
def delete(id):
    friend_to_delete = Friends.query.get_or_404(id)
    try:
        db.session.delete(friend_to_delete)
        db.session.commit()
        return redirect('/friends')
    except:
        return "There was an error deleting your friend..." 

@app.route('/twitter')
def twitter():
    auth = tweepy.OAuthHandler("iaF8eNiybCCdkJyB9AWBGWY6C", "KCKEN63inM5mhn7VxLP83WyEhMVjnamwT0J8wx0x8J37KCTQBB")
    auth.set_access_token("1382048922814844930-NDR9AEchHVRZKTh1guGzD3ZYkihuVh", "HipKaPVqwi5yHdvXGmZtR2eUDb3k7SlPH7BycBNOCSeJZ")
    api = tweepy.API(auth)

    try: 
        api.verify_credentials()
        print("Authentication OK")
    except:
        print("Error during authentication")

    user=api.get_user("POTUS")

    print("User details:")
    print(user.name)
    print(user.description)
    print(user.location)

    timeline = api.user_timeline("POTUS", tweet_mode="extended")

    for tweet in timeline:
        print(f"{tweet.user.name} said  {tweet.full_text}")

    return render_template("tweets.html", user=user, timeline=timeline)
       
