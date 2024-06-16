from config import app, db, bcrypt
from models import User, Inventory, Importation, Customer, Sale, Invoice, Report, Notification, Receipt, GalleryImage


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
        db.session.query(GalleryImage).delete()
        db.session.commit()

        # Add specific users
        password_hash = bcrypt.generate_password_hash('mypassword').decode('utf-8')
        password_hash2 = bcrypt.generate_password_hash('password').decode('utf-8')

        users = [

            User(first_name='Dennis', last_name='Irungu', status="active", email='irungud220@gmail.com', image='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcScNc6oZl7o7MuTWxfNXnWIiqzzCRmQg8sjBp59ZBZpFg&s', role='super admin', contact=1234567890, _password_hash=password_hash),
            User(first_name='Maurine', last_name='Wambui', status="active", email='maurinewambui@gmail.com', image='https://imgv3.fotor.com/images/blog-cover-image/a-pink-barbie-doll-with-a-pink-background.jpg', role='admin', contact=9876543210, _password_hash=password_hash2),
            User(first_name='Stanley', last_name='Muiruri', status="active", email='stanleywanjau@gmail.com', image='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcScNc6oZl7o7MuTWxfNXnWIiqzzCRmQg8sjBp59ZBZpFg&s', role='admin', contact=9876567, _password_hash=password_hash),
            User(first_name='Beatrice', last_name='Mwangi', status="active", email='bbeatricemwangi@gmail.com', image='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS2bPWPwj6jFqpAFm7q02z4hQ2Uwt4vYEueQzkzpq7dfg&s', role='seller', contact=2345098, _password_hash=password_hash2),
            User(first_name='Samuel', last_name='Mwangi', status="active", email='samwelmwangi@gmail.com', image='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcScNc6oZl7o7MuTWxfNXnWIiqzzCRmQg8sjBp59ZBZpFg&s', role='seller', contact=98765678, _password_hash=password_hash),
            User(first_name='James', last_name='Kinyanjui', status="active", email='jameskinyanjui@gmail.com', image='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS2bPWPwj6jFqpAFm7q02z4hQ2Uwt4vYEueQzkzpq7dfg&s', role='seller', contact=987678, _password_hash=password_hash2),

        ]

        db.session.bulk_save_objects(users)
        db.session.commit()


        # Add inventories
        inventories = [
            Inventory(make='Toyota', image='https://images.pexels.com/photos/3311574/pexels-photo-3311574.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1', price=15000, currency='USD', model='SUV', year='2022', VIN='12345678901234567', color='Black', mileage=5000, body_style='SUV', transmission='Automatic', fuel_type='Gasoline', engine_size='3.5L', drive_type='AWD', trim_level='XLE', condition='New', availability='Available', cylinder=6, doors=4, stock_number=1001, purchase_cost=12000, profit=3000, user_id=1),
            Inventory(make='Honda', image='https://images.pexels.com/photos/712618/pexels-photo-712618.jpeg?auto=compress&cs=tinysrgb&w=600', price=20000, currency='USD', model='Sedan', year='2021', VIN='98765432109876543', color='White', mileage=10000, body_style='Sedan', transmission='Automatic', fuel_type='Gasoline', engine_size='2.0L', drive_type='FWD', trim_level='Touring', condition='Used', availability='Available', cylinder=4, doors=4, stock_number=1002, purchase_cost=15000, profit=5000, user_id=2),
            Inventory(make='Mercedes Benz', image='https://images.pexels.com/photos/3786091/pexels-photo-3786091.jpeg?auto=compress&cs=tinysrgb&w=600', price=25000, currency='USD', model='SUV', year='2022', VIN='98767898', color='Black', mileage=5000, body_style='SUV', transmission='Automatic', fuel_type='Gasoline', engine_size='3.5L', drive_type='AWD', trim_level='XLE', condition='New', availability='Pending', cylinder=6, doors=4, stock_number=1001, purchase_cost=20000, profit=5000, user_id=3),
            Inventory(make='BMW', image='https://images.pexels.com/photos/2676096/pexels-photo-2676096.jpeg?auto=compress&cs=tinysrgb&w=600', price=2700, currency='KSH', model='Sedan', year='2021', VIN='23456789', color='White', mileage=10000, body_style='Sedan', transmission='Automatic', fuel_type='Gasoline', engine_size='2.0L', drive_type='FWD', trim_level='Touring', condition='Used', availability='Available', cylinder=4, doors=4, stock_number=1002, purchase_cost=2000, profit=700, user_id=2),
        ]

        db.session.bulk_save_objects(inventories)
        db.session.commit()

        # Add importations
        importations = [
            Importation(country_of_origin='Japan', transport_fee=1500, currency='USD', import_duty=3000, expense=500, car_id=1),
            Importation(country_of_origin='Germany', transport_fee=2000, currency='USD', import_duty=4000, expense=700, car_id=2),
            Importation(country_of_origin='USA', transport_fee=2500, currency='USD', import_duty=5000, expense=800, car_id=3),
            Importation(country_of_origin='UK', transport_fee=1000, currency='USD', import_duty=2000, expense=300, car_id=4),
        ]

        db.session.bulk_save_objects(importations)
        db.session.commit()

        # Add customers
        customers = [
            Customer(first_name='John', last_name='Doe', email='john.doe@example.com', phone_number='555-1234', address='123 Elm Street', image='https://example.com/image.jpg', seller_id=4),
            Customer(first_name='Jane', last_name='Smith', email='jane.smith@example.com', phone_number='555-5678', address='456 Oak Avenue', image='https://example.com/image.jpg', seller_id=5),
            Customer(first_name='Alice', last_name='Johnson', email='alice.johnson@example.com', phone_number='555-8765', address='789 Pine Road', image='https://example.com/image.jpg', seller_id=6),
            Customer(first_name='Bob', last_name='Brown', email='bob.brown@example.com', phone_number='555-4321', address='321 Birch Lane', image='https://example.com/image.jpg', seller_id=4),
        ]

        db.session.bulk_save_objects(customers)
        db.session.commit()

        # Add sales
        sales = [
            Sale(inventory_id=1, customer_id=1, sale_date='2023-01-01', seller_id=4, status='Completed', history='First sale', discount=0, promotions='None', commision=3000),
            Sale(inventory_id=2, customer_id=2, sale_date='2023-02-01', seller_id=5, status='Pending', history='Second sale', discount=500, promotions='Holiday Sale', commision=5000),
            Sale(inventory_id=3, customer_id=3, sale_date='2023-03-01', seller_id=6, status='Refunded', history='Third sale', discount=200, promotions='Spring Sale', commision=5000),
            Sale(inventory_id=4, customer_id=4, sale_date='2023-04-01', seller_id=4, status='Completed', history='Fourth sale', discount=100, promotions='Clearance Sale', commision=700),
        ]

        db.session.bulk_save_objects(sales)
        db.session.commit()

        # Add invoices
        invoices = [
            Invoice(date_of_purchase='2023-01-02', method='Credit Card', amount_paid=15000, fee=100, tax=100, currency='USD', seller_id=4, sale_id=1, balance=0, total_amount=15000, installments=1, pending_cleared='Cleared', customer_id=1, vehicle_id=1, signature='John Doe', warranty='3 years', terms_and_conditions='Standard terms', agreement_details='Standard agreement', additional_accessories='None', notes_instructions='Handle with care', payment_proof='proof1.jpg'),
            Invoice(date_of_purchase='2023-02-02', method='Cash', amount_paid=20000, fee=150, tax=150, currency='USD', seller_id=5, sale_id=2, balance=0, total_amount=20000, installments=1, pending_cleared='Cleared', customer_id=2, vehicle_id=2, signature='Jane Smith', warranty='2 years', terms_and_conditions='Standard terms', agreement_details='Standard agreement', additional_accessories='None', notes_instructions='Handle with care', payment_proof='proof2.jpg'),
            Invoice(date_of_purchase='2023-03-02', method='Bank Transfer', amount_paid=25000, fee=200, tax=200, currency='USD', seller_id=6, sale_id=3, balance=0, total_amount=25000, installments=1, pending_cleared='Cleared', customer_id=3, vehicle_id=3, signature='Alice Johnson', warranty='5 years', terms_and_conditions='Standard terms', agreement_details='Standard agreement', additional_accessories='None', notes_instructions='Handle with care', payment_proof='proof3.jpg'),
            Invoice(date_of_purchase='2023-04-02', method='Credit Card', amount_paid=2700, fee=50, tax=50, currency='KSH', seller_id=4, sale_id=4, balance=0, total_amount=2700, installments=1, pending_cleared='Cleared', customer_id=4, vehicle_id=4, signature='Bob Brown', warranty='1 year', terms_and_conditions='Standard terms', agreement_details='Standard agreement', additional_accessories='None', notes_instructions='Handle with care', payment_proof='proof4.jpg'),
        ]

        db.session.bulk_save_objects(invoices)
        db.session.commit()

        # Add reports
        reports = [
            Report(company_profit=3000, sale_id=1, inventory_id=1, customer_id=1, seller_id=4, importation_id=1),
            Report(company_profit=5000, sale_id=2, inventory_id=2, customer_id=2, seller_id=5, importation_id=2),
            Report(company_profit=5000, sale_id=3, inventory_id=3, customer_id=3, seller_id=6, importation_id=3),
            Report(company_profit=700, sale_id=4, inventory_id=4, customer_id=4, seller_id=4, importation_id=4),
        ]

        db.session.bulk_save_objects(reports)
        db.session.commit()

        # Add notifications
        notifications = [
            Notification(user_id=1, message='New sale completed!', notification_type='Sale'),
            Notification(user_id=2, message='Inventory updated!', notification_type='Inventory'),
            Notification(user_id=3, message='New customer added!', notification_type='Customer'),
            Notification(user_id=4, message='Sale pending approval', notification_type='Sale'),
            Notification(user_id=5, message='New invoice generated!', notification_type='Invoice'),
            Notification(user_id=6, message='Report available', notification_type='Report'),
        ]

        db.session.bulk_save_objects(notifications)
        db.session.commit()

        # Add receipts
        receipts = [
            Receipt(user_id=4, customer_id=1, invoice_id=1, amount_paid=15000),
            Receipt(user_id=5, customer_id=2, invoice_id=2, amount_paid=20000),
            Receipt(user_id=6, customer_id=3, invoice_id=3, amount_paid=25000),
            Receipt(user_id=4, customer_id=4, invoice_id=4, amount_paid=2700),
        ]

        


        db.session.bulk_save_objects(receipts)
        db.session.commit()

        # Add gallery images
        gallery_images = [
            GalleryImage(url='https://images.pexels.com/photos/3311574/pexels-photo-3311574.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1', inventory_id=1),
            GalleryImage(url='https://images.pexels.com/photos/3311574/pexels-photo-3311574.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1', inventory_id=1),
            GalleryImage(url='https://images.pexels.com/photos/3311574/pexels-photo-3311574.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1', inventory_id=1),
            GalleryImage(url='https://images.pexels.com/photos/712618/pexels-photo-712618.jpeg?auto=compress&cs=tinysrgb&w=600', inventory_id=2),
            GalleryImage(url='https://images.pexels.com/photos/712618/pexels-photo-712618.jpeg?auto=compress&cs=tinysrgb&w=600', inventory_id=2),
            GalleryImage(url='https://images.pexels.com/photos/712618/pexels-photo-712618.jpeg?auto=compress&cs=tinysrgb&w=600', inventory_id=2),
            GalleryImage(url='https://images.pexels.com/photos/3786091/pexels-photo-3786091.jpeg?auto=compress&cs=tinysrgb&w=600', inventory_id=3),
            GalleryImage(url='https://images.pexels.com/photos/3786091/pexels-photo-3786091.jpeg?auto=compress&cs=tinysrgb&w=600', inventory_id=3),
            GalleryImage(url='https://images.pexels.com/photos/3786091/pexels-photo-3786091.jpeg?auto=compress&cs=tinysrgb&w=600', inventory_id=3),
            GalleryImage(url='https://images.pexels.com/photos/2676096/pexels-photo-2676096.jpeg?auto=compress&cs=tinysrgb&w=600', inventory_id=4),
            GalleryImage(url='https://images.pexels.com/photos/2676096/pexels-photo-2676096.jpeg?auto=compress&cs=tinysrgb&w=600', inventory_id=4),
            GalleryImage(url='https://images.pexels.com/photos/2676096/pexels-photo-2676096.jpeg?auto=compress&cs=tinysrgb&w=600', inventory_id=4),
            GalleryImage(url='https://images.pexels.com/photos/2676096/pexels-photo-2676096.jpeg?auto=compress&cs=tinysrgb&w=600', inventory_id=4),
        ]

        db.session.bulk_save_objects(gallery_images)
        db.session.commit()

     

if __name__ == '__main__':
    seed_data()
