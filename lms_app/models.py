from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from lms_app import db, login_manager
from slugify import slugify

# -------------------------
# 📚 User Model
# -------------------------

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)
    active = db.Column(db.Boolean, default=True)
    transactions = db.relationship('Transaction', back_populates='user', lazy='dynamic')
    feedbacks = db.relationship('Feedback', back_populates='user', lazy='dynamic')

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False
        
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    

# -------------------------
# 📗 Book Model
# -------------------------
class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    author = db.Column(db.String(150), nullable=False)
    genre = db.Column(db.String(100))
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    cover = db.Column(db.String(255))
    publication_year = db.Column(db.Integer)
    isbn = db.Column(db.String(20))

    # 📖 Initialize Book
    def __init__(self, title, author, genre, description, quantity=1, cover=None, publication_year=None, isbn=None):
        self.title = title
        self.slug = self.generate_unique_slug(title)
        self.author = author
        self.genre = genre
        self.description = description 
        self.quantity = quantity
        self.cover = cover
        self.publication_year = publication_year
        self.isbn = isbn

    def generate_unique_slug(self, title):
        base_slug = slugify(str(title))
        slug = base_slug
        counter = 1

        while Book.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    transactions = db.relationship('Transaction', back_populates='book', lazy='dynamic')
    feedbacks = db.relationship('Feedback', back_populates='book', lazy='dynamic')

    @property
    def availability(self):
        borrowed = Transaction.query.filter_by(book_id=self.id, status='Borrowed').count()
        if self.quantity - borrowed <= 0:
            return "Currently Unavailable"
        return "Available"



# -------------------------
# 📊 Transaction Model
# -------------------------
class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    fine_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Borrowed', nullable=False)

    user = db.relationship('User', back_populates='transactions')
    book = db.relationship('Book', back_populates='transactions')

# -------------------------
# 💬 Feedback Model
# -------------------------
class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='feedbacks')
    book = db.relationship('Book', back_populates='feedbacks')