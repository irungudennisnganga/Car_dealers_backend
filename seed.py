from config import app, db, bcrypt
from models import User, Inventory, Importation, Customer, Sale, Invoice, Report, Notification, Receipt

def seed_data():
    with app.app_context():
        # Delete all existing records
        db.session.query(User).delete()
        db.session.query(Inventory).delete()
        db.session.query(Importation).delete()
        db.session.query(Customer).delete()
        db.session.query(Sale).delete()
        db.session.query(Invoice).delete()
        db.session.query(Report).delete()
        db.session.query(Notification).delete()
        db.session.query(Receipt).delete()
        db.session.commit()

        # Add users
        password_hash = bcrypt.generate_password_hash('mypassword').decode('utf-8')
        password_hash2 = bcrypt.generate_password_hash('password').decode('utf-8')

        user1 = User(first_name='Dennis', last_name='Irungu', email='irungud220@gmail.com', image='avatar.jpg', role='admin', contact=1234567890,_password_hash=password_hash)
        user3 = User(first_name='dennis', last_name='irungu', email='dennisnganga7148@gmail.com', image='avatar.jpg', role='super admin', contact=345678765, _password_hash=password_hash2)

        user2 = User(first_name='Jane', last_name='Smith', email='jane@example.com', image='avatar.jpg', role='seller', contact=9876543210, _password_hash=password_hash2)
        db.session.add(user1)
        db.session.add(user3)
        db.session.add(user2)

        # Add inventories
        inventory1 = Inventory(make='Toyota', image='car.jpg', price=15000, currency='USD', model='SUV', year='2022', VIN=12345678901234567, color='Black', mileage=5000, body_style='SUV', transmission='Automatic', fuel_type='Gasoline', engine_size='3.5L', drive_type='AWD', trim_level='XLE', condition='New', availability='Available', cylinder=6, doors=4, stock_number=1001, purchase_cost=12000, profit=3000, user_id=1)
        inventory2 = Inventory(make='Honda', image='car.jpg', price=20000, currency='USD', model='Sedan', year='2021', VIN=98765432109876543, color='White', mileage=10000, body_style='Sedan', transmission='Automatic', fuel_type='Gasoline', engine_size='2.0L', drive_type='FWD', trim_level='Touring', condition='Used', availability='Available', cylinder=4, doors=4, stock_number=1002, purchase_cost=15000, profit=5000, user_id=1)
        db.session.add(inventory1)
        db.session.add(inventory2)

        # Add importations
        importation1 = Importation(country_of_origin='Japan', transport_fee=1000, currency='USD', import_duty=500, import_date='2023-01-01', import_document='import_doc.pdf', car_id=1)
        importation2 = Importation(country_of_origin='USA', transport_fee=800, currency='USD', import_duty=400, import_date='2023-02-01', import_document='import_doc.pdf', car_id=2)
        db.session.add(importation1)
        db.session.add(importation2)

        # Add customers
        customer1 = Customer(first_name='Alice', last_name='Johnson', email='alice@example.com', address='123 Main St', phone_number=1234567890, image='avatar.jpg')
        customer2 = Customer(first_name='Bob', last_name='Smith', email='bob@example.com', address='456 Oak St', phone_number=9876543210, image='avatar.jpg')
        db.session.add(customer1)
        db.session.add(customer2)

        # Add sales
        sale1 = Sale(commision=500, status='completed', history='No issues', discount=1000, sale_date='2023-03-01', customer_id=1, seller_id=1, inventory_id=1, promotions='Discount on next purchase')
        sale2 = Sale(commision=700, status='completed', history='Minor scratches', discount=1500, sale_date='2023-04-01', customer_id=2, seller_id=2, inventory_id=2, promotions='Extended warranty')
        db.session.add(sale1)
        db.session.add(sale2)

        # Add invoices
        invoice1 = Invoice(date_of_purchase='2023-03-01', method='credit card', amount_paid=14000, fee=500, tax=1000, currency='USD', seller_id=1, sale_id=1, balance=1000, total_amount=15000, installments=1, pending_cleared='no', customer_id=1, vehicle_id=1, signature='signature.jpg', warranty='1 year', terms_and_conditions='Terms', agreement_details='Details', additional_accessories='Accessories', notes_instructions='Instructions', payment_proof='proof.jpg')
        invoice2 = Invoice(date_of_purchase='2023-04-01', method='cash', amount_paid=18500, fee=700, tax=1500, currency='USD', seller_id=2, sale_id=2, balance=500, total_amount=20000, installments=1, pending_cleared='no', customer_id=2, vehicle_id=2, signature='signature.jpg', warranty='2 years', terms_and_conditions='Terms', agreement_details='Details', additional_accessories='Accessories', notes_instructions='Instructions', payment_proof='proof.jpg')
        db.session.add(invoice1)
        db.session.add(invoice2)

        # Add reports
        report1 = Report(company_profit=3000, sale_id=1, expenses=500, inventory_id=1, sale_date='2023-03-01', customer_id=1, seller_id=1, importation_id=1)
        report2 = Report(company_profit=5000, sale_id=2, expenses=700, inventory_id=2, sale_date='2023-04-01', customer_id=2, seller_id=2, importation_id=2)
        db.session.add(report1)
        db.session.add(report2)

        # Add notifications
        notification1 = Notification(user_id=1, customer_id=1, message='Notification 1', notification_type='email')
        notification2 = Notification(user_id=2, customer_id=2, message='Notification 2', notification_type='sms')
        db.session.add(notification1)
        db.session.add(notification2)

        # Add receipts
        receipt1 = Receipt(user_id=1, customer_id=1, invoice_id=1, amount_paid=14000, commission=500)
        receipt2 = Receipt(user_id=2, customer_id=2, invoice_id=2, amount_paid=18500, commission=700)
        db.session.add(receipt1)
        db.session.add(receipt2)

        db.session.commit()

if __name__ == '__main__':
    seed_data()
