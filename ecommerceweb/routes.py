from flask import render_template, url_for, flash, redirect, request
from ecommerceweb import app, db, bcrypt
from ecommerceweb.forms import RegistrationForm, LoginForm, UpdateAccountForm, QuantityForm, PaymentDetails
from ecommerceweb.dbmodel import User, Product, Category, Cart, UserTransac, Order
from flask_login import login_user, current_user, logout_user, login_required
import base64

b=[]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

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
    global b
    b=[]
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
    else:
        c=5
        title="Jewellery"
    prod=Product.query.filter_by(category_id=c).all()
    img=[]
    for p in prod:
        img.append(base64.b64encode(p.image_file1).decode('ascii'))
    return render_template('category.html', prod=prod, img=img, l=len(prod), title=title)

@app.route("/product<int:id>", methods=['GET', 'POST'])
def product(id):
    global b
    prod=Product.query.filter_by(pid=id).first_or_404("This product does not exist")
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
        if form.buy.data:
            if(form.quantity.data > prod.stock):
                s='Requested quantity exceeds stock. Only {stock} pieces available'.format(stock=prod.stock)
                flash(s, 'danger')
            else:
                l=[]
                b=[]
                user = User.query.filter_by(id=current_user.id).first()
                l.extend([user.name, id, prod.name, form.quantity.data, prod.cost*form.quantity.data])
                b.append(l)
                return redirect(url_for('payment'))
        elif form.add.data:
            if(form.quantity.data > prod.stock):
                s='Requested quantity exceeds stock. Only {stock} pieces available'.format(stock=prod.stock)
                flash(s, 'danger')
            else:
                c = Cart(uid=current_user.id, pid=id, quantity=form.quantity.data)
                db.session.add(c)
                db.session.commit()
                flash('The product was added to your cart!', 'success')
    return render_template('product_desc.html', title='Product Details', prod=prod, img=img, form=form)

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

@app.route("/payment", methods=['GET', 'POST'])
@login_required 
def payment():
    global b
    c = Cart.query.filter_by(uid=current_user.id).all()
    print(c)
    if c==[] and b==[]:
        flash('No product has been selected', 'warning')
        return redirect(url_for('home'))
    elif c==[]:
        form = PaymentDetails()
        if form.validate_on_submit():
            o = Order(uid=current_user.id, pid=b[0][1], order_status="Ordered")
            db.session.add(o)
            db.session.commit()
            u = UserTransac(uid=current_user.id, oid=o.oid, upiid=form.upiid.data)
            db.session.add(u)
            db.session.commit()
            flash('Your order was processed successfully!', 'success')
            p = Product.query.filter_by(pid=b[0][1]).first()
            p.stock-=int(b[0][3])
            db.session.commit()
            return redirect(url_for('checkout'))
        return render_template('payment.html', title='Payment Details', form=form)
    elif b==[]:
        print('cart has some products')
        user = User.query.filter_by(id=current_user.id).first()
        form = PaymentDetails()
        cost=[]
        if form.validate_on_submit():
            for i in range(len(c)):
                l=[]
                prod = Product.query.filter_by(pid=c[i].pid).first()
                cost.append(prod.cost * c[i].quantity)
                o = Order(uid=current_user.id, pid=c[i].pid, order_status="Ordered")
                db.session.add(o)
                db.session.commit()
                u = UserTransac(uid=current_user.id, oid=o.oid, upiid=form.upiid.data)
                db.session.add(u)
                db.session.commit()
                prod.stock-=c[i].quantity
                db.session.commit()
                l.extend([user.name, prod.pid, prod.name, c[i].quantity, cost[i]])
                b.append(l)
            Cart.query.filter_by(uid=user.id).delete()
            db.session.commit()
            return redirect(url_for('checkout'))
        return render_template('payment.html', title='Payment Details', form=form)

@app.route("/checkout")
@login_required 
def checkout():
    global b
    b1=b
    print(b1)
    b=[]
    return render_template('checkout.html', inv=b1, length=len(b1))