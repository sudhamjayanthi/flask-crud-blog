from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from datetime import datetime as dt
from dotenv import load_dotenv
import requests
import csv
import os

app = Flask(__name__)
ckeditor = CKEditor(app)

load_dotenv()
WEBHOOK_URL = os.getenv('IFTTT_WEBHOOK_URL')
USERNAME = os.getenv('LOGIN_USERNAME')
PASS = os.getenv('LOGIN_PASS')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50), nullable=False)
	content = db.Column(db.Text, nullable=False)
	author = db.Column(db.String(20))
	date_time = db.Column(db.DateTime, nullable=True, default=dt.now)
	post_edited = db.Column(db.String, default='Posted')


@app.route("/")
def home():
	return render_template("home.html")

@app.route('/blog', methods=['GET', 'POST'])
def blog():
	all_posts = Post.query.order_by(Post.date_time.desc())
	return render_template("blog.html", posts=all_posts)


@app.route('/blog/delete/<id>')
def delete(id):

	if id < 4 :
		return redirect('/blog')

	post = Post.query.get_or_404(id)

	db.session.delete(post)
	db.session.commit()

	all_posts = Post.query.order_by(Post.date_time.desc())

	return render_template("admin_blog.html", posts=all_posts)


@app.route('/blog/edit/<id>', methods=['GET', 'POST'])
def edit(id):
	if id < 4 :
		return redirect('/blog')

	post = Post.query.get_or_404(id)

	if request.method == 'POST':
		post.title = request.form['title']
		post.content = request.form.get("ckeditor")
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
		title = request.form['title']
		content = request.form.get("ckeditor")
		author = request.form['author']

		new_post = Post(title=title, content=content, author=author)

		db.session.add(new_post)
		db.session.commit()

		all_posts = Post.query.order_by(Post.date_time.desc())
		return render_template("admin_blog.html", posts=all_posts)

	elif request.method == 'GET':
		return render_template('new_post.html')

@app.route('/admin', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		# Contact me at hey@sudham.tk for these login credentials if you want to see a demo
		if request.form['username'] == USERNAME and request.form['password'] == PASS:
			all_posts = Post.query.order_by(Post.date_time.desc())
			return render_template('admin_blog.html', posts=all_posts)
		else:
			return render_template('login.html', show_error=True)

	elif request.method == "GET":
		return render_template('login.html', show_error=False)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
	if request.method == 'POST':
		name = request.form['name']
		feedback = request.form['feedback']
		rating = request.form['rating']

		# Deta.sh doesn't allow to write things in a file, hence removed feedback.csv 
		# row = map(str, [name, feedback, rating])

		# with open('feedback.csv', 'a', newline='') as file:
		# 	writer = csv.writer(file)
		# 	writer.writerow(row)
		# 	file.close()

		# Posts a webhook to IFTTT to send me a email when someone submits a feedback
		requests.post(WEBHOOK_URL, {'value1': name, 'value2': rating, 'value3': feedback}) 

		return render_template('feedback.html', msg='Thank you for your valuable feedback')

	else:
		return render_template('feedback.html', msg=None)


if __name__ == "__main__":
	app.run()
