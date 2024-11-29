import datetime

from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from app.models.purchase import Purchase
from app.models.reviews import Review
from app.models.user import User
from app.models.product import Product


from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    address = StringField('Address', validators=[DataRequired()])
    seller = BooleanField('Seller?')
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.address.data,
                         form.seller.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))


@bp.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')


@bp.route('/user-info', methods=['POST', 'GET'])
def user_info():
    if current_user.is_authenticated:
        firstname = request.form.get('firstname')

        if firstname:
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            address = request.form.get('address')
            balance = request.form.get('balance')
            oldpassword = request.form.get('oldpassword')
            newpassword = request.form.get('newpassword')

            if len(newpassword) > 0:
                password = generate_password_hash(newpassword)
            else:
                password = generate_password_hash(oldpassword)

            user = User.get_by_auth(email, oldpassword)

            if user is None:
                flash('Invalid password!', 'warning')
            else:
                successful = User.update_info(current_user.id,
                                            password,
                                            firstname,
                                            lastname,
                                            email,
                                            address,
                                            balance
                                            )

                if not successful:
                    flash("That email is already in use!", "warning")
                else:
                    flash('Info successfully updated!')
            
        # get user info
        user = User.get(current_user.id)
    else:
        user = None

    return render_template('user_info.html', user=user)


@bp.route('/created-products', methods=['GET'])
def created_products():
    page = request.args.get('page', 1, type=int)
    per_page = 9
    offset = (page - 1) * per_page

    if current_user.is_authenticated:
        all_products = Product.get_user_products(current_user.id)

        products_count = len(all_products)
        products = all_products[offset:offset+per_page]
    else:
        products_count = 0
        products = None

    # Calculate total pages based on the count of created products
    total_pages = (products_count + per_page - 1) // per_page  # Calculate the number of pages

    return render_template(
        'my_products.html',
        products=products,
        page=page,
        total_pages=total_pages
        )


@bp.route('/purchase-history', methods=['GET'])
def order_history():
    page = request.args.get('page', 1, type=int)
    per_page = 3
    offset = (page - 1) * per_page

    if current_user.is_authenticated:
        # Find the products current user has bought to display on current page
        all_purchases = Purchase.get_all_purchased_by_uid(uid=current_user.id)

        all_orders = {}
        for purchase in all_purchases:
            time = purchase.time_purchased

            if time not in all_orders:
                all_orders[time] = []

            all_orders[time].append(purchase)
        
        all_orders = list(all_orders.items())
        orders_count = len(all_orders)
        orders = all_orders[offset:offset+per_page]
    else:
        orders_count = 0
        orders = None

    # Calculate total pages based on the count of purchases
    total_pages = (orders_count + per_page - 1) // per_page  # Calculate the number of pages

    return render_template(
        'order_history.html',
        orders=orders,
        page=page,
        total_pages=total_pages
        )


@bp.route('/review-history', methods=['GET'])
def review_history():
    page = request.args.get('page', 1, type=int)
    per_page = 3
    offset = (page - 1) * per_page

    if current_user.is_authenticated:
        # get most recent reviews
        all_reviews = Review.get_recent_reviews(current_user.id)

        reviews_count = len(all_reviews)
        reviews = all_reviews[offset:offset+per_page]
    else:
        reviews_count = 0
        reviews = None
    
    # Calculate total pages based on the count of reviews
    total_pages = (reviews_count + per_page - 1) // per_page  # Calculate the number of pages

    return render_template(
        'review_history.html',
        reviews=reviews,
        page=page,
        total_pages=total_pages
        )


@bp.route('/edit-profile')
def edit_profile():
    if current_user.is_authenticated:
        # get user info
        user = User.get(current_user.id)
    else:
        user = None

    return render_template('edit_profile.html',
                    user=user,
                    )
