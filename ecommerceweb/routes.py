from flask import render_template, url_for, flash, redirect, request
from ecommerceweb import app, db, bcrypt
from ecommerceweb.forms import RegistrationForm, LoginForm, UpdateAccountForm
from ecommerceweb.dbmodel import User
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/product")
def product():
    return render_template('product_desc.html', title='Product Details')


@app.route("/signup", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.contactno = form.contactno.data
        current_user.address_line1 = form.addr1.data
        current_user.address_line2 = form.addr2.data
        current_user.address_line3 = form.addr3.data
        current_user.pincode = form.pincode.data
        current_user.city = form.city.data
        current_user.state = form.state.data
        current_user.country = form.country.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        print(current_user.name)
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.contactno.data = current_user.contactno
        form.addr1.data = current_user.address_line1
        form.addr2.data = current_user.address_line2
        form.addr3.data = current_user.address_line3
        form.pincode.data = current_user.pincode
        form.city.data = current_user.city
        form.state.data = current_user.state
        form.country.data = current_user.country

    return render_template('account.html', title='Account', form=form)
   