from models import User
from config import app,api
from flask_restful import Resource
from flask import request,jsonify,make_response
class AllUsers(Resource):
    def get(self):
        user = [n.serializer() for n in User.query.all()]
        
        return make_response(jsonify(user), 200)

api.add_resource(AllUsers, '/user')
if __name__ == "__main__":
    app.run(port=5555, debug=True) 