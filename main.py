from time import strftime
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime

# Get current date
date = datetime.date
today = date.today()
my_date_time = strftime('%B %d, %Y')

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/', methods=['GET', 'POST'])
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    posts = BlogPost.query.all()
    requested_post = None
    for blog_post in posts:
        if blog_post.id == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    my_post_form = CreatePostForm()
    title = request.form.get('title')
    subtitle = request.form.get('subtitle')
    author = request.form.get('author')
    img_url = request.form.get('img_url')
    body = request.form.get('body')
    if request.method == 'POST':
        new_blog_item = BlogPost(title=title,
                                 subtitle=subtitle,
                                 date=my_date_time,
                                 body=body,
                                 img_url=img_url,
                                 author=author)
        db.session.add(new_blog_item)
        db.session.commit()

        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', my_post_form=my_post_form)

@app.route('/edit_post/<int:post_id>', methods=['POST', 'GET'])
def edit_post(post_id):
    all_post = BlogPost.query.all()
    for post in all_post:
        if post.id == post_id:
            '''Takes the current value from the given post 
            and puts it into a newly created form'''
            old_title = post.title
            old_subtitle = post.subtitle
            old_author = post.author
            old_img_url = post.img_url
            old_body = post.body
            edit_post_form = CreatePostForm(title=old_title,
                                            subtitle=old_subtitle,
                                            author=old_author,
                                            img_url=old_img_url,
                                            body=old_body)
            if request.method == 'POST':
                '''If request was sent then takes value from the current 
                form and saves it right back to the post item (Have to call 
                .data at the end to make it a processable format.'''
                post.title = edit_post_form.title.data
                post.subtitle = edit_post_form.subtitle.data
                post.author = edit_post_form.author.data
                post.img_url = edit_post_form.img_url.data
                post.body = edit_post_form.body.data
                db.session.commit()

                return redirect(url_for('get_all_posts'))
            return render_template('make-post.html', edit_post_form=edit_post_form, post=post)

@app.route('/delete/<int:post_id>')
def delete(post_id):
    all_blog_item = BlogPost.query.all()
    for blog in all_blog_item:
        if blog.id == post_id:
            db.session.delete(blog)
            db.session.commit()
            return redirect(url_for('get_all_posts'))

if __name__ == "__main__":
    app.run( debug=True)