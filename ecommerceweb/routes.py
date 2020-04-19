import os
import secrets
from flask import render_template, url_for, flash, redirect, request, session, g, abort
from ecommerceweb import app, db, bcrypt, mail
from ecommerceweb.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                                QuantityForm, PaymentDetails, SearchForm,
                                RequestResetForm, ResetPasswordForm)
from ecommerceweb.dbmodel import User, Product, Category, Cart, UserTransac, Order, Shipping, Seller
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from datetime import datetime, timedelta
import base64

b = []

@app.before_request
def before_request():
    g.search_form = SearchForm()

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About Us')

@app.route('/search', methods=['POST'])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('home'))
    return redirect(url_for('search_results', query=g.search_form.search.data))

@app.route('/search_results/<query>')
def search_results(query):
    qstring = "%{}%".format(query)
    prod = Product.query.filter(Product.name.like(qstring)).all()
    length = len(prod)
    img=[]
    for p in prod:
        img.append(base64.b64encode(p.image_file1).decode('ascii'))
    return render_template('search_results.html', title='Search Results', query=query, prod=prod, length=length, img=img)

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
            if 'url' in session and session['url'] != None:
                return redirect(session['url'])
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    global b
    b = []
    logout_user()
    return redirect(url_for('home'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

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
   

@app.route("/<string:catname>")
def categorypage(catname):
    c=0
    title=""
    if catname=="handicrafts":
        c=1
        title="Handicrafts"
    elif catname=="homedecor":
        c=2
        title="Home Decor"
    elif catname=="ayurvedicproducts":
        c=3
        title="Ayurvedic Products"
    elif catname=="khadiclothproducts":
        c=4
        title="Khadi Cloth Products"
    elif catname=="jewellery":
        c=5
        title="Jewellery"
    else:
        return redirect(url_for('home'))
    prod=Product.query.filter_by(category_id=c).all()
    img=[]
    for p in prod:
        img.append(base64.b64encode(p.image_file1).decode('ascii'))
    return render_template('category.html', prod=prod, img=img, l=len(prod), title=title)

@app.route("/product<int:id>", methods=['GET', 'POST'])
def product(id):
    session['url'] = None
    global b
    prod = Product.query.filter_by(pid=id).first_or_404("This product does not exist")
    seller = Seller.query.filter_by(sid=prod.sid).first()
    img=[]
    img.append(base64.b64encode(prod.image_file1).decode('ascii'))
    if prod.image_file2:
        img.append(base64.b64encode(prod.image_file2).decode('ascii'))
    if prod.image_file3:
        img.append(base64.b64encode(prod.image_file3).decode('ascii'))
    if prod.image_file4:
        img.append(base64.b64encode(prod.image_file4).decode('ascii'))
    form=QuantityForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            session['url'] = url_for('product', id=id)
            flash('You must log in first', 'danger')  
            return redirect(url_for('login'))
        else:
            if form.buy.data:
                if(form.quantity.data > prod.stock):
                    s = 'Requested quantity exceeds stock. Only {stock} pieces available'.format(stock=prod.stock)
                    flash(s, 'danger')
                else:
                    l = []
                    b = []
                    user = User.query.filter_by(id=current_user.id).first()
                    l.extend([user.name, id, prod.name, form.quantity.data, prod.cost*form.quantity.data])
                    b.append(l)
                    print(b)
                    return redirect(url_for('checkout'))
            elif form.add.data:
                if(form.quantity.data > prod.stock):
                    s='Requested quantity exceeds stock. Only {stock} pieces available'.format(stock=prod.stock)
                    flash(s, 'danger')
                else:
                    cart = Cart.query.filter_by(pid=id).first()
                    if cart != None:
                        cart.quantity += form.quantity.data
                        db.session.commit()
                    else:
                        c = Cart(uid=current_user.id, pid=id, quantity=form.quantity.data)
                        db.session.add(c)
                        db.session.commit()
                    flash('The product was added to your cart!', 'success')
    return render_template('product_desc.html', title='Product Details', prod=prod, img=img, form=form, seller=seller)

@app.route("/cart")
@login_required
def cart():
    c = Cart.query.filter_by(uid=current_user.id).all()
    p=[]
    cost=[]
    for i in range(len(c)):
        prod = Product.query.filter_by(pid=c[i].pid).first()
        p.append(prod.name)
        cost.append(prod.cost * c[i].quantity)
    total=sum(cost)
    return render_template('cart.html', title='Cart', p=p, cost=cost, c=c, total=total, l=len(c))

@app.route("/removeitem<int:id>")
@login_required
def removeitem(id):
    c = Cart.query.filter_by(uid=current_user.id).all()
    if len(c)==0:
        flash('No item to remove from cart', 'warning')
        return redirect(url_for('home'))
    else:
        flag = False
        for i in range(len(c)):
            if id == c[i].pid:
                flag = True
                Cart.query.filter_by(uid=current_user.id, pid=id).delete()
                db.session.commit()
                flash('The item was removed from the cart', 'success')
                break
        if not flag:
            flash('Item not present in cart', 'warning')
    p=[]
    cost=[]
    c = Cart.query.filter_by(uid=current_user.id).all()
    for i in range(len(c)):
        prod = Product.query.filter_by(pid=c[i].pid).first()
        p.append(prod.name)
        cost.append(prod.cost * c[i].quantity)
    total=sum(cost)
    return render_template('cart.html', title='Cart', p=p, cost=cost, c=c, total=total, l=len(c))

@app.route("/checkout", methods=['GET', 'POST'])
@login_required 
def checkout():
    global b
    print(b)
    c = Cart.query.filter_by(uid=current_user.id).all()
    if c==[] and b==[]:
        flash('No product has been selected', 'warning')
        return redirect(url_for('home'))
    elif len(b)!=0:
        form = PaymentDetails()
        if form.validate_on_submit():
            p = Product.query.filter_by(pid=b[0][1]).first()
            o = Order(uid=current_user.id, pid=b[0][1], order_status="Ordered", quantity=b[0][3], total=p.cost*b[0][3])
            db.session.add(o)
            db.session.commit()
            u = UserTransac(uid=current_user.id, oid=o.oid, upiid=form.upiid.data, quantity=b[0][3], total=p.cost*b[0][3])
            db.session.add(u)
            db.session.commit()
            delivery_date=datetime.utcnow()+timedelta(days=4)
            shipping = Shipping(oid=o.oid, transac_id=u.transac_id, delivery_date=delivery_date, contactno=form.contactno.data, 
                                address_line1=form.addr1.data, address_line2=form.addr2.data, address_line3=form.addr3.data, 
                                pincode=form.pincode.data, city=form.city.data, state=form.state.data, country=form.country.data)
            db.session.add(shipping)
            db.session.commit()
            flash('Your order was processed successfully! An email was sent confirming your order', 'success')
            p.stock-=int(b[0][3])
            db.session.commit()
            msg = Message('Order Confirmation', sender='noreply@demo.com', recipients=[current_user.email])
            msg.body = f'''Your order was confirmed! Details:
            Product Name:{p.name}
            Order ID: {o.oid}
            Expected Delivery Date: {delivery_date}
            Transaction Details: {url_for('transaction', transac_id=u.transac_id, _external=True)}
                '''
            mail.send(msg)

            print('before invoice')
            return redirect(url_for('invoice'))
        elif request.method == 'GET':
            form.contactno.data = current_user.contactno
            form.addr1.data = current_user.address_line1
            form.addr2.data = current_user.address_line2
            form.addr3.data = current_user.address_line3
            form.pincode.data = current_user.pincode
            form.city.data = current_user.city
            form.state.data = current_user.state
            form.country.data = current_user.country
        return render_template('checkout.html', title='Checkout', form=form)
    else:
        print('cart has some products')
        user = User.query.filter_by(id=current_user.id).first()
        form = PaymentDetails()
        cost=[]
        if form.validate_on_submit():
            body = f'''Your order was confirmed! Details:
            '''
            for i in range(len(c)):
                l=[]
                prod = Product.query.filter_by(pid=c[i].pid).first()
                cost.append(prod.cost * c[i].quantity)
                o = Order(uid=current_user.id, pid=c[i].pid, order_status="Ordered", quantity=c[i].quantity, total=cost[i])
                db.session.add(o)
                db.session.commit()
                u = UserTransac(uid=current_user.id, oid=o.oid, upiid=form.upiid.data, quantity=c[i].quantity, total=cost[i])
                db.session.add(u)
                db.session.commit()
                delivery_date=datetime.utcnow()+timedelta(days=4)
                shipping = Shipping(oid=o.oid, transac_id=u.transac_id, delivery_date=delivery_date, contactno=form.contactno.data, 
                                    address_line1=form.addr1.data, address_line2=form.addr2.data, address_line3=form.addr3.data, 
                                    pincode=form.pincode.data, city=form.city.data, state=form.state.data, country=form.country.data)
                db.session.add(shipping)
                db.session.commit()
                prod.stock-=c[i].quantity
                db.session.commit()
                l.extend([user.name, prod.pid, prod.name, c[i].quantity, cost[i]])
                b.append(l)
                body+=f'''Product name: {prod.name}
                Order ID: {o.oid}
                Expected Delivery Date: {delivery_date}
                Transaction Details: {url_for('transaction', transac_id=u.transac_id, _external=True)}
                
                '''
            flash('Your order was processed successfully! An email was sent confirming your order', 'success')
            msg = Message('Order Confirmation', sender='noreply@demo.com', recipients=[current_user.email])
            msg.body = body
            mail.send(msg)
            Cart.query.filter_by(uid=user.id).delete()
            db.session.commit()
            return redirect(url_for('invoice'))
        elif request.method == 'GET':
            form.contactno.data = current_user.contactno
            form.addr1.data = current_user.address_line1
            form.addr2.data = current_user.address_line2
            form.addr3.data = current_user.address_line3
            form.pincode.data = current_user.pincode
            form.city.data = current_user.city
            form.state.data = current_user.state
            form.country.data = current_user.country

        return render_template('checkout.html', title='Checkout', form=form)

@app.route("/invoice")
@login_required 
def invoice():
    global b
    b1 = b
    print(b1)
    b = []
    return render_template('invoice.html', inv=b1, length=len(b1))

@app.route("/orders")
@login_required     
def orders():
    order = Order.query.filter_by(uid=current_user.id).all()
    pname = []
    txn = []
    for i in range(len(order)):
        p = Product.query.filter_by(pid=order[i].pid).first()
        pname.append(p.name)
        t = UserTransac.query.filter_by(oid=order[i].oid).first_or_404()
        txn.append(t.transac_id)
    return render_template('orders.html', title='Your Orders', order=order, l=len(order), pname=pname, txn=txn)

@app.route("/transaction<int:transac_id>")
@login_required     
def transaction(transac_id):
    transaction = UserTransac.query.filter_by(transac_id=transac_id).first_or_404()
    if transaction.uid != current_user.id:
        flash('You do not have the authority to view that transaction', 'warning')
        return redirect(url_for('home'))
    return render_template('transaction.html',title='Transaction Details', transaction=transaction)

@app.route("/shipping<int:id>")
@login_required     
def shipping(id):
    ship = Shipping.query.filter_by(oid=id).first_or_404()
    order = Order.query.filter_by(oid=id).first_or_404()
    if order.uid != current_user.id:
        flash('You do not have the authority to visit this page', 'warning')
        return redirect(url_for('home'))
    return render_template('ship.html',title='Shipping Details', ship=ship)