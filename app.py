from flask import Flask, redirect, request, render_template, jsonify, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from main import get_book_recommendations, cosine_sim
import pickle
import pandas as pd
import sqlite3
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = b'\xa3\xc2\x8f\xd3\xe7\x1a\xbb\x93\xe4\x8d\xfb\xc5\x2d\xbf\xa9\x86\x43\x1d\xe8\xfc\x5a\x3b\x2c\x59'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Veritabanı fonksiyonu
def insert_contact(name, email, message):
    conn = sqlite3.connect('contact.db')
    c = conn.cursor()
    c.execute('INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)', (name, email, message))
    conn.commit()
    conn.close()
    print(f"Contact inserted: {name}, {email}, {message}")

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class FavoriteBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_title = db.Column(db.String(250), nullable=False)
    author = db.Column(db.String(250), nullable=False)
    image_url = db.Column(db.String(250), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Veri setlerini yükleme
books = pd.read_csv('dataset/books.csv')
book_tags = pd.read_csv('dataset/book_tags.csv')
tags = pd.read_csv('dataset/tags.csv')

# pickle dosyalarından öneri modellerinin yüklenmesi
pbr_df = pickle.load(open('PopularBookRecommendation.pkl', 'rb'))

# zip fonksiyonunu Jinja2'de kullanmak için ekleyin
app.jinja_env.globals.update(zip=zip)



@app.route('/')
def index():
    favorites = []
    if current_user.is_authenticated:
        favorites = [fav.book_title for fav in FavoriteBook.query.filter_by(user_id=current_user.id).all()]
        
    return render_template('index.html',
                           book_name=list(pbr_df['title'].values[:50]),
                           author=list(pbr_df['authors'].values[:50]),
                           image=list(pbr_df['image_url'].values[:50]),
                           votes=list(pbr_df['ratings_count'].values[:50]),
                           rating=list(pbr_df['average_rating'].values[:50]),
                           favorites=favorites)

@app.route('/recommender')
def recommender():
    return render_template('recommender.html')

@app.route('/book_list')
def book_list():
    query = request.args.get('query', '').lower()
    results = books[books['title'].str.lower().str.startswith(query)][['title']].head(10).to_dict('records')
    return jsonify(results)

@app.route('/recommend', methods=['POST'])
def recommend():
    book_title = request.form['book_title']
    recommendations = get_book_recommendations(book_title, books, cosine_sim)
    return jsonify(recommendations)

@app.route('/search/<book_name>')
def search(book_name):
    amazon_url = f"https://www.amazon.com/s?k={book_name.replace(' ', '+')}"
    return redirect(amazon_url)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash('Login failed. Check username and/or password', 'danger')
            return redirect(url_for('login'))

        login_user(user)
        flash('Login successful', 'success')
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            message = request.form['message']
            
            # Veritabanına kaydet
            insert_contact(name, email, message)
            
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred: {e}', 'danger')
            print(f'Error: {e}')
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/add_to_favorites', methods=['POST'])
@login_required
def add_to_favorites():
    book_title = request.form['book_title']
    author = request.form['author']
    image_url = request.form['image_url']

    # Aynı kitabın favorilere eklenip eklenmediğini kontrol edin
    existing_favorite = FavoriteBook.query.filter_by(user_id=current_user.id, book_title=book_title).first()
    if existing_favorite:
        flash('Book is already in favorites', 'warning')
    else:
        new_favorite = FavoriteBook(user_id=current_user.id, book_title=book_title, author=author, image_url=image_url)
        db.session.add(new_favorite)
        db.session.commit()
        flash('Book added to favorites', 'success')
    
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    favorite_books = FavoriteBook.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', favorite_books=favorite_books)

@app.route('/remove_from_favorites', methods=['POST'])
@login_required
def remove_from_favorites():
    book_title = request.form['book_title']
    favorite_book = FavoriteBook.query.filter_by(book_title=book_title, user_id=current_user.id).first()
    if favorite_book:
        db.session.delete(favorite_book)
        db.session.commit()
        flash('Book removed from favorites', 'success')
    else:
        flash('Book not found in favorites', 'danger')
    return redirect(url_for('index'))

def is_favorite(book_title):
    if not current_user.is_authenticated:
        return False
    favorite_book = FavoriteBook.query.filter_by(user_id=current_user.id, book_title=book_title).first()
    return favorite_book is not None

app.jinja_env.globals.update(is_favorite=is_favorite)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
