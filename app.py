from models import User, Inventory, Importation, Customer, GalleryImage, Sale,Invoice,Receipt
from config import app, api, db, bcrypt
from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import cloudinary
import cloudinary.uploader
import cloudinary.api
from datetime import datetime
from collections import defaultdict
import smtplib

def send_email(email,subject,body):
    
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'irungud220@gmail.com'
    sender_password = 'qbpq uvgp rrqh bjky'
    subject=subject
    body=body

    message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email,email,message)

cloudinary.config(
    cloud_name='dups4sotm',
    api_key='141549863151677',
    api_secret='ml0oq6T67FZeXf6AFJqhhPsDfAs'
)


class CheckSession(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        user = User.query.filter_by(id=user_id).first()

        if not user:
            return {"message": "user not found"}

        user_data = {
            "user_id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_email": user.email,
            "contact": user.contact,
            "role": user.role,
            "image": user.image,
            "status":user.status

        }

        return make_response(jsonify(user_data), 200)


class Login(Resource):

    def post(self):
        
        email = request.json.get("email")
        password = request.json.get("password")

        if not email or not password:
            return make_response(jsonify({"msg": "Bad Email or password"}), 401)

        user = User.query.filter_by(email=email).first()
        if not user:
            return make_response(jsonify({"msg": "Wrong credentials"}), 401)

        if check_password_hash(user._password_hash, password):
            access_token = create_access_token(identity=user.id)
            # remember to uncomment this code
            send_email(email=email,subject='Login Successful', body='You have been logged in your account successfully')
            user.status="active"
            
            db.session.commit()
            
            return make_response(jsonify(access_token=access_token), 200)

        return make_response(jsonify({"message": "Wrong password"}), 406)


class SignupUser(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        check_user_role = User.query.filter_by(id=user_id).first()

        if check_user_role.role not in ['admin', 'super admin']:
            return make_response(jsonify({'message': 'Unauthorized'}), 401)

        data = request.form
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        image_file = request.files.get('image')
        contact = data.get('contact')
        email = data.get('email')
        status = "inactive"
        role = data.get('role') if check_user_role.role == 'super admin' else 'seller'
        password = '8Dn@3pQo'
        # print(image_file)
        
        if not all([first_name, last_name, email, contact, role]) or not image_file:
            return make_response(jsonify({'errors': ['Missing required data']}), 406)

        if User.query.filter_by(email=email).first() or User.query.filter_by(contact=contact).first():
            return make_response(jsonify({'message': 'User already exists'}), 400)

        if image_file.filename == '':
            return {'error': 'No image selected for upload'}, 400

        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

        if not allowed_file(image_file.filename):
            return {'error': 'Invalid file type. Only images are allowed'}, 400

        # Upload image to Cloudinary
        try:
            image_upload_result = cloudinary.uploader.upload(image_file)
        except Exception as e:
            return {'error': f'Error uploading image: {str(e)}'}, 500

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            image=image_upload_result['secure_url'],
            email=email,
            contact=contact,
            status=status,
            role=role,
            _password_hash=bcrypt.generate_password_hash(password).decode('utf-8')
        )
        db.session.add(new_user)
        db.session.commit()
        # Send email here (assuming you have a function defined for this)
        send_email(
    email=email,
    subject='You have been signed up',
    body=f'You have been signed up to our car dealership management system. Use this password to login into your account PASSWORD: {password} EMAIL: {email}'
)


        return make_response(jsonify({'message': 'Sign up successful'}), 200)

class UpdatePassword(Resource):
    def post(self):
        data = request.get_json()

        user_email = data.get('email')
        former_password = data.get('former_password')
        new_password = data.get('new_password')

        if not user_email or not former_password or not new_password:
            return make_response(jsonify({'message': 'Email, former password, and new password are required.'}), 400)

        user = User.query.filter_by(email=user_email).first()

        if user is None:
            return make_response(jsonify({'message': 'User not found'}), 404)

        # Assuming you are using a password hashing library like bcrypt
        # Check if the former password matches
        if not check_password_hash(user.password_hash, former_password):
            return make_response(jsonify({'message': 'Incorrect former password'}), 401)

        # Update the password hash with the new one
        user.password_hash = generate_password_hash(
            new_password).decode('utf-8')

        db.session.commit()
        send_email(email=user_email, subject='Password Updates', body='Password updated successfully')
        return make_response(jsonify({'message': 'Password updated successfully'}), 200)


# in this class we are getting all the users and serializering each user using list comprehension
class AllUsers(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()

        if check_user_role.role == "admin":

            user = [{
                'id': n.id,
                'first_name': n.first_name,
                'last_name': n.last_name,
                'email': n.email,
                'contact': n.contact,
                'status':n.status
            } for n in User.query.filter_by(role='seller').all()]

            return user
        if check_user_role.role == "super admin":

            user = [{
                'id': n.id,
                'first_name': n.first_name,
                'last_name': n.last_name,
                'email': n.email,
                'role': n.role,
                'contact': n.contact,
                'status':n.status
            } for n in User.query.all()]

            return user

        return make_response(jsonify(user), 200)

# in this function we are getting a specific user by their id


class OneUser(Resource):
    @jwt_required()
    def get(self, id):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        
        if check_user_role.role == "admin" and check_user_role.status == "active"  or  check_user_role.role == "seller" and check_user_role.status == "active"  :
            user = User.query.filter_by(id=id, role='seller').first()
        elif check_user_role.role == "super admin" and check_user_role.status == "active":
            user = User.query.filter_by(id=id).first()
        else:
            return make_response(jsonify({"message": "Un Authorized User"}), 401)
        
        # if user:
        #     user = User.query.filter_by(id=id, role='seller').first()

        if not user:
            return {"message": "No user found"}

        sales = Sale.query.filter_by(seller_id=user.id, status="completed").all()
        number_of_sales = len(sales)
        total_commission = sum(sale.commision for sale in sales) 
        
        user_data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'image': user.image,  
            'email': user.email,
            'role': user.role,
            'contact': user.contact,
            "sales":
                [{
                "id": sale.id,
                "commision": sale.commision,
                "status": sale.status,
                "history": sale.history,
                "discount": sale.discount,
                "sale_date": sale.sale_date,
                'status':sale.status,
                "promotions": sale.promotions,
                
                
            } for  sale in sales],  # Using enumerate to count sales starting from 1
            "number_of_sales":number_of_sales,
            
            "total_commission": total_commission 
        }

        response = make_response(jsonify(user_data), 200)
        return response

    @jwt_required()
    def put(self, id):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()

        # Get the JSON data from the request
        data = request.form

        # Querying the user by their id
        if check_user_role.role == 'super admin' and check_user_role.status == "active":
            user = User.query.filter_by(id=id).first()

        elif check_user_role.role == 'admin' and check_user_role.status == "active":
            user = User.query.filter_by(id=id, role='seller').first()

        
        else:
            return make_response(jsonify({"message": "Unauthorized User"}), 401)

        # If no user is found, return an error response
        if not user:
            return make_response(jsonify({"message": "No user to update"}), 401)

        if check_user_role.role == "super admin":
            # Update user attributes if they are provided in the JSON data
            if 'first_name' in data:
                user.first_name = data.get('first_name')
            if 'last_name' in data:
                user.last_name = data.get('last_name')
            if 'image' in data:
                image = request.files.get('image')
                if image.filename == '':
                    return {'error': 'No image selected for upload'}, 400

                def allowed_file(filename):
                    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

                if not allowed_file(image.filename):
                    return {'error': 'Invalid file type. Only images are allowed'}, 400

                # Upload image to Cloudinary
                try:
                    image_upload_result = cloudinary.uploader.upload(image)
                    user.image = image_upload_result['secure_url']
                except Exception as e:
                    return {'error': f'Error uploading image: {str(e)}'}, 500

            if 'email' in data:
                user.email = data.get('email')
            if 'contact' in data:
                user.contact = data.get('contact')
            if 'role' in data:
                user.role = data.get('role')

            # Commit the changes to the database
            db.session.commit()

            # Return a success response
            return make_response(jsonify({'message': 'User updated successfully'}), 200)

        if check_user_role.role == "admin" and check_user_role.status == "active" or check_user_role.role == "seller" and check_user_role.status == "active":
            # Update user attributes if they are provided in the JSON data
            if 'first_name' in data:
                user.first_name = data.get('first_name')
            if 'last_name' in data:
                user.last_name = data.get('last_name')
            if 'image' in data:
                image = request.files.get('image')
                if image.filename == '':
                    return {'error': 'No image selected for upload'}, 400

                def allowed_file(filename):
                    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

                if not allowed_file(image.filename):
                    return {'error': 'Invalid file type. Only images are allowed'}, 400

                # Upload image to Cloudinary
                try:
                    image_upload_result = cloudinary.uploader.upload(image)
                    user.image = image_upload_result['secure_url']
                except Exception as e:
                    return {'error': f'Error uploading image: {str(e)}'}, 500

            if 'email' in data:
                user.email = data.get('email')
            if check_user_role.role == "admin":
                if 'role' in data:
                    user.role = data.get('role')

            if 'contact' in data:
                user.contact = data.get('contact')

            # Commit the changes to the database
            db.session.commit()

            # Return a success response
            return make_response(jsonify({'message': 'User updated successfully'}), 200)
        else:
            return make_response(jsonify({'message': 'Unauthorized'}), 401)


class INVENTORY(Resource):
    # POST
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        check_user_role = User.query.filter_by(id=user_id).first()
        data = request.form
        image = request.files.get('image')
        gallery = request.files.getlist('gallery_images')

        # print(gallery)
        if image.filename == '':
            return {'error': 'No image selected for upload'}, 400

        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

        if not allowed_file(image.filename) or not all(allowed_file(g.filename) for g in gallery):
            return {'error': 'Invalid file type. Only images are allowed'}, 400

        try:
            image_upload_result = cloudinary.uploader.upload(image)
            gallery_upload_results = [cloudinary.uploader.upload(g) for g in gallery]
        except Exception as e:
            return {'error': f'Error uploading image: {str(e)}'}, 500

        if (check_user_role.role == 'admin' and check_user_role.status == "active") or (check_user_role.role == 'super admin' and check_user_role.status == "active"):
            new_inventory_item = Inventory(
                make=data.get('make'),
                image=image_upload_result['secure_url'],
                price=data.get('price'),
                currency=data.get('currency'),
                model=data.get('model'),
                year=data.get('year'),
                VIN=data.get('VIN'),
                color=data.get('color'),
                mileage=data.get('mileage'),
                body_style=data.get('body_style'),
                transmission=data.get('transmission'),
                fuel_type=data.get('fuel_type'),
                engine_size=data.get('engine_size'),
                drive_type=data.get('drive_type'),
                trim_level=data.get('trim_level'),
                condition=data.get('condition'),
                availability=data.get('availability'),
                cylinder=data.get('cylinder'),
                doors=data.get('doors'),
                features=data.get('features'),
                stock_number=data.get('stock_number'),
                purchase_cost=data.get('purchase_cost'),
                profit=data.get('profit'),
                user_id=user_id
            )

            db.session.add(new_inventory_item)
            db.session.commit()

            db.session.refresh(new_inventory_item)
            last_item = Inventory.query.order_by(Inventory.id.desc()).first()

            for result in gallery_upload_results:
                gallery_image = GalleryImage(
                    url=result['secure_url'], inventory_id=last_item.id)
                db.session.add(gallery_image)

            db.session.commit()

            return make_response(jsonify({'message': 'Inventory created successfully'}), 201)
        else:
            return make_response(jsonify({'message': 'User has no access rights to create a Car'}), 401)

    # GET
    # @jwt_required()
    def get(self):
        items = Inventory.query.all()
        return make_response(jsonify([{
            'id': item.id,
            'make': item.make,
            'image': item.image,
            'price': item.price,
            'currency': item.currency,
            'model': item.model,
            'year': item.year,
            'VIN': item.VIN,
            'color': item.color,
            'mileage': item.mileage,
            'body_style': item.body_style,
            'transmission': item.transmission,
            'fuel_type': item.fuel_type,
            'engine_size': item.engine_size,
            'drive_type': item.drive_type,
            'trim_level': item.trim_level,
            'gallery': [gallery.url for gallery in item.gallery],
            'condition': item.condition,
            'availability': item.availability,
            'cylinder': item.cylinder,
            'doors': item.doors,
            'features': item.features,
            'stock_number': item.stock_number,
            'purchase_cost': item.purchase_cost,
            'profit': item.profit,

        } for item in items]))


class inventory_update(Resource):
    @jwt_required()
    def put(self, id):
        user_id = get_jwt_identity()
        check_user_role = User.query.filter_by(id=user_id).first()

        inventory_item = Inventory.query.filter_by(id=id).first()
        if not inventory_item:
            return {'message': 'Inventory item not found'}, 404

        if check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'super admin' and check_user_role.status == "active":
            data = request.form
            # Handle gallery images
            gallery_images = request.files.getlist('gallery')
            for image in gallery_images:
                try:
                    image_upload_result = cloudinary.uploader.upload(image)
                    gallery_image = GalleryImage(
                        url=image_upload_result['secure_url'], inventory_id=id)
                    db.session.add(gallery_image)
                except Exception as e:
                    return {'error': f'Error uploading gallery image: {str(e)}'}, 500

            for key, value in data.items():
                if hasattr(inventory_item, key):
                    setattr(inventory_item, key, value)

            db.session.commit()
            return {'message': 'Inventory item updated successfully'}, 200
        else:
            return {'message': 'User has no access rights to update Inventory'}, 422

    @jwt_required()
    def delete(self, id):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        if check_user_role.role == 'super admin' and check_user_role.status == "active" or check_user_role.role == 'admin' and check_user_role.status == "active":
            gallery = GalleryImage.query.filter_by(inventory_id=id).all()
            for image in gallery:
                db.session.delete(image)
            inventory_item = Inventory.query.filter_by(id=id).first()

            if inventory_item:
                # db.session.delete(inventory_item)
                db.session.commit()

                return {'message': 'Inventory item deleted successfully'}, 200
        else:
            return {'message': 'User has no access rights to delete'}, 422
        return {'message': "Inventory item not found"}, 404


class Importations(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()

        if check_user_role.role == 'super admin' and check_user_role.status == "active" or check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'seller' and check_user_role.status == "active":
            importations = Importation.query.all()
            importations_data = []
            for importation in importations:
                importations_data.append({
                    'id': importation.id,
                    'country_of_origin': importation.country_of_origin,
                    'transport_fee': importation.transport_fee,
                    'currency': importation.currency,
                    'import_duty': importation.import_duty,
                    'import_date': importation.import_date,
                    'import_document': importation.import_document,
                    'car': [
                        {
                            "id": car.id,
                            "make": car.make,
                            "model": car.model,
                            "image": car.image,
                            "year": car.year,
                            "currency": car.currency,
                            "purchase_cost": car.purchase_cost
                        } for car in Inventory.query.filter_by(id=importation.car_id).all()

                    ]
                })
            return make_response(jsonify(importations_data), 200)
        else:
            return make_response(jsonify({"message": "Unauthorized User"}), 401)

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        if check_user_role.role == 'super admin' and check_user_role.status == "active" or check_user_role.role == 'admin' and check_user_role.status == "active":
            # Get form data and uploaded file
            data = request.form
            import_document = request.files.get('import_document')

            # Check if all required fields are present
            required_fields = ['country_of_origin', 'transport_fee', 'currency', 'import_duty', 'import_date', 'car_id']
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return make_response(jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400)

            if import_document is None or import_document.filename == '':
                return {'error': 'No document selected for upload'}, 400

            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}

            if not allowed_file(import_document.filename):
                return {'error': 'Invalid file type. Only images are allowed'}, 400

            # Upload document to Cloudinary
            try:
                document_upload_result = cloudinary.uploader.upload(import_document)
            except Exception as e:
                return {'error': f'Error uploading document: {str(e)}'}, 500

            # Create new Importation object
            new_importation = Importation(
                country_of_origin=data['country_of_origin'],
                transport_fee=data['transport_fee'],
                currency=data['currency'],
                import_duty=data['import_duty'],
                import_date=data['import_date'],
                import_document=document_upload_result['secure_url'],
                car_id=data['car_id']
            )

            # Add and commit to database
            db.session.add(new_importation)
            db.session.commit()

            return make_response(jsonify({'message': 'Importation created successfully'}), 201)
        else:
            return make_response(jsonify({"message": "Unauthorized User"}), 404)


class UpdateImportation(Resource):
    @jwt_required()
    def put(self, importation_id):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        if check_user_role.role == 'super admin' and check_user_role.status == "active" or check_user_role.role == 'admin' and check_user_role.status == "active":
            data = request.form
            importation = Importation.query.get(importation_id)
            doc = request.files.get(
                'import_document', importation.import_document)

            if doc.filename == '':
                return {'error': 'No image selected for upload'}, 400

            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}

            if not allowed_file(doc.filename):
                return {'error': 'Invalid file type. Only images are allowed'}, 400

            # Upload image to Cloudinary
            try:
                image_upload_result = cloudinary.uploader.upload(doc)
                importation.import_document = image_upload_result['secure_url']
            except Exception as e:
                return {'error': f'Error uploading document: {str(e)}'}, 500
            if not importation:
                return make_response(jsonify({'message': 'Importation not found'}), 404)
            importation.country_of_origin = data.get(
                'country_of_origin', importation.country_of_origin)
            importation.transport_fee = data.get(
                'transport_fee', importation.transport_fee)
            importation.currency = data.get('currency', importation.currency)
            importation.import_duty = data.get(
                'import_duty', importation.import_duty)
            importation.import_date = data.get(
                'import_date', importation.import_date)
            # importation.import_document = image_upload_result
            importation.car_id = data.get('car_id', importation.car_id)
            db.session.commit()
            return make_response(jsonify({'message': 'Importation updated successfully'}), 200)
        else:
            return make_response(jsonify({"message": "Unauthorized User"}), 404)

    @jwt_required()
    def delete(self, importation_id):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        if check_user_role.role == 'super admin' and check_user_role.status == "active" or check_user_role.role == 'admin' and check_user_role.status == "active":
            importation = Importation.query.get(importation_id)
            if not importation:
                return make_response(jsonify({'message': 'Importation not found'}), 404)
            db.session.delete(importation)
            db.session.commit()
            return make_response(jsonify({'message': 'Importation deleted successfully'}), 200)
        else:
            return make_response(jsonify({"message": "Unauthorized User"}), 404)
