from models import User, Inventory, Importation, Customer, GalleryImage, Sale, Invoice
from config import app, api, db, bcrypt
from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import cloudinary
import cloudinary.uploader
import cloudinary.api
from datetime import datetime


cloudinary.config(
    cloud_name='df3sytxef',
    api_key='985443855749731',
    api_secret='lo3vNIHKIgq9R6CZOdcAcQAUKjA'
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
            return make_response(jsonify(access_token=access_token, expires_in=28800), 200)

        return make_response(jsonify({"message": "Wrong password"}), 422)


class SignupUser(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        check_user_role = User.query.filter_by(id=user_id).first()

        if check_user_role.role not in ['admin', 'super admin']:
            return make_response(jsonify({'message': 'Unauthorized'}), 401)

        data = request.form
        first_name = data.get('firstname')
        last_name = data.get('lastname')
        image_file = request.files.get('image')
        contact = data.get('contact')
        email = data.get('email')
        role = data.get(
            'role') if check_user_role.role == 'super admin' else 'seller'
        password = '8Dn@3pQo'

        if not all([first_name, last_name, image_file, email, contact, role]):
            return make_response(jsonify({'error': ['Missing required data']}), 400)

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
            role=role,
            _password_hash=bcrypt.generate_password_hash(
                password).decode('utf-8')
        )
        db.session.add(new_user)
        db.session.commit()

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
            } for n in User.query.all()]

            return user

        return make_response(jsonify(user), 200)

# in this function we are getting a specific user by their id


class OneUser(Resource):
    @jwt_required()
    def get(self, id):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()
        
        if check_user_role.role == "admin" or  check_user_role.role == "seller"  :
            user = User.query.filter_by(id=id, role='seller').first()
        elif check_user_role.role == "super admin":
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
        if check_user_role.role == 'super admin':
            user = User.query.filter_by(id=id).first()

        elif check_user_role.role == 'admin':
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

            # if 'email' in data:
            #     user.email = data.get('email')
            if 'contact' in data:
                user.contact = data.get('contact')
            if 'role' in data:
                user.role = data.get('role')

            # Commit the changes to the database
            db.session.commit()

            # Return a success response
            return make_response(jsonify({'message': 'User updated successfully'}), 200)

        if check_user_role.role == "admin" or check_user_role.role == "seller":
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
        # Changed to getlist to handle multiple files
        gallery = request.files.getlist('gallery')

        if image.filename == '' or len(gallery) == 0:
            return {'error': 'No image selected for upload'}, 400

        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

        if not allowed_file(image.filename) or not all(allowed_file(g.filename) for g in gallery):
            return {'error': 'Invalid file type. Only images are allowed'}, 400

        # Upload images to Cloudinary
        try:
            image_upload_result = cloudinary.uploader.upload(image)
            gallery_upload_results = [
                cloudinary.uploader.upload(g) for g in gallery]
        except Exception as e:
            return {'error': f'Error uploading image: {str(e)}'}, 500

        if check_user_role.role == 'admin' or check_user_role.role == 'super admin':
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

            # Add new inventory item to session
            db.session.add(new_inventory_item)
            db.session.commit()

            db.session.refresh(new_inventory_item)  # Refresh to get the ID
            last_item = Inventory.query.order_by(Inventory.id.desc()).first()
            # print(last_item)

            # Add gallery images
            for result in gallery_upload_results:
                gallery_image = GalleryImage(
                    url=result['secure_url'], inventory_id=last_item.id)  # Use last_item.id
                db.session.add(gallery_image)

            db.session.commit()

            return make_response(jsonify({'message': 'Inventory created successfully'}), 201)
        else:
            return make_response(jsonify({'message': 'User has no access rights to create a Car'}), 401)

    # GET
    @jwt_required()
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

        if check_user_role.role == 'admin' or check_user_role.role == 'super admin':
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
        if check_user_role.role == 'super admin' or check_user_role.role == 'admin':
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

        if check_user_role.role == 'super admin' or check_user_role.role == 'admin' or check_user_role.role == 'seller':
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
        if check_user_role.role == 'super admin' or check_user_role.role == 'admin':
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
        if check_user_role.role == 'super admin' or check_user_role.role == 'admin':
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
        if check_user_role.role == 'super admin' or check_user_role.role == 'admin':
            importation = Importation.query.get(importation_id)
            if not importation:
                return make_response(jsonify({'message': 'Importation not found'}), 404)
            db.session.delete(importation)
            db.session.commit()
            return make_response(jsonify({'message': 'Importation deleted successfully'}), 200)
        else:
            return make_response(jsonify({"message": "Unauthorized User"}), 404)

class CustomerDetails(Resource):
    @jwt_required()
    def get(self):
        # Get the current user's ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Retrieve only the customers associated with the current seller (user)
        customers = [{
            "first_name": customer.first_name,
            'last_name': customer.last_name,
            'email': customer.email,
            'address': customer.address,
            'phone_number': customer.phone_number,
            'image_file': customer.image
        } for customer in Customer.query.filter_by(seller_id=current_user_id).all()]

        return make_response(jsonify(customers), 200)
    
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
        if check_user_role.role == 'seller':
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

        if check_user_role.role == 'seller':
            serialized_sales = []
            for sale in Sale.query.all():
                customer = Customer.query.filter_by(id=sale.customer_id).first()
                seller = User.query.filter_by(id=sale.seller_id).first()
                inventory =Inventory.query.filter_by(id =sale.inventory_id).first()
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
                                 "id":inventory.id,
                                 "name":inventory.make
                                 },
                    "promotions": sale.promotions,
                }
                serialized_sales.append(serialized_sale)
            return make_response(jsonify(serialized_sales), 200)
        else:
            return make_response(jsonify({"message":"User unauthorized"}), 401)

