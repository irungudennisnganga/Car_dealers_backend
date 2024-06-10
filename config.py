from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager,create_access_token,get_jwt_identity,jwt_required
from flask_bcrypt import Bcrypt
from datetime import timedelta
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__) #instanciate a flask application 


app.secret_key = b'\xc2A\x1c\xc6\xc5QvJ?ZH$\x13\\4\xb0'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'ce81d8454bd966ba09bbbdf723f632fd'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=500)

# app.json.compact = False
jwt  = JWTManager(app)


limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)
# Initialize extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
# jwt = JWTManager(app)

# Enable CORS
CORS(app)

# Initialize API
api = Api(app)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
