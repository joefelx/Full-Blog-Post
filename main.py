from flask import Flask, request, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import LoginManager, login_user, logout_user, current_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_ckeditor import CKEditor
from forms import BlogForm, RegistrationForm, LoginForm, CommentForm


app = Flask(__name__)
app.config["SECRET_KEY"] = "HELLO"
ckeditor = CKEditor(app)
Bootstrap(app)

# Login and Registration
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Database Code
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///my-blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


### Creating Database Tables
# Creating users database
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    email = db.Column(db.String(250), unique=True)
    password = db.Column(db.String(250))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

db.create_all()


# Creating blogs database
class BlogPost(db.Model):
    __tablename__ = "blog_post"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250))
    date = db.Column(db.String(250))
    comments = relationship("Comment", back_populates="parent_post")


db.create_all()


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("blog_post.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    parent_post = relationship("BlogPost", back_populates="comments")
    text = db.Column(db.String(250))


db.create_all()


@app.route("/")
def home():
    all_posts = BlogPost.query.all()
    return render_template("index.html", posts=all_posts, current_user=current_user)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed in")
            return redirect(url_for("login"))

        hashed_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha1',
            salt_length=8
        )

        user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("home"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add_new_posts():
    form = BlogForm()

    if not current_user.is_authenticated:
        flash("Please Signup to write blog.")
        return redirect(url_for("register"))

    if form.validate_on_submit():
        post = BlogPost(
            author=current_user,
            title=form.title.data,
            subtitle=form.subtitle.data,
            img_url=form.img_url.data,
            body=form.body.data,
            date=datetime.now().strftime("%d %B, %Y")
        )

        db.session.add(post)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("add_post.html", form=form, is_edit=False)


@app.route("/post/<post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    post = BlogPost.query.get(post_id)

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            return redirect(url_for("login"))
        else:
            comment = Comment(
                text=form.comment.data,
                comment_author=current_user,
                parent_post=post
            )

            db.session.add(comment)
            db.session.commit()

    return render_template("post.html", post=post, current_user=current_user, form=form)


@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = BlogForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=current_user,
        body=post.body
    )

    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("home", id=post.id))

    return render_template("add_post.html", form=edit_form, is_edit=True, current_user=current_user)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    id = request.args.get("id")
    post = BlogPost.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/profile/<user_id>")
def profile(user_id):
    user = User.query.get(user_id)
    return render_template("profile.html", user=user)


@app.route("/user")
def user_profile():
    user_id = request.args.get("user_id")
    if current_user.is_authenticated:
        user = User.query.get(user_id)
        return render_template("profile.html", user=user)
    return redirect(url_for("login"))


@app.route("/delete_cmd", methods=["GET", "POST"])
def delete_cmd():
    cmd_id = request.args.get("cmd_id")
    post_id = request.args.get("post_id")
    comment = Comment.query.get(cmd_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for("show_post", post_id=post_id))


if __name__ == "__main__":
    app.run(debug=True)
