<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Car_dealers_backend](#car_dealers_backend)
  - [Introduction](#introduction)
  - [ROUTE MANAGEMENT](#route-management)
    - [<b>1. CheckSession Class</b>](#b1-checksession-classb)
      - [Sample JSON Response](#sample-json-response)
      - [Example Usage](#example-usage)
    - [<b>2. Login Class</b>](#b2-login-classb)
    - [Sample JSON Request](#sample-json-request)
    - [Sample JSON Response](#sample-json-response-1)
    - [Example Usage](#example-usage-1)
    - [<b>3. SignupUser Class</b>](#b3-signupuser-classb)
    - [Sample JSON Response](#sample-json-response-2)
    - [Example Usage](#example-usage-2)
    - [<b>4. UpdatePassword Class</b>](#b4-updatepassword-classb)
    - [Sample JSON Request](#sample-json-request-1)
    - [Sample JSON Response](#sample-json-response-3)
    - [Example Usage](#example-usage-3)
    - [<b>5. AllUsers Class</b>](#b5-allusers-classb)
    - [Example Usage](#example-usage-4)
    - [<b>6. OneUser Class</b>](#b6-oneuser-classb)
      - [get Method](#get-method)
    - [Sample JSON Response](#sample-json-response-4)
      - [put Method](#put-method)
      - [Sample JSON Request (Form Data)](#sample-json-request-form-data)
    - [Sample JSON Response](#sample-json-response-5)
    - [Example Usage](#example-usage-5)
      - [GET Request](#get-request)
      - [PUT Request](#put-request)
    - [<b>7. INVENTORY Class</b>](#b7-inventory-classb)
      - [post Method](#post-method)
      - [Sample JSON Request (Form Data)](#sample-json-request-form-data-1)
    - [Sample JSON Response](#sample-json-response-6)
      - [get Method](#get-method-1)
    - [Sample JSON Response](#sample-json-response-7)
    - [Example Usage](#example-usage-6)
      - [POST Request](#post-request)
      - [GET Request](#get-request-1)
    - [Inventory Update and Deletion](#inventory-update-and-deletion)
    - [Steps:](#steps)
      - [Steps:](#steps-1)
    - [Importations](#importations)
      - [Steps:](#steps-2)
    - [Update and Delete Importation API](#update-and-delete-importation-api)
      - [Steps:](#steps-3)
      - [Steps:](#steps-4)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Cardealership Management System Back-End 

## Introduction

This project is based on making cardealership management easier and more secure amongest cardealership owner,
seller of the cars and their customers.

Key features include:

- At the top of the heirachy there is a super admin and admin who see's everything that is running throught the whole system that is:

    1. Having a view on all sales, custmomer, invoices and receipts.
    2. They are incharge of adding an admin and a seller.
    3. Add inventory and its details.

- Followed is the seller who is the one providing data to the admins and super admins

    1. Add customer
    2. Creates a sale, invoice and receipt




This documentation is made for (Dennis Irungu) and other developers to have the whole idea of the
do and dont's of my API, the things that are provided by the API, the endpoints, data type that are
supported at the server and the relationship between all the models and how they work.

## Installation

To clone this repostory use this  [ssh link](git@github.com:irungudennisnganga/Car_dealers_backend.git) or [https](https://github.com/irungudennisnganga/Car_dealers_backend.git) and run this command on your terminal

```bash
    git clone https://github.com/irungudennisnganga/Car_dealers_backend.git
```

To install the dependecy required to run the project.

First create a python environment using this command

```bash
    pipenv install
```

This command will install all the required the packages which are used to run to program.

```bash
    pipenv shell
```

``` bash
    python app.py
```

This command above will start the backend server

## ROUTE MANAGEMENT

### <b>1. CheckSession Class</b> 

    The CheckSession class is a resource in a Flask RESTful API that handles the verification and retrieval of the current user's session information. It requires the user to be authenticated using JSON Web Tokens (JWT).
    
    @jwt_required()

    The jwt_required() decorator ensures that the endpoint can only be accessed by authenticated users with a valid JWT. If the user does not provide a valid token, they will receive an authorization error.
    get Method

    The get method is responsible for retrieving the details of the currently authenticated user. Here’s how it works:

    1. Retrieve User ID: It calls get_jwt_identity() to get the user ID from the JWT. This function extracts the identity (user ID) that was stored in the token when it was created.

    2. Fetch User from Database: It queries the User model to find the user with the corresponding ID using User.query.filter_by(id=user_id).first(). If no user is found with that ID, it returns a message indicating that the user was not found.

    3. Prepare User Data: If the user is found, it constructs a dictionary named user_data containing the user's details:

    - user_id: The user's ID
    - first_name: The user's first name
    - last_name: The user's last name
    - user_email: The user's email address
    - contact: The user's contact information
    - role: The user's role
    - image: The URL or path to the user's profile image
    - status: The user's status

    4. Return Response: It returns a JSON response containing the user_data dictionary with a 200 HTTP status code, indicating a successful request.

#### Sample JSON Response

    { 
        "user_id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "user_email": "john.doe@example.com",
        "contact": "+1234567890",
        "role": "admin",
        "image": "http://example.com/image.jpg",
        "status": "active"
    }

#### Example Usage
    To use this endpoint, the client must include a valid JWT in the Authorization header of the request:

    GET /check_session
    Authorization: Bearer <your_jwt_token>

    If the token is valid, the server responds with the authenticated user's information. If the token is missing or invalid, the server responds with an authorization error.
### <b>2. Login Class</b> 

    The Login class is a resource in a Flask RESTful API that handles user authentication. It validates user credentials and generates a JWT access token upon successful authentication.

    The Login class is a resource in a Flask RESTful API that handles user authentication. It validates user credentials and generates a JWT access token upon successful authentication.

    1. Extract Email and Password: It retrieves the email and password from the JSON body of the request using request.json.get("email") and request.json.get("password").

    2. Validate Input: It checks if the email and password are provided. If either is missing, it returns a 401 HTTP status code with a message indicating "Bad Email or password".

    3. Fetch User from Database: It queries the User model to find a user with the provided email using User.query.filter_by(email=email).first(). If no user is found, it returns a 401 HTTP status code with a message indicating "Wrong credentials".

    4. Check Password: It verifies the provided password against the stored password hash using check_password_hash(user._password_hash, password). If the password is incorrect, it returns a 406 HTTP status code with a message indicating "Wrong password".

    5. Generate Access Token: If the password is correct, it generates a JWT access token using create_access_token(identity=user.id) and signs the jwt using the user id.

    6. Send Email Notification: It sends an email notification to the user indicating a successful login (uncomment the send_email function call as needed).

    7. Update User Status: It sets the user's status to "active" and commits the changes to the database using db.session.commit().

    8. Return Response: It returns a JSON response containing the access_token with a 200 HTTP status code, indicating a successful login.

### Sample JSON Request

    {
        "email": "john.doe@example.com",
        "password": "yourpassword"
    }

### Sample JSON Response

    {
        "access_token": "your_jwt_token"
    }

### Example Usage

    POST /login
    Content-Type: application/json

    {
        "email": "john.doe@example.com",
        "password": "yourpassword"
    }

    If the credentials are correct, the server responds with a JWT access token. If the credentials are incorrect or missing, the server responds with an appropriate error message and status code.

### <b>3. SignupUser Class</b>

    The SignupUser class is a resource in a Flask RESTful API that handles the user sign-up process. It requires the user to be authenticated with a JSON Web Token (JWT) and only allows users with certain roles to create new users.

    @jwt_required()

    The jwt_required() decorator ensures that the endpoint can only be accessed by authenticated users with a valid JWT. If the user does not provide a valid token, they will receive an authorization error.

    The post method is responsible for processing sign-up requests. Here’s how it works:

    1. Retrieve User ID and Role: It calls get_jwt_identity() to get the user ID from the JWT and queries the User model to get the current user's role and status using User.query.filter_by(id=user_id).first().

    2. Check User Authorization: It checks if the current user's role is either 'admin' or 'super admin' and that their status is 'active'. If the user is not authorized, it returns a 401 HTTP status code with a message indicating "Unauthorized".

    3. Extract Form Data: It retrieves the form data from the request using request.form and request.files:

        - first_name: The first name of the new user.
        - last_name: The last name of the new user.
        - image_file: The profile image of the new user.
        - contact: The contact information of the new user.
        - email: The email address of the new user.
        - role: The role of the new user (default is 'seller' unless the current user is 'super admin').
        - password: A default password is set for the new user ('8Dn@3pQo').
    
    4. Validate Input: It checks if all required fields are provided and if an image file is uploaded. If any required data is missing, it returns a 406 HTTP status code with a message indicating "Missing required data".

    5. Check for Existing User: It checks if a user with the same email or contact information already exists in the database. If such a user exists, it returns a 400 HTTP status code with a message indicating "User already exists".

    6. Validate Image File: It checks if the uploaded file is a valid image format. If the file is invalid, it returns a 400 HTTP status code with an appropriate error message.

    7. Upload Image: It uploads the image file to Cloudinary and handles any potential upload errors.

    8. Create New User: It creates a new User object with the provided details, including the uploaded image URL, and adds it to the database. The user's password is hashed before storing.

    9. Send Email Notification: It sends an email notification to the new user with their login details .

    10. Return Response: It returns a JSON response with a 200 HTTP status code, indicating that the sign-up was successful.

### Sample JSON Response

    {
    "message": "Sign up successful"
    }

### Example Usage

    To use this endpoint, the client must send a POST request with the user's details in the form data and an image file in the request files:

    POST /signup
    Authorization: Bearer <your_jwt_token>
    Content-Type: multipart/form-data

    {
        "first_name": "Jane",
        "last_name": "Doe",
        "contact": "+1234567890",
        "email": "jane.doe@example.com",
        "role": "seller" (or other role, if user is 'super admin')
        "image": <image_file>
    }

    If the request is valid and the user is authorized, the server responds with a success message. If there are any issues with the request, the server responds with an appropriate error message and status code.

### <b>4. UpdatePassword Class</b>

    The UpdatePassword class is a resource in a Flask RESTful API that handles updating a user's password.

    The post method is responsible for processing requests to update a user's password. Here’s how it works:

    1. Extract Request Data: It retrieves the JSON data from the request body using request.json, including the user's email, former password, and new password.

    2. Validate Input: It checks if the required fields (email, former password, and new password) are provided. If any of these fields are missing, it returns a 400 HTTP status code with a message indicating "Email, former password, and new password are required."

    3. Fetch User from Database: It queries the User model to find the user with the provided email using User.query.filter_by(email=user_email).first(). If no user is found with that email, it returns a 404 HTTP status code with a message indicating "User not found".

    4. Check Former Password: It verifies the provided former password against the stored password hash using check_password_hash(user.password_hash, former_password). If the former password is incorrect, it returns a 401 HTTP status code with a message indicating "Incorrect former password".

    5. Update Password: If the former password is correct, it generates a new password hash for the new password using generate_password_hash(new_password).decode('utf-8') and updates the user's password hash in the database.

    6. Commit Changes: It commits the changes to the database.

    7. Send Email Notification: It sends an email notification to the user indicating that their password has been successfully updated.

    8. Return Response: It returns a JSON response with a 200 HTTP status code, indicating that the password was updated successfully.

### Sample JSON Request

    {
        "email": "john.doe@example.com",
        "former_password": "oldpassword",
        "new_password": "newpassword"
    }

### Sample JSON Response

    {
        "message": "Password updated successfully"
    }

### Example Usage

    To use this endpoint, the client must send a POST request with the user's email, former password, and new password in the JSON body:

    POST /update_password
    Content-Type: application/json

    {
        "email": "john.doe@example.com",
        "former_password": "oldpassword",
        "new_password": "newpassword"
    }

    If the request is valid and the former password is correct, the server responds with a success message. If there are any issues with the request, the server responds with an appropriate error message and status code.

### <b>5. AllUsers Class</b>

    The AllUsers class is a resource in a Flask RESTful API that retrieves information about all users. Access to this endpoint is restricted to authenticated users with specific roles.

    The get method is responsible for retrieving information about all users based on the role and status of the requesting user. Here’s how it works:

    1. Retrieve User ID and Role: It calls get_jwt_identity() to get the user ID from the JWT and queries the User model to get the current user's role and status using User.query.filter_by(id=user_id).first().

    2. Initialize User List: It initializes an empty list user to store user information.

    3. Fetch Users Based on Role: It checks the role and status of the requesting user to determine which users to retrieve:

        - If the user is an "admin" and their status is "active", it retrieves information about all users with the role "seller".

        Sample JSON Response 

        [
            {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "contact": "+1234567890",
                "role": "seller",
                "status": "active"
            },
            {
                "id": 2,
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "role": "seller",
                "contact": "+9876543210",
                "status": "inactive"
            }
        ]

        - If the user is a "super admin" and their status is "active", it retrieves information about all users.

         Sample JSON Response 

        [
            {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "contact": "+1234567890",
                "role": "seller",
                "status": "active"
            },
            {
                "id": 2,
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "role": "admin",
                "contact": "+9876543210",
                "status": "inactive"
            }
            ,
            {
                "id": 2,
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "role": "super admin",
                "contact": "+9876543210",
                "status": "active"
            }
        ]


    4. Construct User Data: It constructs a list of dictionaries containing information about each user, including their ID, first name, last name, email, role, contact, and status.

    5. Return Response: It returns a JSON response containing information about all users with a 200 HTTP status code.

### Example Usage

    To use this endpoint, the client must send a GET request with a valid JWT:

    GET /all_users
    Authorization: Bearer <your_jwt_token>

    If the user is authorized and their status is active, the server responds with information about all users based on their role. If the user is unauthorized or their status is inactive, the server responds with an appropriate error message and status code.

### <b>6. OneUser Class</b>

    The OneUser class is a resource in a Flask RESTful API that handles retrieving and updating information about a specific user. Access to this endpoint is restricted to authenticated users with specific roles.


#### get Method

    The get method is responsible for retrieving information about a specific user based on their ID. Here’s how it works:

    1. Retrieve User ID and Role: It calls get_jwt_identity() to get the user ID from the JWT and queries the User model to get the current user's role and status using User.query.filter_by(id=user_id).first().

    2. Check User Authorization: It checks the role and status of the requesting user to determine if they are authorized to access the requested user information:

        - If the user has the role "admin" or "seller" and their status is "active", it retrieves information about the user with the given ID and role 'seller'.
        - If the user has the role "super admin" and their status is "active", it retrieves information about the user with the given ID.
        - If the user is not authorized, it returns a 401 HTTP status code with a message indicating "Unauthorized User".
    
    3. Fetch User and Sales Data: It queries the User model to get the user information and the Sale model to get the user's completed sales. It calculates the total number of sales and the total commission from these sales.

    4. Construct User Data: It constructs a dictionary containing the user's information, including their ID, first name, last name, image URL, email, role, contact, sales details, number of sales, and total commission.

    5. Return Response: It returns a JSON response with the user's information and a 200 HTTP status code.

### Sample JSON Response

    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "image": "https://example.com/image.jpg",
        "email": "john.doe@example.com",
        "role": "seller",
        "contact": "+1234567890",
        "sales": [
            {
            "id": 101,
            "commision": 500,
            "status": "completed",
            "history": "history details",
            "discount": 10,
            "sale_date": "2023-01-01",
            "promotions": "promo details"
            }
        ],
        "number_of_sales": 1,
        "total_commission": 500
    }
    
#### put Method

    The put method is responsible for updating information about a specific user based on their ID. Here’s how it works:

    1. Retrieve User ID and Role: It calls get_jwt_identity() to get the user ID from the JWT and queries the User model to get the current user's role and status using User.query.filter_by(id=user_id).first().

    2. Validate Input: It retrieves the form data from the request using request.form and the image file using request.files.get('image').

    3. Check User Authorization: It checks the role and status of the requesting user to determine if they are authorized to update the requested user's information:

        - If the user has the role "super admin" and their status is "active", they can update any user's information.
        - If the user has the role "admin" and their status is "active", they can update information for users with the role 'seller'.
        - If the user is not authorized, it returns a 401 HTTP status code with a message indicating "Unauthorized User".
    
    4. Fetch User to Update: It queries the User model to get the user information. If no user is found with the given ID, it returns a 401 HTTP status code with a message indicating "No user to update".

    5. Update User Information: It updates the user's information with the provided data:

        - Updates the first name, last name, email, contact, role (if applicable), and image URL (after uploading the image to Cloudinary).
        - Validates the uploaded image file type and uploads it to Cloudinary. If there are any issues with the file upload, it returns an appropriate error message.
    
    6. Commit Changes: It commits the changes to the database.

    7. Return Response: It returns a JSON response indicating that the user was updated successfully with a 200 HTTP status code.

#### Sample JSON Request (Form Data)

    {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "contact": "+9876543210",
        "role": "admin",
        "image": <image_file>
    }

### Sample JSON Response   
    {
    "message": "User updated successfully"
    }

### Example Usage

    To use this endpoint, the client must send a GET or PUT request with a valid JWT:

#### GET Request

    GET /user/<id>
    Authorization: Bearer <your_jwt_token>

#### PUT Request

    PUT /user/<id>
    Authorization: Bearer <your_jwt_token>
    Content-Type: multipart/form-data

    {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "contact": "+9876543210",
        "role": "admin",
        "image": <image_file>
    }

    If the user is authorized and the request is valid, the server responds with the requested user's information (for GET) or a success message (for PUT). If there are any issues with the request, the server responds with an appropriate error message and status code.

### <b>7. INVENTORY Class</b>

    The INVENTORY class is a resource in a Flask RESTful API that handles creating and retrieving inventory items. Access to the creation endpoint is restricted to authenticated users with specific roles.

#### post Method

    The post method is responsible for creating a new inventory item. Here’s how it works

    1. Retrieve User ID and Role: It calls get_jwt_identity() to get the user ID from the JWT and queries the User model to get the current user's role and status using User.query.filter_by(id=user_id).first().

    2. Validate Input: It retrieves the form data and image files from the request using request.form and request.files. It checks if the main image and gallery images are provided and have valid file types.

    3. Upload Images: It uploads the main image and gallery images to Cloudinary. If there are any issues with the file upload, it returns an appropriate error message.

    4. Check User Authorization: It checks the role and status of the requesting user to determine if they are authorized to create a new inventory item:

        - If the user has the role "admin" or "super admin" and their status is "active", they are authorized to create a new inventory item.
        - If the user is not authorized, it returns a 401 HTTP status code with a message indicating "User has no access rights to create a Car"
    
    5. Create Inventory Item: It creates a new Inventory object with the provided data and adds it to the database. It also creates GalleryImage objects for each uploaded gallery image and associates them with the inventory item.

    6. Commit Changes: It commits the changes to the database.

    7. Return Response: It returns a JSON response indicating that the inventory item was created successfully with a 201 HTTP status code.

#### Sample JSON Request (Form Data)

    {
        "make": "Toyota",
        "image": <image_file>,
        "gallery_images": [<image_file_1>, <image_file_2>],
        "price": 20000,
        "currency": "USD",
        "model": "Camry",
        "year": 2020,
        "VIN": "1234567890ABCDEF",
        "color": "Red",
        "mileage": 15000,
        "body_style": "Sedan",
        "transmission": "Automatic",
        "fuel_type": "Gasoline",
        "engine_size": "2.5L",
        "drive_type": "FWD",
        "trim_level": "XLE",
        "condition": "New",
        "availability": "In Stock",
        "cylinder": 4,
        "doors": 4,
        "features": "Bluetooth, Backup Camera",
        "stock_number": "T12345",
        "purchase_cost": 18000,
        "profit": 2000
    }

### Sample JSON Response

    {
        "message": "Inventory created successfully"
    }

#### get Method

    The get method is responsible for retrieving all inventory items. Here’s how it works:

    1. Fetch Inventory Items: It queries the Inventory model to get all inventory items.

    2. Construct Inventory Data: It constructs a list of dictionaries containing information about each inventory item, including their ID, make, image URL, price, currency, model, year, VIN, color, mileage, body style, transmission, fuel type, engine size, drive type, trim level, gallery images, condition, availability, cylinder, doors, features, stock number, purchase cost, and profit.

    3. Return Response: It returns a JSON response with the inventory items' information.

### Sample JSON Response

    [
        {
            "id": 1,
            "make": "Toyota",
            "image": "https://example.com/image.jpg",
            "price": 20000,
            "currency": "USD",
            "model": "Camry",
            "year": 2020,
            "VIN": "1234567890ABCDEF",
            "color": "Red",
            "mileage": 15000,
            "body_style": "Sedan",
            "transmission": "Automatic",
            "fuel_type": "Gasoline",
            "engine_size": "2.5L",
            "drive_type": "FWD",
            "trim_level": "XLE",
            "gallery": ["https://example.com/gallery1.jpg", "https://example.com/gallery2.jpg"],
            "condition": "New",
            "availability": "In Stock",
            "cylinder": 4,
            "doors": 4,
            "features": "Bluetooth, Backup Camera",
            "stock_number": "T12345",
            "purchase_cost": 18000,
            "profit": 2000
        }
    ]

### Example Usage

    To use this endpoint, the client must send a POST request with a valid JWT for creating inventory items and a GET request for retrieving inventory items:

#### POST Request

    POST /inventory
    Authorization: Bearer <your_jwt_token>
    Content-Type: multipart/form-data

    {
        "make": "Toyota",
        "image": <image_file>,
        "gallery_images": [<image_file_1>, <image_file_2>],
        "price": 20000,
        "currency": "USD",
        "model": "Camry",
        "year": 2020,
        "VIN": "1234567890ABCDEF",
        "color": "Red",
        "mileage": 15000,
        "body_style": "Sedan",
        "transmission": "Automatic",
        "fuel_type": "Gasoline",
        "engine_size": "2.5L",
        "drive_type": "FWD",
        "trim_level": "XLE",
        "condition": "New",
        "availability": "In Stock",
        "cylinder": 4,
        "doors": 4,
        "features": "Bluetooth, Backup Camera",
        "stock_number": "T12345",
        "purchase_cost": 18000,
        "profit": 2000
    }

#### GET Request

    GET /inventory

If the user is authorized and the request is valid, the server responds with the created inventory item's information (for POST) or the list of all inventory items (for GET). If there are any issues with the request, the server responds with an appropriate error message and status code.


### Inventory Update and Deletion 
This class defines the InventoryUpdate resource, which handles the update and deletion of inventory items. It requires JSON Web Token (JWT) authentication to ensure that only authorized users can perform these actions.

Class: InventoryUpdate(Resource)

Endpoints:

    PUT /inventory/<id>

    DELETE /inventory/<id>

    Methods:
    PUT /inventory/<id>

    This method updates an inventory item.

    Authentication: Requires a valid JWT token.
    Authorization: Only users with the role of 'admin' or 'super admin' and an active status can update inventory items.
    Request Parameters:
    Form data for updating inventory item attributes.
    Gallery images as files for updating the inventory item's image gallery.

### Steps:

    1. Authenticate and authorize the user:

        Retrieve the user ID from the JWT token.
        Fetch the user from the database and check their role and status.

    2. Find the inventory item:

        Query the Inventory table to find the item by its ID.
        Return a 404 error if the item is not found.
        
    3. Upload gallery images:

        If provided, upload gallery images to Cloudinary.
        Save the URLs of the uploaded images in the GalleryImage table.

    4. Update inventory item attributes:

    Iterate over the provided form data and update the inventory item attributes accordingly.
    Commit the changes to the database.

    5. Return a success message:

    Respond with a message indicating that the inventory item was updated successfully.
    Response:

    200 OK - Inventory item updated successfully.
    404 Not Found - Inventory item not found.
    422 Unprocessable Entity - User does not have access rights to update the inventory item.
    500 Internal Server Error - Error occurred while uploading gallery images.
    DELETE /inventory/<id>
    This method deletes an inventory item.

    Authentication: Requires a valid JWT token.
    Authorization: Only users with the role of 'admin' or 'super admin' and an active status can delete inventory items.
#### Steps:

    1. Authenticate and authorize the user:

        Retrieve the user ID from the JWT token.
        Fetch the user from the database and check their role and status.

    2. Delete gallery images:

        Query the GalleryImage table to find images associated with the inventory item.
        Delete all found gallery images.
        Delete the inventory item:

    3. Query the Inventory table to find the item by its ID.

        If found, delete the inventory item and commit the changes to the database.
        Return a success message.
        Return a response:

    Respond with a message indicating that the inventory item was deleted successfully.
    If the item is not found, return a 404 error.
    Response:

    200 OK - Inventory item deleted successfully.
    404 Not Found - Inventory item not found.
    422 Unprocessable Entity - User does not have access rights to delete the inventory item.


### Importations

This class defines the Importations resource, which handles the retrieval and creation of importation records. It requires JSON Web Token (JWT) authentication to ensure that only authorized users can perform these actions.

Class: Importations(Resource)
Endpoints:

GET /importations

POST /importations

Methods:
GET /importations

This method retrieves all importation records.

Authentication: Requires a valid JWT token.
Authorization: Only users with the role of 'super admin', 'admin', or 'seller' with an active status can retrieve importation records.

#### Steps:

    1. Authenticate and authorize the user:

        Retrieve the user ID from the JWT token.
        Fetch the user from the database and check their role and status.

    2. Retrieve importation records:

        Query the Importation table to get all importation records.
        For each importation record, gather relevant details, including associated car information from the Inventory table.
    3. Return importation data:

        Respond with a list of importation records, each containing details such as the country of origin, transport fee, currency, import duty, import date, import document, and car details.
    4. Response:

        200 OK - Successfully retrieved importation records.
        401 Unauthorized - User does not have access rights to retrieve importation records.
        POST /importations
        This method creates a new importation record.

        Authentication: Requires a valid JWT token.
        Authorization: Only users with the role of 'super admin' or 'admin' with an active status can create importation records.

        Steps:

        1. Authenticate and authorize the user:

        Retrieve the user ID from the JWT token.
        Fetch the user from the database and check their role and status.
        2. Validate form data and uploaded document:

        Ensure all required fields are present: country_of_origin, transport_fee, currency, import_duty, import_date, car_id.
        Ensure an import document is provided and is of an allowed file type (e.g., png, jpg, jpeg, gif, pdf, doc, docx, txt).

        3. Upload import document:

        Upload the document to Cloudinary.
        Handle any errors during the upload process.

        4. Create new importation record:

        Create a new Importation object with the provided data and the URL of the uploaded document.
        Add the new importation record to the database and commit the transaction.

        5. Return a success message:

        Respond with a message indicating that the importation record was created successfully.
        Response:

        201 Created - Importation record created successfully.
        400 Bad Request - Missing required fields or invalid file type.
        401 Unauthorized - User does not have access rights to create importation records.
        500 Internal Server Error - Error occurred while uploading the document.

### Update and Delete Importation API

This class defines the UpdateImportation resource, which handles the updating and deletion of importation records. It requires JSON Web Token (JWT) authentication to ensure that only authorized users can perform these actions.

Class: UpdateImportation(Resource)
Endpoints:

    PUT /importations/<importation_id>

    DELETE /importations/<importation_id>

    Methods:
    PUT /importations/<importation_id>

    This method updates an existing importation record.

    Authentication: Requires a valid JWT token.
    Authorization: Only users with the role of 'super admin' or 'admin' with an active status can update importation records.

#### Steps:

    1. Authenticate and authorize the user:

    Retrieve the user ID from the JWT token.
    Fetch the user from the database and check their role and status.

    2. Retrieve and validate the importation record:

    Query the Importation table to find the record by its ID.
    Return a 404 error if the importation record is not found.

    3. Validate and upload the document:

    Retrieve the import document from the request.
    Check if a document is selected for upload and validate its file type.
    Upload the document to Cloudinary and update the import_document field with the secure URL.

    4. Update importation attributes:

    Iterate over the provided form data and update the importation attributes accordingly.
    Commit the changes to the database.

    5. Return a success message:

    Respond with a message indicating that the importation record was updated successfully.
    Response:

    200 OK - Importation record updated successfully.
    400 Bad Request - No document selected for upload or invalid file type.
    404 Not Found - Importation record not found.
    500 Internal Server Error - Error occurred while uploading the document.
    401 Unauthorized - User does not have access rights to update importation records.
    DELETE /importations/<importation_id>
    This method deletes an existing importation record.

    Authentication: Requires a valid JWT token.
    Authorization: Only users with the role of 'super admin' or 'admin' with an active status can delete importation records.
#### Steps:

    1. Authenticate and authorize the user:

    Retrieve the user ID from the JWT token.
    Fetch the user from the database and check their role and status.
    Retrieve and validate the importation record:

    2. Query the Importation table to find the record by its ID.
    Return a 404 error if the importation record is not found.
    Delete the importation record:

    3 Delete the importation record from the database and commit the changes.
    Return a success message:

    4. Respond with a message indicating that the importation record was deleted successfully.
    Response:

    200 OK - Importation record deleted successfully.
    404 Not Found - Importation record not found.
    401 Unauthorized - User does not have access rights to delete importation records.








