from config import app, db, bcrypt
from models import User, Inventory, Importation, Customer, Sale, Invoice, Report, Notification, Receipt, GalleryImage
from faker import Faker
import random

fake = Faker()

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

        # Generate additional users using Faker
        for _ in range(10):
            password_hash = bcrypt.generate_password_hash(fake.password()).decode('utf-8')
            user = User(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                status="active",
                email=fake.email(),
                image=fake.image_url(),
                role=fake.random_element(elements=('admin', 'seller')),
                contact=fake.phone_number(),
                _password_hash=password_hash
            )
            db.session.add(user)

        db.session.commit()

        # Add inventories
        inventories = [
            Inventory(make='Toyota', image='https://images.pexels.com/photos/3311574/pexels-photo-3311574.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1', price=15000, currency='USD', model='SUV', year='2022', VIN=12345678901234567, color='Black', mileage=5000, body_style='SUV', transmission='Automatic', fuel_type='Gasoline', engine_size='3.5L', drive_type='AWD', trim_level='XLE', condition='New', availability='Available', cylinder=6, doors=4, stock_number=1001, purchase_cost=12000, profit=3000, user_id=1),
            Inventory(make='Honda', image='https://images.pexels.com/photos/712618/pexels-photo-712618.jpeg?auto=compress&cs=tinysrgb&w=600', price=20000, currency='USD', model='Sedan', year='2021', VIN=98765432109876543, color='White', mileage=10000, body_style='Sedan', transmission='Automatic', fuel_type='Gasoline', engine_size='2.0L', drive_type='FWD', trim_level='Touring', condition='Used', availability='Available', cylinder=4, doors=4, stock_number=1002, purchase_cost=15000, profit=5000, user_id=2),
            Inventory(make='Mercedes Benz', image='https://images.pexels.com/photos/3786091/pexels-photo-3786091.jpeg?auto=compress&cs=tinysrgb&w=600', price=25000, currency='USD', model='SUV', year='2022', VIN=98767898, color='Black', mileage=5000, body_style='SUV', transmission='Automatic', fuel_type='Gasoline', engine_size='3.5L', drive_type='AWD', trim_level='XLE', condition='New', availability='Pending', cylinder=6, doors=4, stock_number=1001, purchase_cost=12000, profit=3000, user_id=3),
            Inventory(make='BMW', image='https://images.pexels.com/photos/2676096/pexels-photo-2676096.jpeg?auto=compress&cs=tinysrgb&w=600', price=2700, currency='KSH', model='Sedan', year='2021', VIN=23456789, color='White', mileage=10000, body_style='Sedan', transmission='Automatic', fuel_type='Gasoline', engine_size='2.0L', drive_type='FWD', trim_level='Touring', condition='Used', availability='Available', cylinder=4, doors=4, stock_number=1002, purchase_cost=15000, profit=5000, user_id=2),
        ]

        db.session.bulk_save_objects(inventories)

        # Generate additional inventories using Faker
        for _ in range(20):
            inventory = Inventory(
                make=fake.company(),
                image=fake.image_url(),
                price=fake.random_int(min=5000, max=50000),
                currency=fake.random_element(elements=('USD', 'KSH')),
                model=fake.word(),
                year=fake.year(),
                VIN=fake.random_int(min=10000000000000000, max=99999999999999999),
                color=fake.color_name(),
                mileage=fake.random_int(min=0, max=200000),
                body_style=fake.random_element(elements=('SUV', 'Sedan', 'Hatchback', 'Convertible')),
                transmission=fake.random_element(elements=('Automatic', 'Manual')),
                fuel_type=fake.random_element(elements=('Gasoline', 'Diesel', 'Electric', 'Hybrid')),
                engine_size=fake.random_element(elements=['1.5L', '2.0L', '2.5L', '3.0L', '3.5L']),
                drive_type=fake.random_element(elements=('FWD', 'RWD', 'AWD')),
                trim_level=fake.word(),
                condition=fake.random_element(elements=('New', 'Used')),
                availability=fake.random_element(elements=('Available', 'Pending', 'Sold')),
                cylinder=fake.random_int(min=3, max=12),
                doors=fake.random_int(min=2, max=5),
                stock_number=fake.random_int(min=1000, max=9999),
                purchase_cost=fake.random_int(min=5000, max=45000),
                profit=fake.random_int(min=500, max=10000),
                user_id=fake.random_int(min=1, max=8)
            )
            db.session.add(inventory)

        db.session.commit()

        # Generate data for other models using Faker

        for _ in range(20):
            importation = Importation(
                country_of_origin=fake.country(),
                transport_fee=fake.random_int(min=500, max=5000),
                currency=fake.random_element(elements=('USD', 'KSH')),
                import_duty=fake.random_int(min=1000, max=10000),
                import_date=fake.date_this_decade(),
                import_document='file.jpg',
                car_id=fake.random_int(min=1, max=10)
            )
            db.session.add(importation)

        db.session.commit()

        # Fetch seller IDs
        seller_ids = [user.id for user in User.query.filter_by(role='seller').all()]

        for _ in range(20):
            customer = Customer(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone_number=fake.phone_number(),
                address=fake.address(),
                
                image=fake.image_url(),
                seller_id=random.choice(seller_ids)
            )
            db.session.add(customer)

        db.session.commit()
        
        seller_ids = [user.id for user in User.query.filter_by(role='seller').all()]

        for _ in range(30):
            inventory_id = fake.random_int(min=1, max=10)
            inventory = Inventory.query.filter_by(id=inventory_id).first()
            if inventory:
                commision = inventory.price * 0.20
                sale = Sale(
                    inventory_id=inventory_id,
                    customer_id=fake.random_int(min=1, max=10),
                    sale_date=fake.date_this_year(),
                    seller_id=random.choice(seller_ids),  # Select a random seller ID
                    status=fake.random_element(elements=('Pending', 'Completed', 'Refunded')),
                    history=fake.text(max_nb_chars=200),
                    discount=fake.random_int(min=0, max=500),
                    promotions=fake.text(max_nb_chars=200),
                    commision=commision
                )
                db.session.add(sale)

        db.session.commit()



        for _ in range(30):
            invoice = Invoice(
                date_of_purchase=fake.date_this_year(),
                method=fake.random_element(elements=('Credit Card', 'Cash', 'Bank Transfer')),
                amount_paid=fake.random_int(min=5000, max=50000),
                fee=fake.random_int(min=100, max=1000),
                tax=fake.random_int(min=100, max=1000),
                currency=fake.random_element(elements=('USD', 'KSH')),
                seller_id=fake.random_int(min=1, max=8),
                sale_id=fake.random_int(min=1, max=10),
                balance=fake.random_int(min=1000, max=10000),
                total_amount=fake.random_int(min=10000, max=100000),
                installments=fake.random_int(min=1, max=12),
                pending_cleared=fake.random_element(elements=('Pending', 'Cleared')),
                customer_id=fake.random_int(min=1, max=10),
                vehicle_id=fake.random_int(min=1, max=10),
                signature=fake.text(max_nb_chars=50),
                warranty=fake.text(max_nb_chars=100),
                terms_and_conditions=fake.text(max_nb_chars=200),
                agreement_details=fake.text(max_nb_chars=200),
                additional_accessories=fake.text(max_nb_chars=200),
                notes_instructions=fake.text(max_nb_chars=200),
                payment_proof='proof.jpg',
            )
            db.session.add(invoice)

        db.session.commit()


        seller_ids = [user.id for user in User.query.filter_by(role='seller').all()]

        for _ in range(30):
            report = Report(
                company_profit=fake.random_int(min=1000, max=10000),
                sale_id=fake.random_int(min=1, max=10),
                expenses=fake.random_int(min=500, max=5000),
                inventory_id=fake.random_int(min=1, max=10),
                sale_date=fake.date_this_year(),
                customer_id=fake.random_int(min=1, max=10),
                seller_id=random.choice(seller_ids),  # Select a random seller ID
                importation_id=fake.random_int(min=1, max=10)
            )
            db.session.add(report)

        db.session.commit()


        for _ in range(10):
            notification = Notification(
                user_id=fake.random_int(min=1, max=8),
                customer_id=fake.random_int(min=1, max=10),
                message=fake.sentence(),
                notification_type=fake.random_element(elements=('Type1', 'Type2', 'Type3'))  # Adjust notification types as needed
            )
            db.session.add(notification)

        db.session.commit()

        for _ in range(10):
            receipt = Receipt(
                user_id=fake.random_int(min=1, max=8),
                customer_id=fake.random_int(min=1, max=10),
                invoice_id=fake.random_int(min=1, max=10),
                amount_paid=fake.random_int(min=5000, max=50000)
            )
            db.session.add(receipt)

        db.session.commit()


        for _ in range(10):
            gallery_image = GalleryImage(
                url=fake.image_url(),
                inventory_id=fake.random_int(min=1, max=10)
            )
            db.session.add(gallery_image)

        db.session.commit()


if __name__ == '__main__':
    seed_data()