class SaleItemResource(Resource):
    # GET
    @jwt_required()
    def get(self, sale_id):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()

        if not check_user_role.role == 'seller':
            return make_response(jsonify({"message": "Unauthorized"}), 401)

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
                                 "name":inventory.make
                                 },
            "promotions": sale.promotions,
        }
        return make_response(jsonify(one_sale), 200)

    # PUT
    @jwt_required()
    def put(self, sale_id):
        user_id = get_jwt_identity()

        # Get the sale object
        sale = Sale.query.filter_by(id=sale_id).first()

        # Check if the logged-in user is the seller who created the sale
        # if sale.seller_id != user_id:
        #     return make_response(jsonify({"message": "Unauthorized"}), 401)

        # Get the request data
        data = request.get_json()

        
        if 'status' in data:
            sale.status = data['status']
        
        # Commit the changes to the database
        db.session.commit()

        return make_response(jsonify({'message': 'Sale updated successfully'}))

    # DELETE
    def delete(self, sale_id):
        sale = Sale.query.get_or_404(sale_id)
        db.session.delete(sale)
        db.session.commit()

        return jsonify({'message': 'Sale deleted successfully'})
    
class AdminSales(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()

        if check_user_role.role == 'admin' or check_user_role.role == 'super admin':
            serialized_sales = []
            for sale in Sale.query.all():
                customer = Customer.query.filter_by(id=sale.customer_id).first()
                seller = User.query.filter_by(id=sale.seller_id).first()
                inventory =Inventory.query.filter_by(id =sale.inventory_id).first()
                serialized_sale = {
                    "id":sale.id,
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
                serialized_sales.append(serialized_sale)
            return make_response(jsonify(serialized_sales), 200)
        else:
            return make_response(jsonify({"message":"User unauthorized"}), 401)
        
class OneSellerAdmin(Resource):
    @jwt_required()
    def get(self, sale_id):
        user_id = get_jwt_identity()

        check_user_role = User.query.filter_by(id=user_id).first()

        if check_user_role.role == 'admin' or check_user_role.role == 'super admin':
            
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
                                 "name":inventory.make
                                 },
                "promotions": sale.promotions,
            }
            return make_response(jsonify(one_sale), 200)
        else:
            return make_response(jsonify({"message":"User unauthorized"}), 401)    
        
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
                date_of_purchase=datetime.datetime.strptime(data['date_of_purchase'], "%Y-%m-%d"),
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
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now()
            )
            db.session.add(new_invoice)
            db.session.commit()
            return make_response(jsonify({'message': 'Invoice created successfully', 'invoice_id': new_invoice.id}), 201)
        except Exception as e:
            return make_response(jsonify({'message': 'Failed to create invoice', 'error': str(e)}), 500)

class InvoiceGet(Resource):
    @jwt_required()
    def get(self, invoice_id):
        invoice = Invoice.query.get(invoice_id)
        if invoice:
            invoice_data = {
                'id': invoice.id,
                'date_of_purchase': invoice.date_of_purchase,
                'method': invoice.method,
                'amount_paid': invoice.amount_paid,
                'fee': invoice.fee,
                'tax': invoice.tax,
                'currency': invoice.currency,
                'seller_id': invoice.seller_id,
                'customer_id': invoice.customer_id,
                'vehicle_id': invoice.vehicle_id,
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
                'created_at': invoice.created_at.isoformat() if invoice.created_at else None,
                'updated_at': invoice.updated_at.isoformat() if invoice.updated_at else None,
               
            }
            return jsonify(invoice_data)
        else:
            return make_response(jsonify({'message': 'Invoice not found'}), 404)
class InvoiceUpdate(Resource):
    @jwt_required()
    def put(self, invoice_id):
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return make_response(jsonify({'message': 'Invoice not found'}), 404)
        
        data = request.get_json()
        for key, value in data.items():
            if hasattr(invoice, key):
                setattr(invoice, key, value)
        
        db.session.commit()
        return make_response(jsonify({'message': 'Invoice updated successfully'}), 200)
    
class InvoiceDelete(Resource):
    @jwt_required()
    def delete(self, invoice_id):
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return make_response(jsonify({'message': 'Invoice not found'}), 404)
        
        db.session.delete(invoice)
        db.session.commit()
        return make_response(jsonify({'message': 'Invoice deleted successfully'}), 200)




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
api.add_resource(CustomerDetails, '/customerdetails')
api.add_resource(SaleResource, '/sales')
api.add_resource(SaleItemResource, '/sale/<int:sale_id>')
api.add_resource(UpdateDetails, '/updatedetails/<int:customer_id>')
api.add_resource(DeleteDetails, '/deletedetails/<int:customer_id>')
api.add_resource(AdminSales, '/sellers')
api.add_resource(OneSellerAdmin, '/seller/<int:sale_id>')
api.add_resource(InvoiceCreate, '/invoice')
api.add_resource(InvoiceGet, '/invoice/<int:invoice_id>')
api.add_resource(InvoiceUpdate, '/updateinvoice/<int:invoice_id>')
api.add_resource(InvoiceDelete, '/deleteinvoice/<int:invoice_id>')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
