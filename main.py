from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as dt
import csv
import requests
import os
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('url')

app = Flask(__name__, template_folder="templates", static_folder="static")

usernames = ['Sudham', 'fiitjee', 'Akhilesh']

pws = ['2020', 'friends', '2006']

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'

db = SQLAlchemy(app)


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50), nullable=False)
	content = db.Column(db.Text, nullable=False)
	author = db.Column(db.String(20))
	date_time = db.Column(db.DateTime, nullable=True, default=dt.now)
	post_edited = db.Column(db.String, default='Posted')

	def __repr__(self):
		return 'Blog post ' + str(self.id)


class User(db.Model):
	user = db.Column(db.String(10), primary_key=True, nullable=False)
	pw = db.Column(db.String(15), nullable=False)

	def __repr__(self):
		return str(self.username)


@app.route("/")
def home():
	return render_template("home.html")


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
	if request.method == 'POST':
		name = request.form['name']
		feedback = request.form['feedback']
		rating = request.form['rating']
		row = [str(name), str(feedback), str(rating)]
		with open('feedback.csv', 'a', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(row)
			file.close()
		data = {'value1': name, 'value2': rating, 'value3': feedback}
		requests.post(url, data)
		return render_template(
		    'feedback.html', thank='Thank you for your valuable feedback')
	else:
		return render_template('feedback.html', thank=None)


@app.route('/admin', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		if request.form['username'] in usernames and request.form[
		    'password'] in pws:
			all_posts = Post.query.order_by(Post.date_time.desc())
			return render_template('admin_blog.html', posts=all_posts)
		else:
			return render_template('login.html', auth=False)
	else:
		return render_template('login.html', auth=True)


# BLOG #
@app.route('/blog', methods=['GET', 'POST'])
def blog():
	all_posts = Post.query.order_by(Post.date_time.desc())
	return render_template("blog.html", posts=all_posts)


@app.route('/blog/delete/<id>')
def delete(id):
	post = Post.query.get_or_404(id)
	db.session.delete(post)
	db.session.commit()
	all_posts = Post.query.order_by(Post.date_time.desc())
	return render_template("admin_blog.html", posts=all_posts)


@app.route('/blog/edit/<id>', methods=['GET', 'POST'])
def edit(id):
	post = Post.query.get_or_404(id)
	if request.method == 'POST':
		post.title = request.form['title']
		post.content = request.form['content']
		post.author = request.form['author']
		post.date_time = dt.now()
		post.post_edited = 'Edited'
		db.session.commit()
		all_posts = Post.query.order_by(Post.date_time.desc())
		return render_template("admin_blog.html", posts=all_posts)
	else:
		return render_template("edit.html", post=post)


@app.route('/blog/new_post', methods=['GET', 'POST'])
def new_post():
	if request.method == 'POST':
		post_title = request.form['title']
		post_content = request.form['content']
		post_author = request.form['author']
		new_post = Post(
		    title=post_title, content=post_content, author=post_author)
		db.session.add(new_post)
		db.session.commit()
		all_posts = Post.query.order_by(Post.date_time.desc())
		return render_template("admin_blog.html", posts=all_posts)
	else:
		return render_template('new_post.html')


# BLOG CODE ENDS #
if __name__ == "__main__":
	app.run('0.0.0.0', 8080)