class DetailCustomer(Resource):
    @jwt_required()
    def get(self):
        # Get the current user's ID from the JWT token
        user_id = get_jwt_identity()
        check_user_role = User.query.filter_by(id=user_id).first()
        # Retrieve only the customers associated with the current seller (user)
        if check_user_role.role == 'seller' and check_user_role.status == "active" :
            customers = Customer.query.filter_by(seller_id=user_id).all()
        
        # Check if customers exist
            if not customers:
                return make_response(jsonify({'message': 'No customers found for this seller'}), 404)

            # Serialize customer data
            serialized_customers = [{
                "first_name": customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email,
                'address': customer.address,
                'phone_number': customer.phone_number,
                'image_file': customer.image
            } for customer in customers]

            return make_response(jsonify(serialized_customers), 200)
class Customers(Resource):
    @jwt_required()
    def get(self):
        # Get the current user's ID from the JWT token
        current_user_id = get_jwt_identity()

        # Retrieve only the customers associated with the current seller (user)
        customers = Customer.query.filter_by(seller_id=current_user_id).all()
        
        # Check if customers exist
        if not customers:
            return make_response(jsonify({'message': 'No customers found for this seller'}), 404)

        # Serialize customer data
        serialized_customers = [{
            "first_name": customer.first_name,
            'last_name': customer.last_name,
            'email': customer.email,
            'address': customer.address,
            'phone_number': customer.phone_number,
            'image_file': customer.image
        } for customer in customers]

        return make_response(jsonify(serialized_customers), 200)
    
    @jwt_required()  # Require JWT authentication
    def post(self):

        user_id = get_jwt_identity()

        data = request.form
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        address = data.get('address')
        phone_number = data.get('phone_number')
        image_file = request.files.get('image')

        if not all([first_name, last_name, email, address, phone_number, image_file]):
            return {'error': '422 Unprocessable Entity', 'message': 'Missing customer details'}, 422

        # Get the current user's ID from the JWT token
        current_user_id = get_jwt_identity()

        # Retrieve the user object from the database
        user = User.query.filter_by(id=current_user_id).first()

        # Check if the user exists and has the role "seller"
        if not user or user.role != "seller":
            return {'error': '403 Forbidden', 'message': 'User is not authorized to add customer details'}, 403

        # Check if file uploaded and is an image
        if image_file.filename == '':
            return {'error': 'No image selected for upload'}, 400

        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

        if not allowed_file(image_file.filename):
            return {'error': 'Invalid file type. Only images are allowed'}, 400

        # Upload image to Cloudinary
        try:
            image_upload_result = cloudinary.uploader.upload(image_file)
        except Exception as e:
            return {'error': f'Error uploading image: {str(e)}'}, 500

        # Create a new customer object
        new_customer = Customer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            phone_number=phone_number,
            # Store Cloudinary URL
            image=image_upload_result['secure_url'],
            created_at=datetime.now(),

            seller_id=user_id  # Assign the current user ID as the seller ID
        )

        db.session.add(new_customer)
        db.session.commit()

        return {'message': 'Customer details added successfully'}, 201
