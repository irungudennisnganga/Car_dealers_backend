from models import User,Inventory
from config import app,api,db,bcrypt
from flask_restful import Resource
from flask import request,jsonify,make_response
from flask_bcrypt import check_password_hash
from flask_jwt_extended import JWTManager,create_access_token,get_jwt_identity,jwt_required


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
            access_token = create_access_token(identity=email)
            return make_response(jsonify(access_token=access_token), 200)
        
        return make_response(jsonify({"message":"Wrong password"}), 422)

class SignupUser(Resource):
    
    def post(self):
        data = request.json
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        image = data.get('image')
        contact= data.get('contact')
        email = data.get('email')
        role =data.get('role')
        password = data.get('password')
        
        if not all([first_name, last_name, image, email,contact,role, password]):
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
            _password_hash=bcrypt.generate_password_hash(password).decode('utf-8')
        )
        db.session.add(new_user)
        db.session.commit()
        
        return make_response(jsonify({'message': 'Sign up successful'}), 200)



# in this class we are getting all the users and serializering each user using list comprehension
class AllUsers(Resource):
    # @jwt_required()
    def get(self):
        user = [n.serializer() for n in User.query.all()]
        
        # if no user is found the method will stop there and return "No users found"
        if not user:
            return {"message":"No users found"}
        
        return make_response(jsonify(user), 200)

# in this function we are getting a specific user by their id 
class OneUser(Resource):
    # @jwt_required()
    def get(self,id):
        # here one is quering all the users available filtering them by their id's, after getting the first user, we serialize the user
        # using the serializer() function found in the models  
        user = User.query.filter_by(id = id).first().serializer()
        
        # if no user is found the method will stop there and return "No users found"
        if not user:
            return {"message":"No user found"}
        #  after getting a user we jsonify the data received 
        response = make_response(
            jsonify(user),
            200
        )
        
        return response
    
# inventory

class INVENTORY(Resource): 
    # POST
    def post(self):
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
            user_id=data.get('user_id')
        )
        db.session.add(new_inventory_item)
        db.session.commit()
        return make_response (jsonify({'message': 'Inventory created successfully'}), 201)
    
    # GET
    
    def get(self,id=None):
        if id:
            inventory_item = Inventory.query.filter_by(id=id).first()
            if inventory_item:
                return make_response (jsonify(inventory_item.serializer()))
            return {'message': 'Inventory item not found'}, 404
        else:
            items = Inventory.query.all()
            return make_response (jsonify([item.serializer()for item in items]))
        
        # PATCH
        

class inventory_update(Resource):
    def patch(self,id):
        inventory_item = Inventory.query.filter_by(id=id).first()
        if inventory_item:
            data = request.json
            for key, value in data.items():
                if hasattr(inventory_item,key):
                    setattr(inventory_item,key,value)

                db.session.commit()
                return {'message':"Inventory item updated successfully"},200
            return {'meaage':'Inventory item not found'}, 404
        
        # DELETE
        
    def delete(self,id):
        inventory_item = Inventory.query.filter_by(id=id).first()
        if inventory_item:
            db.session.delete(inventory_item)
            db.session.commit()
            
            return{'message': 'Inventory item deleted successfully'}, 200
        return {'message': "Inventory item not found"}, 404



    

api.add_resource(AllUsers, '/user')
api.add_resource(OneUser, '/user/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(SignupUser, '/signup')
api.add_resource(inventory_update,"/inventory/<int:id>")
api.add_resource(INVENTORY, '/inventory')




if __name__ == "__main__":
    app.run(port=5555, debug=True) 