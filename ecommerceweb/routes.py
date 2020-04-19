import os
import secrets
from flask import render_template, url_for, flash, redirect, request, session, g, abort
from ecommerceweb import app, db, bcrypt, mail
from ecommerceweb.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                                QuantityForm, ShippingDetails, SearchForm,
                                RequestResetForm, ResetPasswordForm)
from ecommerceweb.dbmodel import User, Product, Category, Cart, UserTransac, Order, Shipping, Seller
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from datetime import datetime, timedelta
import stripe
import base64

b = []
body = f''''''
ship = []
order = []
stock = []
product = []
stripe_keys = {
  'secret_key': os.environ.get('STRIPE_SECRET_KEY'),
  'publishable_key': os.environ.get('STRIPE_PUBLISHABLE_KEY')
}

stripe.api_key = stripe_keys['secret_key']

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
                        print(cart)
                    else:
                        c = Cart(uid=current_user.id, pid=id, quantity=form.quantity.data)
                        db.session.add(c)
                        db.session.commit()
                        print(c)
                    flash('The product was added to your cart!', 'success')
    return render_template('product_desc.html', title='Product Details', prod=prod, img=img, form=form, seller=seller)

@app.route("/cart")
@login_required
def cart():
    print(current_user.id)
    c = Cart.query.filter_by(uid=current_user.id).all()
    print(c)
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
    global b, body, ship, order, stock, product
    ship = []
    order = []
    stock = []
    product = []
    body = f''''''
    print(b)
    c = Cart.query.filter_by(uid=current_user.id).all()
    o = Order.query.filter_by(uid=current_user.id).all()
    if o == []:
        order_id = current_user.id*10000
    else:
        order_id = o[-1].oid + 1
    if c==[] and b==[]:
        flash('No product has been selected', 'warning')
        return redirect(url_for('home'))
    elif len(b)!=0:
        form = ShippingDetails()
        if form.validate_on_submit():
            p = Product.query.filter_by(pid=b[0][1]).first()
            total = p.cost*b[0][3]
            order.append(Order(oid = order_id, uid=current_user.id, pid=b[0][1], 
                        order_status="Ordered", quantity=b[0][3], total=p.cost*b[0][3]))
            #db.session.add(o)
            #db.session.commit()
            delivery_date=datetime.utcnow()+timedelta(days=4)
            ship.append(Shipping(oid=order_id, delivery_date=delivery_date, contactno=form.contactno.data, 
                                address_line1=form.addr1.data, address_line2=form.addr2.data, address_line3=form.addr3.data, 
                                pincode=form.pincode.data, city=form.city.data, state=form.state.data, country=form.country.data))
            body += f'''Your order was confirmed! Details:
            Product Name:{p.name}
            Order ID: {order_id}
            Expected Delivery Date: {delivery_date}'''
            product.append(p)
            stock.append(int(b[0][3]))#stores the amount that stock should be decreased by
            print('before redirect')
            session['url'] = url_for('checkout')
            return redirect(url_for('pay', amount=total))
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
        form = ShippingDetails()
        cost=[]
        totalcost = 0
        if form.validate_on_submit():
            body = f'''Your order was confirmed! Details:
            '''
            for i in range(len(c)):
                l=[]
                prod = Product.query.filter_by(pid=c[i].pid).first()
                cost.append(prod.cost * c[i].quantity)
                order.append(Order(oid=order_id, uid=current_user.id, pid=c[i].pid, order_status="Ordered", 
                                    quantity=c[i].quantity, total=cost[i]))
                delivery_date=datetime.utcnow()+timedelta(days=4)
                ship.append(Shipping(oid=order_id, delivery_date=delivery_date, contactno=form.contactno.data, 
                                    address_line1=form.addr1.data, address_line2=form.addr2.data, address_line3=form.addr3.data, 
                                    pincode=form.pincode.data, city=form.city.data, state=form.state.data, country=form.country.data))
                product.append(prod)
                stock.append(c[i].quantity)#stores the amount that stock should be decreased by
                l.extend([user.name, prod.pid, prod.name, c[i].quantity, cost[i]])
                b.append(l)
                totalcost += cost[i]
                body+=f'''Product name: {prod.name}
                Order ID: {order_id}
                Expected Delivery Date: {delivery_date}
                
                '''
                order_id += 1
            session['url'] = url_for('checkout')
            return redirect(url_for('pay', amount=totalcost))
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
    
@app.route('/pay<int:amount>', methods=['GET', 'POST'])
@login_required 
def pay(amount):
    print(session['url'])
    if 'url' in session and session['url'] == url_for('checkout'):
        session['url'] = url_for('pay', amount=amount)
        print(session['url'])
        amount = amount*100
        return render_template('pay.html', title='Payment Screen', amount=amount, 
                            key=stripe_keys['publishable_key'])
    else:
        flash('Shipping details not entered', 'danger')
        return redirect(url_for('home'))

@app.route('/invoice<int:amount>', methods=['POST'])
@login_required 
def invoice(amount):
    global b, body, ship, order, product, stock
    print(b)
    b1 = b
    print(b1)
    b = []
    customer = stripe.Customer.create(
        email=current_user.email,
        source=request.form['stripeToken'],
        name=current_user.name,
        address={
            'line1': current_user.address_line1,
            'postal_code': current_user.pincode,
            'city': current_user.city,
            'state': current_user.state,
            'country': current_user.country,
        },
    )
    stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='inr',
        description='Flask Charge'
    )
    for i in range(len(order)):
        db.session.add(order[i])
        db.session.commit()
    for i in range(len(ship)):
        db.session.add(ship[i])
        db.session.commit()
        product[i].stock -= stock[i]
        db.session.commit()
    if(len(order) > 1):
        Cart.query.filter_by(uid=current_user.id).delete()
        db.session.commit()
    msg = Message('Order Confirmation', sender='noreply@demo.com', recipients=[current_user.email])
    msg.body = body
    mail.send(msg)
    flash('Your order was processed successfully! An email was sent confirming your order', 'success')
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
    return render_template('orders.html', title='Your Orders', order=order, l=len(order), pname=pname, txn=txn)


@app.route("/shipping<int:id>")
@login_required     
def shipping(id):
    ship = Shipping.query.filter_by(oid=id).first_or_404()
    order = Order.query.filter_by(oid=id).first_or_404()
    if order.uid != current_user.id:
        flash('You do not have the authority to visit this page', 'warning')
        return redirect(url_for('home'))
    return render_template('ship.html',title='Shipping Details', ship=ship)


            