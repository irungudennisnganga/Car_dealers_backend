from models import User, Inventory, Importation
from config import app, api, db, bcrypt
from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_bcrypt import check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required


class CheckSession(Resource):
    @jwt_required() 
    def get(self):
        user_id = get_jwt_identity()
        
        user= User.query.filter_by(id=user_id).first()
        
        if  not user :
            return {"message":"user not found"}
        
        user_data = {
            "user_id":user.id,
            "first_name":user.first_name,
            "last_name":user.last_name,
            "user_email":user.email,
            "contact":user.contact,
            "role":user.role,
            "image":user.image,
            
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
            return make_response(jsonify(access_token=access_token), 200)

        return make_response(jsonify({"message": "Wrong password"}), 422)


class SignupUser(Resource):

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        
        check_user_role= User.query.filter_by(id=user_id).first()
        
        if check_user_role.role == 'admin':
        
            data = request.json
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            image = data.get('image')
            contact = data.get('contact')
            email = data.get('email')
            role = 'seller'
            password = data.get('password')

            if not all([first_name, last_name, image, email, contact, role, password]):
                return make_response(jsonify({'errors': ['Missing required data']}), 400)

            if User.query.filter_by(email=email).first():
                return make_response(jsonify({'message': 'User already exists'}), 400)

            new_user = User(
                first_name=first_name,
                last_name=last_name,
                image=image,
                email=email,
                contact=contact,
                role=role,
                _password_hash=bcrypt.generate_password_hash(
                    password).decode('utf-8')
            )
            db.session.add(new_user)
            db.session.commit()

            return make_response(jsonify({'message': 'Sign up successful'}), 200)

        if check_user_role.role =='super admin':
            data = request.json
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            image = data.get('image')
            contact = data.get('contact')
            email = data.get('email')
            role = data.get('role')
            password = data.get('password')

            if not all([first_name, last_name, image, email, contact, role, password]):
                return make_response(jsonify({'errors': ['Missing required data']}), 400)

            if User.query.filter_by(email=email).first():
                return make_response(jsonify({'message': 'User already exists'}), 400)

            new_user = User(
                first_name=first_name,
                last_name=last_name,
                image=image,
                email=email,
                contact=contact,
                role=role,
                _password_hash=bcrypt.generate_password_hash(
                    password).decode('utf-8')
            )
            db.session.add(new_user)
            db.session.commit()

            return make_response(jsonify({'message': 'Sign up successful'}), 200)
# in this class we are getting all the users and serializering each user using list comprehension
class AllUsers(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        
        check_user_role= User.query.filter_by(id=user_id).first()
        
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
class UserAccount(Resource):
    @jwt_required()
    def get(self):
        user_id =get_jwt_identity()

        user = User.query.filter_by(id=user_id).first()
        
        user_data = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'image': user.image,
                'email': user.email,
                'role': user.role,
                'contact': user.contact,
            }
        
        return make_response(
            jsonify(user_data),
            200
        )


class OneUser(Resource):
    @jwt_required()
    
    def get(self, id):
        user_id = get_jwt_identity()
        
        check_user_role= User.query.filter_by(id=user_id).first()
        
        
        if check_user_role.role == "admin":
        # here one is quering all the users available filtering them by their id's, after getting the first user, we serialize the user
        # using the serializer() function found in the models
            user = User.query.filter_by(id=id , role='seller').first()

        if check_user_role.role == "super admin":
       
            user = User.query.filter_by(id=id).first()
        # if no user is found the method will stop there and return "No users found"
        if not user:
            return {"message": "No user found"}
        
        user_data = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'image': user.image,
                'email': user.email,
                'role': user.role,
                'contact': user.contact,
            }

        #  after getting a user we jsonify the data received
        response = make_response(
            jsonify(user_data),
            200
        )

        return response
    @jwt_required()
    def patch(self, id):
        user_id = get_jwt_identity()
        
        check_user_role= User.query.filter_by(id=user_id).first()
        
        # Get the JSON data from the request
        data = request.json
        
        # Querying the user by their id
        user = User.query.filter_by(id=id).first()
        
        # If no user is found, return an error response
        if not user:
            return make_response(jsonify({"message": "No user to update"}), 404)
        
        if check_user_role.role == "admin" :
            # try:
                # Update user attributes if they are provided in the JSON data
            if 'first_name' in data:
                user.first_name = data.get('first_name')
            if 'last_name' in data:
                user.last_name = data.get('last_name')
            if 'image' in data:
                user.image = data.get('image')
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
        if check_user_role.role == "super_admin":
            if 'first_name' in data:
                user.first_name = data.get('first_name')
            if 'last_name' in data:
                user.last_name = data.get('last_name')
            if 'image' in data:
                user.image = data.get('image')
            if 'email' in data:
                user.email = data.get('email')
            if 'contact' in data:
                user.contact = data.get('contact')
            if 'role' in data:
                user.role = data.get('role')

            db.session.commit()
            
            # Return a success response
            return make_response(jsonify({'message': 'User updated successfully'}), 200)
        