class UpdateDetails(Resource):    
    @jwt_required()
    def put(self, customer_id):
        # Get the current user's identity
        current_user_id = get_jwt_identity()

        # Retrieve the customer to update
        customer = Customer.query.filter_by(id=customer_id, seller_id=current_user_id).first()
        if not customer:
            return {'message': 'Customer not found or not authorized to update'}, 404

        # Parse customer data from request form
        data = request.form
        image_file = request.files.get('image')

        # Update fields if they are provided
        for key in ['first_name', 'last_name', 'email', 'address', 'phone_number']:
            if key in data:
                setattr(customer, key, data[key])

        # Check if file uploaded and is an image
        if image_file.filename == '':
            return {'error': 'No image selected for upload'}, 400

        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

        if not allowed_file(image_file.filename):
            return {'error': 'Invalid file type. Only images are allowed'}, 400

        # Upload image to Cloudinary
        try:
            image_upload_result = cloudinary.uploader.upload(image_file)
        except Exception as e:
            return {'error': f'Error uploading image: {str(e)}'}, 500

        db.session.commit()
        return {'message': 'Customer details updated successfully'}, 200
class DeleteDetails(Resource):
    @jwt_required()
    def delete(self, customer_id):
        # Get the current user's identity
        current_user_id = get_jwt_identity()

        # Retrieve and delete the customer
        customer = Customer.query.filter_by(id=customer_id, seller_id=current_user_id).first()
        if not customer:
            return {'message': 'Customer not found or not authorized to delete'}, 404

        db.session.delete(customer)
        db.session.commit()

        return {'message': 'Customer deleted successfully'}, 200

