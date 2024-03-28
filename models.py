from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from config import db
from sqlalchemy import UniqueConstraint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from config import db,bcrypt


class User(db.Model):
    __tablename__ ='user'

    id = db.Column(db.Integer, primary_key=True)
    first_name =db.Column(db.String)
    last_name =db.Column(db.String)
    email =db.Column(db.String)
    image =db.Column(db.String)
    role =db.Column(db.String)
    contact =db.Column(db.Integer)
    _password_hash =db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    
    inventory =db.relationship("Inventory", backref='user')
    sale =db.relationship("Sale", backref='user')
    invoice =db.relationship("Invoice", backref='user')
    report =db.relationship("Report", backref='user')
    notifications =db.relationship("Notification", backref='user')
    receipt =db.relationship("Receipt", backref='user')
    
class Inventory(db.Model):
    __tablename__ ='inventories'   

    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String, nullable=False)
    model = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)
    VIN = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)
    body_style = db.Column(db.String, nullable=False)
    transmission = db.Column(db.String, nullable=False)
    fuel_type = db.Column(db.String, nullable=False)
    engine_size = db.Column(db.String, nullable=False)
    drive_type = db.Column(db.String, nullable=False)
    trim_level = db.Column(db.String, nullable=False)
    gallery = db.Column(db.String)
    condition = db.Column(db.String, nullable=False)
    availability = db.Column(db.String, nullable=False)
    cylinder = db.Column(db.Integer)
    doors = db.Column(db.Integer, nullable=False)
    features = db.Column(db.String)
    stock_number = db.Column(db.Integer, nullable=False)
    purchase_cost = db.Column(db.Integer, nullable=False)
    profit = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    
    importation = db.relationship("Importation", backref='inventories')
    sale =db.relationship("sale", backref='inventories')
    invoice =db.relationship("Invoice", backref='inventories')
    report =db.relationship("Report", backref='inventories')
    

class Importation(db.Model):
    __tablename__ ='importations'

    id = db.Column(db.Integer,primary_key=True, nullable=False)
    country_of_origin = db.Column(db.String, nullable=False)
    transport_fee = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String, nullable=False)
    import_duty = db.Column(db.Integer, nullable=False)
    import_date = db.Column(db.String, nullable=False)
    import_document = db.Column(db.String, nullable=False)
    car_id = db.Column(db.Integer,db.ForeignKey("inventories.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

class Customer(db.Model):
    __tablename__ ='customers'    

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    
    sale= db.relationship("Sale",backref='customers')
    invoice =db.relationship("Invoice", backref='customers')
    report =db.relationship("Report", backref='customers')
    notification =db.relationship("Notification", backref='customers')
    receipt =db.relationship("Receipt", backref='customers')

class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    commision = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)
    history = db.Column(db.String, nullable=False)
    discount = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.String, nullable=False)
    customer_id = db.Column(db.Integer,db.ForeignKey("customers.id"), nullable=False)
    seller_id = db.Column(db.String,db.ForeignKey("user.id"), nullable=False)
    inventory_id = db.Column(db.String,db.ForeignKey("inventories.id"), nullable=False)
    promotions = db.Column(db.String, nullable=False)
    
    invoice =db.relationship("Invoice", backref='sales')
    
class Invoice(db.Model):
    __tablename__ ='invoices'

    id = db.Column(db.Integer, primary_key=True)
    date_of_purchase = db.Column(db.String, nullable=False)
    method = db.Column(db.String, nullable=False)
    amount_paid = db.Column(db.Integer, nullable=False)
    fee = db.Column(db.Integer, nullable=False)
    tax = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"), nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    installments = db.Column(db.Integer, nullable=False)
    pending_cleard = db.Column(db.String, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("inventories.id"), nullable=False)
    signature = db.Column(db.String, nullable=False)
    warranty = db.Column(db.String, nullable=False)
    terms_and_conditions = db.Column(db.String, nullable=False)
    agreemnet_details = db.Column(db.String, nullable=False)
    additional_accessories = db.Column(db.String, nullable=False)
    notes_instructions = db.Column(db.String, nullable=False)
    payment_proof = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())


class Report(db.Model):
    __tablename__ ='reports'
    
    id = db.Column(db.Integer, primary_key=True)
    company_profit = db.Column(db.Integer, nullable=False)
    sale_id = db.Column(db.Integer, nullable=False)
    expenses = db.Column(db.Integer, nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey("inventories.id"), nullable=False)
    sale_date = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    importation_id = db.Column(db.Integer, nullable=False)


class Notificaton(db.Model):
    __tablename__ ='notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    message = db.Column(db.String, nullable=False)
    notification_type = db.Column(db.String, nullable=False)
    

class Receipt(db.Model):
    __tablename__ ='receipts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    invoice_id = db.Column(db.Integer, nullable=False)
    amount_paid = db.Column(db.Integer, nullable=False)
    commision = db.Column(db.Integer, nullable=False)
    time_stamp =db.Column(db.DateTime, server_default=db.func.now())

