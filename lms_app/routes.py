from flask import Blueprint, render_template, redirect, url_for, flash, request, abort,  current_app,  session
from .models import User, Book, Transaction, Feedback
from . import db
from .forms import BookForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import func, extract
from sqlalchemy.exc import SQLAlchemyError
from lms_app import db
from lms_app.models import Transaction
from datetime import datetime, timedelta
from slugify import slugify
import os
import time
import plotly.express as px
import pandas as pd
from flask_wtf.csrf import CSRFProtect

main = Blueprint('main', __name__)

@main.after_request
def add_ngrok_header(response):
    response.headers['ngrok-skip-browser-warning'] = 'true'
    return response

@main.route('/search')
def search_books():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    if query:
        search = f"%{query}%"
        books_query = Book.query.filter(
            (Book.title.ilike(search)) |
            (Book.author.ilike(search)) |
            (Book.genre.ilike(search)) |
            (Book.description.ilike(search))
        )
    else:
        books_query = Book.query
    
    books = books_query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('search_results.html', books=books, query=query)

# 🏠 Home Page
@main.route('/')
def index():
    current_time = datetime.now()
    current_year = current_time.year
    return render_template('index.html', current_time=current_time, current_year=current_year)

# 🔑 Login
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            if user.is_active:
                login_user(user)
                flash("Logged in successfully! ✅", "success")
                return redirect(url_for('main.admin_dashboard' if user.role == 'admin' else 'main.user_dashboard'))
            else:
                flash("Account is inactive. Please contact admin.", "warning")
        else:
            flash("Invalid username or password.", "danger")

    return render_template('login.html')

# 📝 Register
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')  # ✅ Capture email
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not email or not password:
            flash("All fields are required!", "warning")
            return redirect(url_for('main.register'))

        if password != confirm_password:
            flash("Passwords do not match!", "warning")
            return redirect(url_for('main.register'))

        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return redirect(url_for('main.register'))

        if User.query.filter_by(username=username).first():
            flash("Username is already taken.", "danger")
            return redirect(url_for('main.register'))

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, email=email, password_hash=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error during registration: {e}", "danger")
            return redirect(url_for('main.register'))

    return render_template('register.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out. 👋", "success")
    return redirect(url_for('main.login'))

@main.route('/user_dashboard')
@login_required
def user_dashboard():

    current_loans = Transaction.query.filter_by(user_id=current_user.id, status='Borrowed').all()

    borrowing_history = Transaction.query.filter_by(user_id=current_user.id, status='Returned').all()

    borrowed_genres = db.session.query(Book.genre, func.count(Book.id))\
        .join(Transaction, Book.id == Transaction.book_id)\
        .filter(Transaction.user_id == current_user.id)\
        .group_by(Book.genre)\
        .order_by(func.count(Book.id).desc())\
        .first()

    if borrowed_genres:
        recommended_books = Book.query.filter_by(genre=borrowed_genres[0]).limit(5).all()
    else:
        recommended_books = Book.query.limit(5).all()

    return render_template('user_dashboard.html',
                           current_loans=current_loans,
                           borrowing_history=borrowing_history,
                           recommended_books=recommended_books)

def hex_to_rgba(hex_color, alpha=1.0):
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"

@main.route('/analytics')
@login_required

def analytics_dashboard():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_loans = Transaction.query.filter_by(user_id=current_user.id, status='Borrowed').all()
    reading_history = Transaction.query.filter_by(user_id=current_user.id, status='Returned').all()
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    total_borrowed = len(current_loans + reading_history)
    total_returned = len(reading_history)
    total_overdue = len([t for t in current_loans if t.due_date < datetime.utcnow()])

    theme = current_app.config['THEME_COLORS']

    daily_borrows = db.session.query(
        func.date(Transaction.borrow_date).label('date'),
        func.count(Transaction.id).label('count')
    ).filter(
        extract('month', Transaction.borrow_date) == current_month,
        extract('year', Transaction.borrow_date) == current_year,
        Transaction.user_id == current_user.id
    ).group_by('date').all()
    
    df_daily = pd.DataFrame(daily_borrows, columns=['Date', 'Books Borrowed'])
    
    fig_line = px.line(df_daily, x='Date', y='Books Borrowed', 
                      title='<b>Your Progress this Month</b>',
                      template='plotly_dark',
                      markers=True,
                      line_shape='spline')
    
    fig_line.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=theme['text'],
        title_font_size=20,
        title_x=0.03,
        hovermode='x unified',
        xaxis_title=None,
        yaxis_title='Books Borrowed',
        margin=dict(l=40, r=20, t=80, b=40),
        xaxis=dict(
            showgrid=False,
            linecolor=theme['secondary'],
            tickfont=dict(color=theme['text'])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=hex_to_rgba(theme['secondary'], 0.2),  # Use the new function
            linecolor=theme['secondary'],
            tickfont=dict(color=theme['text'])
        ),
        hoverlabel=dict(
            bgcolor=theme['background'],
            font_size=14,
            font_color=theme['text']
        )
    )
    
    fig_line.update_traces(
        line=dict(width=3, color=theme['primary']),
        marker=dict(size=8, color=theme['primary']),
        hovertemplate='<b>%{x}</b><br>%{y} Books'
    )
    
    line_graph = fig_line.to_html(full_html=False)

    metrics_data = {
        'Category': ['Borrowed', 'Returned', 'Overdue'],
        'Count': [total_borrowed, total_returned, total_overdue]
    }
    df_metrics = pd.DataFrame(metrics_data)
    
    fig_donut = px.pie(df_metrics, names='Category', values='Count', 
                        hole=0.6,
                        title='<b>Borrow-Return Ratio</b>',
                        color='Category',
                        color_discrete_map={
                            'Borrowed': theme.get('primary', '#4361ee'),
                            'Returned': theme.get('success', '#4CAF50'),
                            'Overdue': theme.get('danger', '#FF5252')
                        })
    
    fig_donut.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=theme['text'],
        title_font_size=20,
        title_x=0.1,
        margin=dict(t=80, b=20),
        showlegend=False,
        annotations=[dict(
            text=f'{total_borrowed}',
            x=0.5, y=0.5,
            font_size=28,
            showarrow=False,
            font_color=theme['text']
        )]
    )
    
    fig_donut.update_traces(
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>',
        marker=dict(line=dict(color=theme['background'], width=2))
    )
    
    donut_graph = fig_donut.to_html(full_html=False)
                  
    return render_template('analytics.html',
                            current_time=current_time,
                            current_loans=current_loans,
                            reading_history=reading_history,
                            total_borrowed=total_borrowed,
                            total_returned=total_returned,
                            total_overdue=total_overdue,
                            line_graph=line_graph,
                            donut_graph=donut_graph)