# inventory


class INVENTORY(Resource):
    # POST
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        
        # check_user_role= User.query.filter_by(id=user_id).first()
        data = request.json
        new_inventory_item = Inventory(
            make=data.get('make'),
            image=data.get('image'),
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
            gallery=data.get('gallery'),
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
        return make_response(jsonify({'message': 'Inventory created successfully'}), 201)

    # GET
    @jwt_required()
    def get(self):
        
        items = Inventory.query.all()
        return make_response(jsonify([ {
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
                'gallery': item.gallery,
                'condition': item.condition,
                'availability': item.availability,
                'cylinder': item.cylinder,
                'doors': item.doors,
                'features': item.features,
                'stock_number': item.stock_number,
                'purchase_cost': item.purchase_cost,
                'profit': item.profit,
                
            }for item in items]))

        # PATCH


class inventory_update(Resource):
    @jwt_required()
    
    def patch(self, id):
        user_id = get_jwt_identity()
        
        check_user_role= User.query.filter_by(id=user_id).first()
        
        inventory_item = Inventory.query.filter_by(id=id).first()
        if check_user_role.role =='admin' or check_user_role.role =='super admin':
            if inventory_item:
                data = request.json
                for key, value in data.items():
                    if hasattr(inventory_item, key):
                        setattr(inventory_item, key, value)

                    db.session.commit()
                    return {'message': "Inventory item updated successfully"}, 200
                return {'meaage': 'Inventory item not found'}, 404
        else:
            return {'message': "User has no access rights to update Inventory"}, 422
            

        # DELETE
    @jwt_required()
    def delete(self, id):
        user_id = get_jwt_identity()
        
        check_user_role= User.query.filter_by(id=user_id).first()
        if check_user_role.role == 'super admin' or check_user_role.role == 'admin' :
            inventory_item = Inventory.query.filter_by(id=id).first()
            if inventory_item:
                db.session.delete(inventory_item)
                db.session.commit()

                return {'message': 'Inventory item deleted successfully'}, 200
        else:
            return {'message': 'User has no access rights to delete'}, 422
        return {'message': "Inventory item not found"}, 404


class Importations(Resource):
    # @jwt_required()
    def get(self):
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
                'car_id': importation.car_id
            })
        return make_response(jsonify(importations_data), 200)

class AddImportation(Resource):
    # @jwt_required()
    def post(self):
        data = request.json
        new_importation = Importation(
            country_of_origin=data['country_of_origin'],
            transport_fee=data['transport_fee'],
            currency=data['currency'],
            import_duty=data['import_duty'],
            import_date=data['import_date'],
            import_document=data['import_document'],
            car_id=data['car_id']
        )
        db.session.add(new_importation)
        db.session.commit()
        return make_response(jsonify({'message': 'Importation created successfully'}), 201)

class UpdateImportation(Resource):
    # @jwt_required()
    def put(self, importation_id):
        data = request.json
        importation = Importation.query.get(importation_id)
        if not importation:
            return make_response(jsonify({'message': 'Importation not found'}), 404)
        importation.country_of_origin = data.get('country_of_origin', importation.country_of_origin)
        importation.transport_fee = data.get('transport_fee', importation.transport_fee)
        importation.currency = data.get('currency', importation.currency)
        importation.import_duty = data.get('import_duty', importation.import_duty)
        importation.import_date = data.get('import_date', importation.import_date)
        importation.import_document = data.get('import_document', importation.import_document)
        importation.car_id = data.get('car_id', importation.car_id)
        db.session.commit()
        return make_response(jsonify({'message': 'Importation updated successfully'}), 200)

class DeleteImportation(Resource):
    # @jwt_required()
    def delete(self, importation_id):
        importation = Importation.query.get(importation_id)
        if not importation:
            return make_response(jsonify({'message': 'Importation not found'}), 404)
        db.session.delete(importation)
        db.session.commit()
        return make_response(jsonify({'message': 'Importation deleted successfully'}), 200)



api.add_resource(AllUsers, '/users')
api.add_resource(OneUser, '/user/<int:id>')
api.add_resource(UserAccount, '/me')
api.add_resource(Login, '/login')
api.add_resource(SignupUser, '/signup')
api.add_resource(inventory_update, "/inventory/<int:id>")
api.add_resource(INVENTORY, '/inventory')
api.add_resource(Importations, '/importations')
api.add_resource(AddImportation, '/importations/add')
api.add_resource(UpdateImportation, '/importations/update/<int:importation_id>')
api.add_resource(DeleteImportation, '/importations/delete/<int:importation_id>')



if __name__ == "__main__":
    app.run(port=5555, debug=True)
