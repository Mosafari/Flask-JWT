# import flask
import uuid # for public id
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, make_response
from  werkzeug.security import generate_password_hash, check_password_hash
# imports for PyJWT authentication
import jwt
from functools import wraps
from datetime import datetime, timedelta

# creates Flask object
app = Flask(__name__)
# configuration
app.config['SECRET_KEY'] = 'your secret key'
# database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# creates SQLALCHEMY object
db = SQLAlchemy(app)

# Database ORMs
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique = True)
    password = db.Column(db.String(80))
    # Coupon validators
    coupon = db.Column(db.String(10))
    

# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'X-Access-Token' in request.headers:
            token = request.headers['X-Access-Token']
            print(token,type(token))
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query\
                .filter_by(public_id = data['public_id'])\
                .first()
        except Exception as e:
            return jsonify({
                'error' : f'{e}',
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated

# User Database Route
# this route sends back data of current logged in users
@app.route('/user', methods =['GET'])
@token_required
def get_users_data(current_user):
    # querying the database
    # for all the entries in it

    # converting the query objects
    # to list of jsons
    output = []
    
    if current_user.coupon:
        validate = "Successfull"
    else :
        validate = "no coupon found"
    # appending the user data json
    # to the response list
    output.append({
        'public_id': current_user.public_id,
        'name' : current_user.name,
        'coupon' : validate
    })
  
    return jsonify({f"{current_user}" : output})

# route for logging user in
@app.route('/login', methods =['POST'])
def login():
    # creates dictionary of form data
    auth = request.form
  
    if not auth or not auth.get('email') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
        )
    # checking for existing user
    user = User.query\
        .filter_by(email = auth.get('email'))\
        .first()
  
    if not user:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
        )
  
    if check_password_hash(user.password, auth.get('password')):
        # generates the JWT Token
        token = jwt.encode({
            'public_id': user.public_id,
            'exp' : datetime.now() + timedelta(minutes = 30)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        print(token,type(token))
        return make_response(jsonify({'token' : token}), 201) #.decode('UTF-8')
    # returns 403 if password is wrong
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
    )
    
    # signup route
@app.route('/signup', methods =['POST'])
def signup():
    # creates a dictionary of the form data
    data = request.form
    # gets name, email and password
    name, email = data.get('name'), data.get('email')
    password = data.get('password')
  
    # checking for existing user
    user = User.query\
        .filter_by(email = email)\
        .first()
    if not user:
        # database ORM object
        user = User(
            public_id = str(uuid.uuid4()),
            name = name,
            email = email,
            password = generate_password_hash(password)
        )
        # insert user
        db.session.add(user)
        db.session.commit()
  
        return make_response('Successfully registered.', 201)
    else:
        # returns 202 if user already exists
        return make_response('User already exists. Please Log in.', 202)


# getting users coupons and checking if are valid
@app.route('/coupon', methods =['POST'])
@token_required
def coupon_validator(current_user):
    coupon = None
    # checking for coupon in header
    if 'coupon' in request.form:
        coupon = request.form['coupon']
    # return 401 if token is not passed
    if not coupon:
        return jsonify({'message' : 'coupon is missing !!'}), 401

    try:
        print(coupon)
        if coupon[0] == 'x' and coupon[-1] == 'Q':
            covalue = sum([ord(i) for i in coupon])
            if 396 <= covalue <= 399 :
                print("Value of Coupon : ", covalue)
                # checking for existing coupon
                expierdcoupon = User.query\
                    .filter_by(coupon = coupon)\
                    .first()
                if not expierdcoupon:
                    # update records ,database ORM object
                    user = User.query.filter_by(name=current_user.name).first()
                    user.coupon = coupon
                    db.session.commit()
                else :
                    return make_response('Coupon already exists. ', 202)
                return make_response('Coupon Successfully registered.', 201)
            else:
                raise Exception
        else :
            raise Exception
    except:
        return jsonify({
            'message' : 'coupon is invalid !!'
        }), 401
        

if __name__ == "__main__":
    # setting debug to True enables hot reload
    # and also provides a debugger shell
    # if you hit an error while running the server
    app.run(debug = True)