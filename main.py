from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import smtplib
import os
from dotenv import load_dotenv
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
app.config['CKEDITOR_PKG_TYPE'] = 'basic'
bootstrap = Bootstrap(app)
##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

today = datetime.datetime.today()
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField('Blog Content', validators=[DataRequired()])  # <--
    submit = SubmitField("Submit Post", validators=[DataRequired()])

    def __repr__(self):
        return '<CreatePostForm %r>' % self.title


def send_email(name, email, number, message):
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=EMAIL, password=PASSWORD)
        connection.sendmail(
            from_addr=EMAIL,
            to_addrs=email,
            msg=f"Subject: SoriOner's Blog Website Contact\n\n"
                f"{name} want to hear from you\n"
                f"{name} Phone Number: {number}\n"
                f"message: {message}"
        )


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts, year=today.year)


@app.route("/post/<index>")
def show_post(index):
    posts = db.session.query(BlogPost).all()
    print(posts[int(index) - 1])
    return render_template("post.html", post=posts[int(index) - 1], year=today.year)


@app.route("/make_post", methods=['POST', 'GET'])
def make_post():
    form = CreatePostForm()
    body = form.body.data
    title = form.title.data
    subtitle = form.subtitle.data
    author = form.author.data
    img_url = form.img_url.data
    h1 = "Create a Post"
    if form.validate_on_submit():
        new_post = BlogPost(title=title, subtitle=subtitle, author=author, img_url=img_url, body=body, date=f"{today.strftime('%B')} {today.day}, {today.year}")
        db.session.add(new_post)
        db.session.commit()
        return redirect("/")
    return render_template("make-post.html", form=form, h1=h1, year=today.year)


# @app.route("create_post")

@app.route("/edit-post/<post_id>", methods=["POST", "GET"])
def edit_post(post_id):
    post = BlogPost.query.get(int(post_id))
    form = CreatePostForm(title=post.title,
    subtitle=post.subtitle,
    img_url=post.img_url,
    author=post.author,
    body=post.body)
    h1 = "Edit Post"
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.subtitle = form.subtitle.data
        post.author = form.author.data
        post.img_url = form.img_url.data
        db.session.commit()
        return redirect("/")
    return render_template("make-post.html", form=form, h1=h1, year=today.year)


@app.route("/delete_post/<post_id>", methods=["POST", "GET"])
def delete_post(post_id):
    post = BlogPost.query.get(int(post_id))
    db.session.delete(post)
    db.session.commit()
    return redirect("/")


@app.route("/about")
def about():
    return render_template("about.html", year=today.year)


@app.route("/contact", methods=["POST", "GET"])
def contact():
    h1 = "Contact Me"
    return render_template("contact.html", h1=h1, year=today.year)


@app.route('/message', methods=['POST'])
def message():
    h1 = "Email Sent"
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    message = request.form['message']
    try:
        send_email(name, email, phone, message)
    except Exception as e:
        print(e)

    return render_template("contact.html", date=today, h1=h1, year=today.year)


def footer():
    return render_template("footer.html", year=today.year)


if __name__ == '__main__':
    app.run(debug=True)