from ecommerceweb import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    contactno=db.Column(db.Numeric(10,0), unique=True, nullable=False)
    s_address=db.Column(db.String(300), nullable=False)
    b_address=db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"

class Seller(db.Model):
    sid=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(75), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Seller('{self.username}', '{self.email}')"

class Category(db.Model):
    cid=db.Column(db.Integer, primary_key=True)
    cname=db.Column(db.String(100), nullable=False)

class Product(db.Model):
    pid=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), unique=True, nullable=False)
    cost=db.Column(db.Integer, nullable=False)
    details=db.Column(db.String(500), nullable=False)
    category_id=db.Column(db.Integer, db.ForeignKey(Category.__table__.c.cid), nullable=False)
    sid=db.Column(db.Integer, db.ForeignKey(Seller.__table__.c.sid), nullable=False)

class Order(db.Model):
    oid=db.Column(db.Integer, primary_key=True)
    uid=db.Column(db.Integer, db.ForeignKey(User.__table__.c.id), nullable=False)
    pid=db.Column(db.Integer, db.ForeignKey(Product.__table__.c.pid), nullable=False)
    order_date=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    order_status=db.Column(db.Integer, nullable=False)

class Invoice(db.Model):
    inv_id=db.Column(db.Integer, primary_key=True)
    oid=db.Column(db.Integer, db.ForeignKey(Order.__table__.c.oid), nullable=False)
    inv_date=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    inv_details=db.Column(db.String(100))

class Shipping(db.Model):
    ship_id=db.Column(db.Integer, primary_key=True)
    oid=db.Column(db.Integer, db.ForeignKey(Order.__table__.c.oid), nullable=False)
    inv_id=db.Column(db.Integer, db.ForeignKey(Invoice.__table__.c.inv_id), nullable=False)
    tracking_no=db.Column(db.Numeric(12,0), unique=True, nullable=False)
    delivery_date=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    details=db.Column(db.String(100))