@main.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)

    borrow_trends = db.session.query(Book.title, func.count(Transaction.id).label('borrow_count'))\
        .join(Transaction, Book.id == Transaction.book_id)\
        .group_by(Book.title)\
        .order_by(func.count(Transaction.id).desc())\
        .limit(5).all()

    top_book = db.session.query(Book.title, func.count(Transaction.id).label('borrow_count'))\
        .join(Transaction, Book.id == Transaction.book_id)\
        .group_by(Book.title)\
        .order_by(func.count(Transaction.id).desc())\
        .first()

    total_books = Book.query.count()
    borrowed_books = Transaction.query.filter_by(status='Borrowed').count()
    available_books = total_books - borrowed_books
    books = Book.query.all()

    active_users = db.session.query(User.username, func.count(Transaction.id).label('books_borrowed'))\
        .join(Transaction, User.id == Transaction.user_id)\
        .group_by(User.username)\
        .order_by(func.count(Transaction.id).desc())\
        .limit(5).all()

    return render_template('admin_dashboard.html',
                           books=books,  # 🟢 Added books to template context
                           borrow_trends=borrow_trends,
                           top_book=top_book,
                           total_books=total_books,
                           borrowed_books=borrowed_books,
                           available_books=available_books,
                           active_users=active_users)