class SaleResource(Resource):
    # POST
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        if check_user_role.role == 'seller' and check_user_role.status == "active":
            data = request.get_json()

            # commision =data.get('commision')
            
            status=data.get('status')
            history=data.get('history')
            discount=data.get('discount')
            sale_date=data.get('sale_date')
            customer_id=data.get('customer_id')
            seller_id=user_id
            inventory_id=data.get('inventory_id')
            promotions=data.get('promotions')
            
            if not status or not history or not discount or not sale_date or not customer_id or not inventory_id  :
                inventory =Inventory.query.filter_by(id =inventory_id).first()
                
                commision = inventory.price * 0.20
                
                sale = Sale(
                    commision=commision,
                    status=status,
                    history=history,
                    discount=discount,
                    sale_date=sale_date,
                    customer_id=customer_id,
                    seller_id=seller_id,
                    inventory_id=inventory_id,
                    promotions=promotions
                )

                db.session.add(sale)
                db.session.commit()

                return make_response(jsonify({'message': 'Sale created successfully'}), 201)
            
            else:
                return make_response(jsonify({'message': 'Unauthorized User'}), 401)
        else:
            return make_response(jsonify({'message': 'Enter all Data required'}), 401)
    # GET
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()

        if check_user_role.role == 'seller' and check_user_role.status == "active":
            serialized_sales = []
            sales = Sale.query.filter_by(seller_id=check_user_role.id).all()
            customers = Customer.query.all()
            customer_dict = {customer.id: customer for customer in customers}  # Create a dictionary for quick lookup
            
            for sale in sales:
                customer = customer_dict.get(sale.customer_id)  # Get the specific customer for this sale
                seller = User.query.filter_by(id=sale.seller_id).first()
                inventory = Inventory.query.filter_by(id=sale.inventory_id).first()
                
                if customer and seller and inventory:
                    serialized_sale = {
                        "commision": sale.commision,
                        "status": sale.status,
                        "history": sale.history,
                        "discount": sale.discount,
                        "sale_date": sale.sale_date,
                        "customer": {
                            "id": customer.id,
                            "Names": f'{customer.first_name} {customer.last_name}',
                            "email": customer.email,
                        },
                        "seller": {
                            "id": seller.id,
                            "Names ": f'{seller.first_name} {seller.last_name}',
                            "email": seller.email,
                        },
                        "inventory_id": {
                            "id": inventory.id,
                            "name": inventory.make
                        },
                        "promotions": sale.promotions,
                    }
                    serialized_sales.append(serialized_sale)
            return make_response(jsonify(serialized_sales), 200)
        else:
            return make_response(jsonify({"message": "User unauthorized"}), 401)
        

class SaleItemResource(Resource):
    # PUT
    @jwt_required()
    def put(self, sale_id):
        user_id = get_jwt_identity()

        # Get the sale object
        check_user_role = User.query.filter_by(id=user_id).first()
        
        if check_user_role.role == 'seller' and check_user_role.status == 'active':
            sale = Sale.query.filter_by(id=sale_id, seller_id=user_id).first()

            # Check if the logged-in user is the seller who created the sale
            # if sale.seller_id != user_id:
            #     return make_response(jsonify({"message": "Unauthorized"}), 401)
            if not sale:
                 return make_response(jsonify({'message': 'Sale not found'}), 400)
            # Get the request data
            data = request.get_json()

            
            if 'status' in data:
                sale.status = data['status']
            
            # Commit the changes to the database
            db.session.commit()

            return make_response(jsonify({'message': 'Sale updated successfully'}), 201)

    # DELETE
    # who should be deleting a sale ?
    def delete(self, sale_id):
        sale = Sale.query.get_or_404(sale_id)
        db.session.delete(sale)
        db.session.commit()

        return jsonify({'message': 'Sale deleted successfully'}, 201)
# class GeneralSale(Resource):
#     @jwt_required
#     def get(self):
#         user_id = get_jwt_identity()

#         check_user_role = User.query.filter_by(id=user_id).first()

#         if (check_user_role.role == 'admin' and check_user_role.status == "active") or (check_user_role.role == 'super admin' and check_user_role.status == "active"):
#             serialized_sales = []
#             for sale in Sale.query.all():
#                 customer = Customer.query.filter_by(id=sale.customer_id).first()
#                 seller = User.query.filter_by(id=sale.seller_id).first()
#                 inventory = Inventory.query.filter_by(id=sale.inventory_id).first()
#                 serialized_sale = {
#                     # "id": sale.id,
#                     "customer": len(customer),
#                     "seller": len(seller),
#                     "inventory_id": len(inventory),
                    
#                 }
#                 serialized_sales.append(serialized_sale)
#             return make_response(serialized_sales)  # Use serialized_sales instead of serialized_sale
        
