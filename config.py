from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt



app = Flask(__name__) #instanciate a flask application 
 

app.secret_key = b'\xc2A\x1c\xc6\xc5QvJ?ZH$\x13\\4\xb0'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'ce81d8454bd966ba09bbbdf723f632fd'


# app.json.compact = False
jwt  = JWTManager(app)


# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Enable CORS
CORS(app)

# Initialize API
api = Api(app)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