@main.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)  # Initialize the form with the book data
    current_year = datetime.now().year

    if form.validate_on_submit():
        try:
            # Update book attributes
            book.title = form.title.data
            book.author = form.author.data
            book.genre = form.genre.data
            book.category = form.category.data
            book.description = form.description.data
            book.quantity = form.quantity.data
            book.publication_year = form.publication_year.data
            book.isbn = form.isbn.data

            db.session.commit()
            flash('Book updated successfully!', 'success')
            
            # Redirect based on user role
            if current_user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            else:
                return redirect(url_for('main.user_dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating book: {str(e)}', 'danger')
            current_app.logger.error(f'Error updating book {book_id}: {str(e)}')  # Log the error for debugging

    else:
        # If form validation fails, log the errors
        current_app.logger.warning(f'Form validation failed for book {book_id}: {form.errors}')

    return render_template('edit_book.html', 
                           form=form, 
                           book=book,
                           current_year=current_year)
                         
@main.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    try:
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting book', 'danger')
    
    return redirect(url_for('main.admin_dashboard'))

@main.route('/book/<slug>', methods=['GET'])
@login_required
def book_details(slug):
    book = Book.query.filter_by(slug=slug).first_or_404()
    feedbacks = Feedback.query.filter_by(book_id=book.id).all()
    average_rating = db.session.query(func.avg(Feedback.rating)).filter_by(book_id=book.id).scalar() or 0

    active_transaction = Transaction.query.filter_by(
        book_id=book.id,
        status='Borrowed'
    ).order_by(Transaction.due_date.desc()).first()

    return render_template(
        'book_details.html',
        book=book,
        feedbacks=feedbacks,
        average_rating=average_rating,
        active_transaction=active_transaction  # Add this
    )

@main.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    try:

        book = Book.query.get_or_404(book_id)

        if book.quantity < 1:
            flash('This book is out of stock and cannot be borrowed.', 'warning')
            return redirect(url_for('main.book_details', book_id=book_id))

        existing_transaction = Transaction.query.filter_by(
            user_id=current_user.id,
            book_id=book_id,
            status='Borrowed'
        ).first()

        if existing_transaction:
            flash('You already have an active borrow for this book.', 'warning')
            return redirect(url_for('main.book_details', book_id=book_id))

        due_date = datetime.utcnow() + timedelta(days=14)
        new_transaction = Transaction(
            user_id=current_user.id,
            book_id=book_id,
            due_date=due_date,
            status='Borrowed'
        )

        book.quantity -= 1

        db.session.add(new_transaction)
        db.session.commit()

        current_app.logger.info(f'User {current_user.id} borrowed book {book_id}')
        flash(f"Book successfully borrowed! Due by {due_date.strftime('%Y-%m-%d')}", 'success')
        return redirect(url_for('main.user_dashboard'))

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Borrow error: {str(e)}', exc_info=True)
        flash('Failed to process your borrow request. Please try again.', 'danger')
        return redirect(url_for('main.book_details', book_id=book_id))

@main.route('/return/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def return_book(transaction_id):

    transaction = Transaction.query.get_or_404(transaction_id)
    book = transaction.book
    
    if transaction.user_id != current_user.id:
        current_app.logger.warning(f'Unauthorized access attempt by user {current_user.id}')
        abort(403)
    if transaction.status != 'Borrowed':
        flash('This book has already been returned.', 'info')
        return redirect(url_for('main.user_dashboard'))

    feedbacks = Feedback.query.filter_by(book_id=book.id).all()

    average_rating = db.session.query(func.avg(Feedback.rating)).filter_by(book_id=book.id).scalar() or 0

    if request.method == 'POST':

        rating = request.form.get('rating', type=int)
        message = request.form.get('message', '').strip()
        
        session['returning_transaction'] = transaction_id

        if not rating or not message:
            flash('Both rating and feedback message are required.', 'danger')
            return redirect(url_for('main.return_book', transaction_id=transaction_id))

        try:

            feedback = Feedback(
                user_id=current_user.id,
                book_id=book.id,
                rating=rating,
                message=message
            )
            db.session.add(feedback)

            transaction.return_date = datetime.utcnow()

            book.quantity += 1
            
            if transaction.return_date > transaction.due_date:
                days_overdue = (transaction.return_date - transaction.due_date).days
                transaction.fine_amount = days_overdue * 1.0
                transaction.status = 'Overdue'
                flash_msg = f'Book returned late. Fine: ${transaction.fine_amount:.2f}'
            else:
                transaction.status = 'Returned'
                flash_msg = 'Book returned successfully! ✅'

            db.session.commit()
            current_app.logger.info(f'Transaction {transaction_id} returned successfully')

            # Clear the session after successful return
            session.pop('returning_transaction', None)  # 👈 Clear session data

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Return failed: {str(e)}', exc_info=True)
            flash('An error occurred while processing your return.', 'danger')
            return redirect(url_for('main.user_dashboard'))

        flash(flash_msg, 'success')
        return redirect(url_for('main.user_dashboard'))

    # GET request - show feedback form
    return render_template('feedback.html',
                         book=book,
                         feedbacks=feedbacks,  # Pass the evaluated list of feedbacks
                         average_rating=round(average_rating, 1))  # Pass the average rating
    
# 🟢 Clear Fine (User/Manual)
@main.route('/clear_fine/<int:transaction_id>', methods=['POST'])
@login_required
def clear_fine(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.fine_amount > 0:
        transaction.fine_amount = 0
        db.session.commit()
        flash('Fine cleared. 💸', 'success')
    return redirect(url_for('main.user_dashboard'))

@main.route('/add_feedback/<int:book_id>', methods=['GET', 'POST'])
@login_required
def add_feedback(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        message = request.form.get('message')
        rating = request.form.get('rating')

        transaction_id = session.get('returning_transaction')
        if transaction_id:
            transaction = Transaction.query.get(transaction_id)

            if transaction:
                transaction.status = 'Returned'
                transaction.return_date = datetime.utcnow()
                db.session.commit()
                session.pop('returning_transaction', None)
                flash("Book successfully returned and feedback submitted! 📚✅", "success")

                return redirect(url_for('main.user_dashboard'))

        flash("Error processing return. Please try again.", "danger")


        if not message:
            flash('Message is required!', 'danger')
            return render_template('feedback.html', book=book)

        feedback = Feedback(user_id=current_user.id, book_id=book.id, message=message, rating=rating)

        try:
            db.session.add(feedback)
            db.session.commit()
            flash('Feedback submitted!', 'success')
            return redirect(url_for('main.book_details', slug=book.slug))
        except Exception as e:
            db.session.rollback()  # Rollback the session on error
            flash(f'Error submitting feedback: {e}', 'danger')

    book = Book.query.get_or_404(book_id)
    feedbacks = Feedback.query.filter_by(book_id=book.id).all()  # Fetch existing feedbacks for the book
    return render_template('feedback.html', book=book, feedbacks=feedbacks)  # Pass the book and feedbacks

# 👑 Secure Admin Registration (with Secret Key in URL Params)
@main.route('/adminreg', methods=['GET', 'POST'])
def admin_register():
    secret_key = request.args.get('key')
    if secret_key != 'sinigangmix':
        abort(403)

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')  # 🟢 Capture Email
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        # ✅ Check for Missing Fields
        if not username or not email or not password:
            flash('All fields are required!', 'warning')
            return redirect(url_for('main.admin_register', key=secret_key))

        new_admin = User(username=username, email=email, password_hash=hashed_password, role='admin')

        try:
            db.session.add(new_admin)
            db.session.commit()
            flash('Admin registration successful! ✅ Please log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            flash(f'Error during admin registration: {e}', 'danger')


    return render_template('adminreg.html')

@main.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if current_user.role != 'admin':
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        description = request.form.get('description')
        quantity = request.form.get('quantity', type=int)
        cover_file = request.files.get('cover')
        cover_filename = None

        if cover_file and cover_file.filename != '':
            cover_dir = os.path.join(current_app.root_path, 'static', 'covers')
            os.makedirs(cover_dir, exist_ok=True)
            
            cover_filename = f"{slugify(title)}-{int(time.time())}.{secure_filename(cover_file.filename).split('.')[-1]}"
            cover_path = os.path.join(cover_dir, cover_filename)
            cover_file.save(cover_path)

        if not title or not author or quantity is None or quantity < 1:
            flash("Title, Author, and Quantity (must be at least 1) are required.", "warning")
            return redirect(url_for('main.add_book'))

        # Save Book
        new_book = Book(
            title=title,
            author=author,
            genre=genre,
            description=description,
            quantity=quantity,
            cover=cover_filename,
            publication_year=request.form.get('publication_year', None),
            isbn=request.form.get('isbn', None)
        )

        db.session.add(new_book)
        db.session.commit()
        flash("Book added successfully! 📚", "success")
        return redirect(url_for('main.admin_dashboard'))

    return render_template('add_book.html')
   
@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main.route('/terms')
def terms():
    return render_template('terms.html')

@main.route('/contacts')
def contacts():
    return render_template('contacts.html')