#         else:
#             return make_response(({"message":"User unauthorized"}))
            
    
class AdminSales(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()

        if (check_user_role.role == 'admin' and check_user_role.status == "active") or (check_user_role.role == 'super admin' and check_user_role.status == "active"):
            serialized_sales = []
            customers = Customer.query.all()
            customer_dict = {customer.id: customer for customer in customers}  # Create a dictionary for quick lookup
            
            sales = Sale.query.all()
            for sale in sales:
                customer = customer_dict.get(sale.customer_id)  # Get the specific customer for this sale
                seller = User.query.filter_by(id=sale.seller_id).first()
                inventory = Inventory.query.filter_by(id=sale.inventory_id).first()

                if customer and seller and inventory:
                    serialized_sale = {
                        "id": sale.id,
                        "commision": sale.commision,
                        "status": sale.status,
                        "history": sale.history,
                        "discount": sale.discount,
                        "sale_date": sale.sale_date,
                        "customer": {
                            "id": customer.id,
                            "Names": f'{customer.first_name} {customer.last_name}',
                            "email": customer.email,
                        },
                        "seller": {
                            "id": seller.id,
                            "Names": f'{seller.first_name} {seller.last_name}',
                            "email": seller.email,
                        },
                        "inventory_id": {
                            "id": inventory.id,
                            "name": inventory.make
                        },
                        "promotions": sale.promotions,
                    }
                    serialized_sales.append(serialized_sale)
            return make_response(jsonify(serialized_sales), 200)
        else:
            return make_response(jsonify({"message": "User unauthorized"}), 401)

        
class OneSellerAdmin(Resource):
    @jwt_required()
    def get(self, sale_id):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()

        if check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'super admin' and check_user_role.status == "active":
            
            sale = Sale.query.filter_by(id=sale_id).first()
            
            if not sale:
                return make_response(jsonify({"message": "Sale not found"}), 404)

            customer = Customer.query.filter_by(id=sale.customer_id).first()
            seller = User.query.filter_by(id=sale.seller_id).first()
            inventory =Inventory.query.filter_by(id =sale.inventory_id).first()
            
            if not customer or not seller:
                return make_response(jsonify({"message": "Customer or seller not found for this sale"}), 404)

            one_sale = {
                "commision": sale.commision,
                "status": sale.status,
                "history": sale.history,
                "discount": sale.discount,
                "sale_date": sale.sale_date,
                "customer": {
                    "id": customer.id,
                    "Names": f'{customer.first_name} {customer.last_name}',
                    "email": customer.email,
                    
                },
                "seller": {
                    "id": seller.id,
                    "Names": f'{seller.first_name} {seller.last_name}',
                    "email": seller.email,
                    
                },
                "inventory_id": {
                                 "id":inventory.id,
                                 "name":inventory.make,
                                 "image":inventory.image
                                 },
                "promotions": sale.promotions,
            }
            return make_response(jsonify(one_sale), 200)
        elif check_user_role.role == 'seller' :
            sale = Sale.query.filter_by(id=sale_id, seller_id =user_id).first()
        
            if not sale:
                return make_response(jsonify({"message": "Sale not found"}), 404)

            customer = Customer.query.filter_by(id=sale.customer_id).first()
            seller = User.query.filter_by(id=sale.seller_id).first()
            inventory =Inventory.query.filter_by(id =sale.inventory_id).first()

            if not customer or not seller:
                return make_response(jsonify({"message": "Customer or seller not found for this sale"}), 404)

            one_sale = {
                "commision": sale.commision,
                "status": sale.status,
                "history": sale.history,
                "discount": sale.discount,
                "sale_date": sale.sale_date,
                "customer": {
                    "id": customer.id,
                    "Names": f'{customer.first_name} {customer.last_name}',
                    "email": customer.email,
                    
                },
                "seller": {
                    "id": seller.id,
                    "Names": f'{seller.first_name} {seller.last_name}',
                    "email": seller.email,
                    
                },
                "inventory_id": {
                                    "id":inventory.id,
                                    "name":inventory.make
                                    },
                "promotions": sale.promotions,
            }
            return make_response(jsonify(one_sale), 200)
        else:
            return make_response(jsonify({"message":"User unauthorized"}), 401)  

class Report(Resource):
    # POST
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        if check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'super admin' and check_user_role.status == "active":
            data = request.get_json()

            company_profit = data.get('company_profit')
            sales_id = data.get('sales_id')
            expenses = data.get('expenses')
            sale_date = data.get('sale_date')
            customer_id = data.get('customer_id')
            seller_id = data.get('seller_id')
            importation_id = data.get('importation_id')
            
            if not all([company_profit, sales_id, expenses, sale_date]):
                return make_response(jsonify({'message': 'Please provide all required data'}), 400)

            new_report = Report(
                company_profit=company_profit,
                sales_id=sales_id,
                expenses=expenses,
                sale_date=sale_date,
                customer_id=customer_id,
                seller_id=seller_id,
                importation_id=importation_id
            )

            db.session.add(new_report)
            db.session.commit()

            return make_response(jsonify({'message': 'Report created successfully'}), 201)
        else:
            return make_response(jsonify({'message': 'User has no access rights to create a report'}), 401)

  # GET
@jwt_required()
def get(self):
    user_id = get_jwt_identity()

    check_user_role = User.query.filter_by(id=user_id).first()

    if check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'super admin' and check_user_role.status == "active":
        reports = Report.query.all()
        serialized_reports = []
        for report in reports:
            customer = Customer.query.filter_by(id=report.customer_id).first()
            seller = User.query.filter_by(id=report.seller_id).first()
            importation = Importation.query.filter_by(id=report.importation_id).first()
            sale = Sale.query.filter_by(id=report.sales_id).first()

            serialized_report = {
                'id': report.id,
                'company_profit': report.company_profit,
                'expenses': report.expenses,
                'sale_date': report.sale_date,
                'customer': {
                    'id': customer.id,
                    'Names': f'{customer.first_name} {customer.last_name}',
                    'email': customer.email,
                },
                'seller': {
                    'id': seller.id,
                    'Names': f'{seller.first_name} {seller.last_name}',
                    'email': seller.email,
                },
                'importation': {
                    'id': importation.id,
                    'name': importation.name,
                },
                'sale': {
                    'id': sale.id,
                    'commision': sale.commision,
                    'status': sale.status,
                    'history': sale.history,
                    'discount': sale.discount,
                    'sale_date': sale.sale_date,
                    'promotions': sale.promotions,
                }
            }
            serialized_reports.append(serialized_report)
        return make_response(jsonify(serialized_reports), 200)
    else:
        return make_response(jsonify({'message': 'User unauthorized'}), 401)


class Report_update(Resource):
    # PATCH
    @jwt_required()
    def patch(self, id):
        user_id = get_jwt_identity()
        check_user_role = User.query.filter_by(id=user_id).first()

        if check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'super admin' and check_user_role.status == "active":
            return {'message': 'User unauthorized'}, 401

        report = Report.query.filter_by(id=id).first()
        if not report:
            return {'message': 'Report not found'}, 404

        data = request.get_json()
        for key, value in data.items():
            if hasattr(report, key):
                setattr(report, key, value)

        db.session.commit()
        return {'message': 'Report updated successfully'}, 200

    # DELETE
    @jwt_required()
    def delete(self, id):
        user_id = get_jwt_identity()
        check_user_role = User.query.filter_by(id=user_id).first()

        if check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'super admin' and check_user_role.status == "active":
           
            report = Report.query.filter_by(id=id).first()
            if not report:
                return {'message': 'Report not found'}, 404

            db.session.delete(report)
            db.session.commit()
            return {'message': 'Report deleted successfully'}, 200
        else:
            return make_response(jsonify({'message': 'User unauthorized'}), 401)

class ReceiptAll(Resource):
    # POST
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        if check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'super admin' and check_user_role.status == "active" or check_user_role.role == 'seller' and check_user_role.status == "active":
            data = request.json

            new_receipt = Receipt(
                user_id=user_id,
                customer_id=data.get('customer_id'),
                invoice_id=data.get('invoice_id'),
                amount_paid=data.get('amount_paid'),
                time_stamp=datetime.now()
            )

            db.session.add(new_receipt)
            db.session.commit()

            db.session.refresh(new_receipt)
            return make_response(jsonify({'message': 'Receipt created successfully'}), 201)
        else:
            return make_response(jsonify({'message': 'User unauthorized'}), 401)

    # GET
    @jwt_required()
    
    
    def get(self):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        # print(check_user_role)
        if not check_user_role or check_user_role.status != "active":
            return make_response(jsonify({'message': 'User unauthorized'}), 401)

        serialized_receipts = []

        if check_user_role.role in ['admin', 'super admin']:
            receipts = Receipt.query.all()
        elif check_user_role.role == 'seller':
            receipts = Receipt.query.filter_by(user_id=user_id).all()
        else:
            return make_response(jsonify({'message': 'User unauthorized'}), 401)

        for receipt in receipts:
            customer = Customer.query.filter_by(id=receipt.customer_id).first()
            invoice = Invoice.query.filter_by(id=receipt.invoice_id).first()
            user = User.query.filter_by(id=receipt.user_id).first()

            if not (customer and invoice and user):
                continue  # Skip this receipt if any required data is missing

            serialized_receipt = {
                'id': receipt.id,
                'user': {
                    "id": user.id,
                    "names": f'{user.first_name} {user.last_name}',
                    "email": user.email,
                },
                'customer': {
                    'id': customer.id,
                    'Names': f'{customer.first_name} {customer.last_name}',
                    'email': customer.email,
                },
                'invoice': {
                    'id': invoice.id,
                    'amount_paid': invoice.amount_paid,
                    # 'date': invoice.created_at,
                    'total_amount': invoice.total_amount,  # Assuming this field exists
                    'balance': invoice.balance,  # Assuming this field exists
                },
                'amount_paid': receipt.amount_paid,
                'created_at': receipt.created_at
            }
            serialized_receipts.append(serialized_receipt)

        return make_response(jsonify(serialized_receipts), 200)



class Receipt_update(Resource):
    # PATCH
    @jwt_required()
    # add for seller to fetch their own only
    def patch(self, id):
        user_id = get_jwt_identity()
        check_user_role = User.query.filter_by(id=user_id).first()

        if check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'super admin' and check_user_role.status == "active":
            

            data = request.json

            receipt = Receipt.query.filter_by(id=id).first()
            if not receipt:
                return {'message': 'Receipt not found'}, 404

            for key, value in data.items():
                if hasattr(receipt, key):
                    setattr(receipt, key, value)

            db.session.commit()
            return {'message': 'Receipt updated successfully'}, 200
        

        elif check_user_role.role == 'seller' and check_user_role.status == "active":
            data = request.json

            receipt = Receipt.query.filter_by(id=id).first()
            if  receipt.user_id ==user_id:
                
                for key, value in data.items():
                    if hasattr(receipt, key):
                        setattr(receipt, key, value)

                db.session.commit()
                return {'message': 'Receipt updated successfully'}, 200
            else:
                return make_response(jsonify({'message': 'User unauthorized'}), 401)
        else:
            return make_response(jsonify({'message': 'User unauthorized'}), 401)

    # DELETE
    @jwt_required()
    # create a recipt delete for seller
    def delete(self, id):
        user_id = get_jwt_identity()
        check_user_role = User.query.filter_by(id=user_id).first()

        if check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'super admin' and check_user_role.status == "active"or check_user_role.role == 'seller' and check_user_role.status == "active" :
            

            receipt = Receipt.query.filter_by(id=id).first()
            if not receipt:
                return {'message': 'Receipt not found'}, 404

            db.session.delete(receipt)
            db.session.commit()
            return {'message': 'Receipt deleted successfully'}, 200
        elif check_user_role.role == 'seller' and check_user_role.status == "active":
            receipt = Receipt.query.filter_by(id=id).first()
            if  receipt.user_id==user_id:
                db.session.delete(receipt)
                db.session.commit()
                return {'message': 'Receipt deleted successfully'}, 200
            else:
                return make_response(jsonify({'message': 'User unauthorized'}), 401)
            
        else:
            return make_response(jsonify({'message': 'User unauthorized'}), 401)

class InvoiceCreate(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)

        if current_user.role != 'seller':
            return make_response(jsonify({'message': 'Unauthorized - Only sellers can create invoices'}), 403)

        data = request.get_json()
        try:
            new_invoice = Invoice(
                date_of_purchase = datetime.strptime(data['date_of_purchase'], "%Y-%m-%d"),
                method=data['method'],
                amount_paid=data['amount_paid'],
                fee=data['fee'],
                tax=data['tax'],
                currency=data['currency'],
                seller_id=user_id,  
                customer_id=data['customer_id'],
                vehicle_id=data['vehicle_id'],
                balance=data['balance'],
                total_amount=data['total_amount'],
                installments=data['installments'],
                pending_cleared=data['pending_cleared'],
                signature=data['signature'],
                warranty=data['warranty'],
                terms_and_conditions=data['terms_and_conditions'],
                agreement_details=data['agreement_details'],
                additional_accessories=data['additional_accessories'],
                notes_instructions=data['notes_instructions'],
                payment_proof=data['payment_proof'],
                
            )
            db.session.add(new_invoice)
            db.session.commit()
            return make_response(jsonify({'message': 'Invoice created successfully', 'invoice_id': new_invoice.id}), 201)
        except Exception as e:
            return make_response(jsonify({'message': 'Failed to create invoice', 'error': str(e)}), 500)
    

class GeneralInvoices(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        
        if check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'super admin' and check_user_role.status == "active":
            invoices = Invoice.query.all()

            # Create a dictionary to store aggregated data for each seller
            seller_data = defaultdict(lambda: {'total_customers': 0, 'total_sales': 0, 'total_inventory_sold': 0})

            # Loop through each invoice and aggregate data
            for invoice in invoices:
                seller_name = f"{invoice.user.first_name} {invoice.user.last_name}"  # Assuming 'first_name' and 'last_name' fields in the User model
                seller_data[seller_name]['total_customers'] += 1
                seller_data[seller_name]['total_sales'] += 1 # Increment total sales sold
                seller_data[seller_name]['total_inventory_sold'] += 1  # Increment total inventory sold

            # Convert the aggregated data into a list of dictionaries
            aggregated_invoices = [
                {
                    'seller_name': seller_name,
                    'total_customers': data['total_customers'],
                    'total_sales': data['total_sales'],
                    'total_inventory_sold': data['total_inventory_sold']
                }
                for seller_name, data in seller_data.items()
            ]

            return make_response(jsonify(aggregated_invoices), 200)
        else:
            return make_response(jsonify({"Message":"user unauthorized"}), 401)
class AllInvoices(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        if check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'super admin' and check_user_role.status == "active":
            invoices_data=[]
            for invoice in Invoice.query.filter_by(id=user_id).all():
                customer = Customer.query.get(invoice.customer_id)
                vehicle = Inventory.query.get(invoice.vehicle_id)
                invoice_dict={
                        'id': invoice.id,
                        'date_of_purchase': invoice.date_of_purchase,
                        'method': invoice.method,
                        'amount_paid': invoice.amount_paid,
                        'fee': invoice.fee,
                        'tax': invoice.tax,
                        'currency': invoice.currency,
                        'seller_id': invoice.seller_id,
                        'customer_name': {
                                'id':customer.id,
                                "name":f'{customer.first_name } {customer.last_name }'
                                },
                        'vehicle_details': {
                                'id':vehicle.id,
                                'make': vehicle.make,
                                'model': vehicle.model ,
                                'year': vehicle.year,
                                
                            },
                        'balance': invoice.balance,
                        'total_amount': invoice.total_amount,
                        'installments': invoice.installments,
                        'pending_cleared': invoice.pending_cleared,
                        'signature': invoice.signature,
                        'warranty': invoice.warranty,
                        'terms_and_conditions': invoice.terms_and_conditions,
                        'agreement_details': invoice.agreement_details,
                        'additional_accessories': invoice.additional_accessories,
                        'notes_instructions': invoice.notes_instructions,
                        'payment_proof': invoice.payment_proof,
                        'created_at': invoice.created_at,
                        'updated_at': invoice.updated_at.isoformat() if invoice.updated_at else None,

                    }
                invoices_data.append(invoice_dict)

                
                
            
            return make_response(jsonify(invoices_data), 200)
        elif check_user_role.role == 'seller' and check_user_role.status == "active":
            invoices_data=[]
            for invoice in Invoice.query.filter_by(id=user_id).all():
                customer = Customer.query.get(invoice.customer_id)
                vehicle = Inventory.query.get(invoice.vehicle_id)
                invoice_dict={
                        'id': invoice.id,
                        'date_of_purchase': invoice.date_of_purchase,
                        'method': invoice.method,
                        'amount_paid': invoice.amount_paid,
                        'fee': invoice.fee,
                        'tax': invoice.tax,
                        'currency': invoice.currency,
                        'seller_id': invoice.seller_id,
                        'customer_name': {
                                'id':customer.id,
                                "name":f'{customer.first_name } {customer.last_name }'
                                },
                        'vehicle_details': {
                                'id':vehicle.id,
                                'make': vehicle.make,
                                'model': vehicle.model ,
                                'year': vehicle.year,
                                
                            },
                        'balance': invoice.balance,
                        'total_amount': invoice.total_amount,
                        'installments': invoice.installments,
                        'pending_cleared': invoice.pending_cleared,
                        'signature': invoice.signature,
                        'warranty': invoice.warranty,
                        'terms_and_conditions': invoice.terms_and_conditions,
                        'agreement_details': invoice.agreement_details,
                        'additional_accessories': invoice.additional_accessories,
                        'notes_instructions': invoice.notes_instructions,
                        'payment_proof': invoice.payment_proof,
                        'created_at': invoice.created_at,
                        'updated_at': invoice.updated_at.isoformat() if invoice.updated_at else None,

                    }
                invoices_data.append(invoice_dict)

                
                
            
            return make_response(jsonify(invoices_data), 200)
        else:
            return make_response(jsonify({'message': 'User unauthorized'}), 401)
class AdminInvoice(Resource):
    @jwt_required()
    def get(self, seller_name):
        user_id = get_jwt_identity()
        check_user_role = User.query.filter_by(id=user_id).first()

        if not check_user_role:
            return make_response(jsonify({'Message': "User not found"}), 404)

        user = User.query.filter_by(first_name=seller_name).first()

        if not user:
            return make_response(jsonify({'Message': "No user found"}), 404)

        if check_user_role.role not in ['admin', 'super admin'] or check_user_role.status != "active":
            return make_response(jsonify({'Message': "User unauthorized"}), 401)

        invoices = Invoice.query.filter_by(seller_id=user.id).all()

        if not invoices:
            return make_response(jsonify({'Message': "No Invoice found"}), 404)

        invoice_data = []
        for invoice in invoices:
            seller = User.query.get(invoice.seller_id)
            customer = Customer.query.get(invoice.customer_id)
            vehicle = Inventory.query.get(invoice.vehicle_id)

            invoice_dict = {
                'id': invoice.id,
                'date_of_purchase': invoice.date_of_purchase,
                'method': invoice.method,
                'amount_paid': invoice.amount_paid,
                'fee': invoice.fee,
                'tax': invoice.tax,
                'currency': invoice.currency,
                'seller_name': {
                    'id': seller.id,
                    'name': f'{seller.first_name} {seller.last_name}'
                } if seller else None,
                'customer_name': {
                    'id': customer.id if customer else None,
                    'name': f'{customer.first_name} {customer.last_name}' if customer else None
                },
                'vehicle_details': {
                    'id': vehicle.id if vehicle else None,
                    'make': vehicle.make if vehicle else None,
                    'model': vehicle.model if vehicle else None,
                    'year': vehicle.year if vehicle else None
                },
                'balance': invoice.balance,
                'total_amount': invoice.total_amount,
                'installments': invoice.installments,
                'pending_cleared': invoice.pending_cleared,
                'signature': invoice.signature,
                'warranty': invoice.warranty,
                'terms_and_conditions': invoice.terms_and_conditions,
                'agreement_details': invoice.agreement_details,
                'additional_accessories': invoice.additional_accessories,
                'notes_instructions': invoice.notes_instructions,
                'payment_proof': invoice.payment_proof,
                'created_at': invoice.created_at,
                'updated_at': invoice.updated_at.isoformat() if invoice.updated_at else None,
            }
            invoice_data.append(invoice_dict)

        return make_response(jsonify(invoice_data), 200)

class InvoiceGet(Resource):
    
    @jwt_required()
    def get(self, invoice_id):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        if check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'seller' and check_user_role.status == "active" or check_user_role.role == 'super admin' and check_user_role.status == "active":
            invoice = Invoice.query.filter_by(id=invoice_id).first()
            vehicle = Inventory.query.filter_by(id=invoice.vehicle_id).first()
            seller = User.query.filter_by(id=invoice.seller_id).first()
            customer = Customer.query.get(invoice.customer_id)
            
            if invoice:
                invoice_data = {
                    'id': invoice.id,
                    'date_of_purchase': invoice.date_of_purchase,
                    'method': invoice.method,
                    'amount_paid': invoice.amount_paid,
                    'fee': invoice.fee,
                    'tax': invoice.tax,
                    'currency': invoice.currency,
                    'seller':{
                        "id":seller.id,
                        "names":f'{seller.first_name} {seller.last_name}'
                        },
                    'customer_name': {
                                'id':customer.id,
                                "name":f'{customer.first_name } {customer.last_name }',
                                "address":customer.address,
                                'email':customer.email
                                },
                    'vehicle': {
                                "id":vehicle.id,
                                "make":vehicle.make,
                                "year":vehicle.year,
                                "model":vehicle.model
                                },
                    'balance': invoice.balance,
                    'total_amount': invoice.total_amount,
                    'installments': invoice.installments,
                    'pending_cleared': invoice.pending_cleared,
                    'signature': invoice.signature,
                    'warranty': invoice.warranty,
                    'terms_and_conditions': invoice.terms_and_conditions,
                    'agreement_details': invoice.agreement_details,
                    'additional_accessories': invoice.additional_accessories,
                    'notes_instructions': invoice.notes_instructions,
                    'payment_proof': invoice.payment_proof,
                    'created_at': invoice.created_at,
                    'updated_at': invoice.updated_at.isoformat() if invoice.updated_at else None,

                }
                return jsonify(invoice_data)
            else:
                return make_response(jsonify({'message': 'Invoice not found'}), 404)
        else:
            return make_response(jsonify({'message': 'User unauthorized'}), 401)
class InvoiceUpdate(Resource):
    @jwt_required()
    def put(self, invoice_id):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        if check_user_role.role == 'seller' and check_user_role.status == "active":
            invoice = Invoice.query.filter_by(id=invoice_id).first()
            if invoice.seller_id==user_id:
                

                data = request.get_json()
                for key, value in data.items():
                    if hasattr(invoice, key):
                        setattr(invoice, key, value)

                db.session.commit()
                return make_response(jsonify({'message': 'Invoice updated successfully'}), 200)
            return make_response(jsonify({'message': 'User unauthorized'}), 401)
        else:
            
            return make_response(jsonify({'message': 'User unauthorized'}), 401)
# this route is not protected only the seller can produce an invoice
class InvoiceDelete(Resource):
    @jwt_required()
    def delete(self, invoice_id):
        user_id = get_jwt_identity()
        # only a seller can delete an invoice
        check_user_role = User.query.filter_by(id=user_id).first()
        if  check_user_role.role == 'seller' and check_user_role.status == "active":
            invoice = Invoice.query.filter_by(id=invoice_id).first()
            if invoice.seller_id==user_id :
                

                db.session.delete(invoice)
                db.session.commit()
                return make_response(jsonify({'message': 'Invoice deleted successfully'}), 200)
            return make_response(jsonify({'message': 'User unauthorized'}), 401)
        else:
            return make_response(jsonify({'message': 'User unauthorized'}), 401)
        
class Notification(Resource):
    # POST
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        if check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'seller' and check_user_role.status == "active" or check_user_role.role == 'super admin' and check_user_role.status == "active":
            

            data = request.json

            new_notification = Notification(
                user_id=user_id,
                customer_id=data.get('customer_id'),
                notification_type=data.get('notification_type'),
                message=data.get('message'),
                time_stamp=datetime.now()
            )

            db.session.add(new_notification)
            db.session.commit()

            db.session.refresh(new_notification)
            return make_response(jsonify({'message': 'Notification created successfully'}), 201)
        else:
            return make_response(jsonify({'message': 'User unauthorized'}), 401)

 # GET
@jwt_required()
 
def get(self):
    user_id = get_jwt_identity()

    check_user_role = User.query.filter_by(id=user_id).first()

    if check_user_role.role == 'admin' and check_user_role.status == "active" or  check_user_role.role == 'super admin' and check_user_role.status == "active":
        notifications = Notification.query.all()
        serialized_notifications = []
        for notification in notifications:
            customer = Customer.query.filter_by(id=notification.customer_id).first()

            serialized_notification = {
                'id': notification.id,
                'user_id': notification.user_id,
                'customer_id': notification.customer_id,
                'notification_type': notification.notification_type,
                'message': notification.message,
                'time_stamp': notification.time_stamp,
                'customer': {
                    'id': customer.id,
                    'Names': f'{customer.first_name} {customer.last_name}',
                    'email': customer.email,
                }
            }
            serialized_notifications.append(serialized_notification)
        return make_response(jsonify(serialized_notifications), 200)
    elif check_user_role.role == 'seller' and check_user_role.status == "active" :
        notifications = Notification.query.filter_by(user_id=user_id).all()
        serialized_notifications = []
        for notification in notifications:
            customer = Customer.query.filter_by(id=notification.customer_id).first()

            serialized_notification = {
                'id': notification.id,
                'user_id': notification.user_id,
                'customer_id': notification.customer_id,
                'notification_type': notification.notification_type,
                'message': notification.message,
                'time_stamp': notification.time_stamp,
                'customer': {
                    'id': customer.id,
                    'Names': f'{customer.first_name} {customer.last_name}',
                    'email': customer.email,
                }
            }
            serialized_notifications.append(serialized_notification)
        return make_response(jsonify(serialized_notifications), 200)
    else:
        return make_response(jsonify({'message': 'User unauthorized'}), 401)



class Notification_update(Resource):
    # PATCH
    @jwt_required()
    
    def patch(self, id):
        user_id = get_jwt_identity()
        check_user_role = User.query.filter_by(id=user_id).first()

        if check_user_role.role == 'admin' and check_user_role.status == "active"  or check_user_role.role == 'super admin' and check_user_role.status == "active":
            data = request.json

            notification = Notification.query.filter_by(id=id).first()
            if not notification:
                return {'message': 'Notification not found'}, 404

            for key, value in data.items():
                if hasattr(notification, key):
                    setattr(notification, key, value)

            db.session.commit()
            return {'message': 'Notification updated successfully'}, 200
        elif check_user_role.role == 'seller' and check_user_role.status == "active" :
            data = request.json

            notification = Notification.query.filter_by(id=id).first()
            if notification.user_id ==user_id:
                
                for key, value in data.items():
                    if hasattr(notification, key):
                        setattr(notification, key, value)

                db.session.commit()
                return {'message': 'Notification updated successfully'}, 200
            else:
                return make_response(jsonify({'message': 'User unauthorized'}), 401)
        return {'message': 'User unauthorized'}, 401    

        

    # DELETE
    @jwt_required()
    
    def delete(self, id):
        user_id = get_jwt_identity()
        check_user_role = User.query.filter_by(id=user_id).first()

        if check_user_role.role == 'admin' and check_user_role.status == "active" or check_user_role.role == 'super admin' and check_user_role.status == "active":
            notification = Notification.query.filter_by(id=id).first()
            if not notification:
                return {'message': 'Notification not found'}, 404

            db.session.delete(notification)
            db.session.commit()
            return {'message': 'Notification deleted successfully'}, 200
        elif check_user_role.role == 'seller' and check_user_role.status == "active" :
            notification = Notification.query.filter_by(id=id).first()
            if  notification.user_id==user_id:
                
                db.session.delete(notification)
                db.session.commit()
                return {'message': 'Notification deleted successfully'}, 200
            else:
                return make_response(jsonify({'message': 'User unauthorized'}), 401)
        else:
            return make_response(jsonify({'message': 'User unauthorized'}), 401)

        






api.add_resource(CheckSession, '/checksession')
api.add_resource(AllUsers, '/users')
api.add_resource(OneUser, '/user/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(SignupUser, '/signup')
api.add_resource(inventory_update, "/inventory/<int:id>")
api.add_resource(INVENTORY, '/inventory')
api.add_resource(Importations, '/importations')
api.add_resource(UpdatePassword, '/change_password')
api.add_resource(UpdateImportation, '/importations/<int:importation_id>')
api.add_resource(Customers, '/customers')
api.add_resource(SaleResource, '/sales')
api.add_resource(SaleItemResource, '/sale/<int:sale_id>')
api.add_resource(UpdateDetails, '/updatedetails/<int:customer_id>')
api.add_resource(DeleteDetails, '/deletedetails/<int:customer_id>')
api.add_resource(AdminSales, '/sellers')
api.add_resource(OneSellerAdmin, '/seller/<int:sale_id>')
api.add_resource(Report, '/report')
api.add_resource(Report_update, '/report/<int:id>')
api.add_resource(ReceiptAll, '/receipt')
api.add_resource(Receipt_update, '/receipt/<int:id>')
api.add_resource(Notification, '/notification')
api.add_resource(Notification_update, '/notification/<int:id>')
api.add_resource(InvoiceCreate, '/invoice')
api.add_resource(InvoiceGet, '/invoice/<int:invoice_id>')
api.add_resource(InvoiceUpdate, '/updateinvoice/<int:invoice_id>')
api.add_resource(InvoiceDelete, '/deleteinvoice/<int:invoice_id>')
api.add_resource(AllInvoices, '/invoices')
api.add_resource(GeneralInvoices, '/general')
api.add_resource(AdminInvoice, '/userinvoice/<string:seller_name>')
api.add_resource(DetailCustomer, '/customer')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
