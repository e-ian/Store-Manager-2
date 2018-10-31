"""
module views
"""
from flask import Flask, jsonify, request, make_response
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token, get_jwt_identity)
from api.v1 import app
from api.v1.validators import Validate
from api.v1.db_actions import Products, Sales, Users
from api.v1.models import Datastore

a = Products()
b = Sales()
c = Users()
validator = Validate()

@app.route('/')
def index():
    """default home route"""
    return jsonify({'message': 'welcome to store manager'})

@app.route('/api/v1/products', methods=['POST'])
def post_product():
    """ implements the post products api  """
    try:        
        form_data = request.get_json(force=True)
        product_item = {
                'product_name': form_data['product_name'],            
                'price' : form_data['price'],
                'category' : form_data['category'],
                'quantity' : form_data['quantity'],
                'minimum_quantity' : form_data['minimum_quantity']
            }
        if not Validate.validate_prod_name_and_category(product_item['product_name'], product_item['category']):
            return make_response(jsonify({"Message": "Product_name or category cannot be empty and takes alphabets"}), 400)
        elif not Validate.validate_price_and_quantity(product_item['price'], product_item['quantity'], product_item['minimum_quantity']):
            return make_response(jsonify({"message": 'Price, quantity and minimum_quantity fields cannot be empty and should be an integer '}), 400)
        
        check_product = a.check_product(product_item['product_name'])
        if check_product:
            return make_response(jsonify({"message": "product already exits"}), 400)
        else:
            a.add_product(product_item)
            return make_response(jsonify({"message": 'product added successfully'}), 201)
    except Exception:
        return make_response(jsonify({"error": 'invalid input format'}), 400)

@app.route('/api/v1/products/<int:product_id>', methods=['PUT'])
def edit_product(product_id):
    """method to edit or modify an existing product"""
    pdt_list = a.get_single_product(product_id)
    data = request.get_json(force=True)
    if pdt_list:
        a.modify_product(data['product_id'], data['product_name'], data['price'], data['category'], data['quantity'], data['minimum_quantity'])
        return make_response(jsonify({'message': 'product edited'}),200)
    else:
        return make_response(jsonify({'message': 'product does not exist'}), 404)

@app.route('/api/v1/sales', methods=['POST'])
def post_sale_order():
    """ adds a sale order """
    try:
        data = request.get_json(force=True)
        sale_order = {
            "product_name": data['product_name'],
            "price": data["price"],
            "quantity": data["quantity"]
        }
        if not Validate.validate_prod_name(sale_order['product_name']):
            return make_response(jsonify({"Message": "Product_name cannot be empty and takes alphabets"}), 400)
        elif not Validate.validate_sale_price_and_quantity(sale_order['price'], sale_order['quantity']):
            return make_response(jsonify({"message": 'Price and quantity fields cannot be empty and should be an integer '}), 400)
        else:
            b.add_sale_order(sale_order)
            return make_response(jsonify({"message": 'sale order added successfully'}), 201)
    except Exception:
        return make_response(jsonify({"error": 'invalid input format'}), 400)
    data = request.get_json(force=True)

@app.route('/api/v1/sales')
def get_all_sale_orders():
    """implements get all sale orders endpoint"""
    sale_orders = b.get_sale_orders()
    if sale_orders:
        return make_response(jsonify({'sale_list': sale_orders}), 200)

@app.route('/api/v1/sales/<int:sale_id>')
def get_a_sale_order(sale_id):
    """method to get a one sale order"""
    get_sale = b.get_specific_sale_order(sale_id)
    if get_sale:
        return make_response(jsonify({"sale order": get_sale}), 200)
    else:
        return make_response(jsonify({"message": 'sale order not found'}), 404)

@app.route('/api/v1/auth/login', methods=['POST'])
def log_a_user():
    """method implementing api for logging in user"""
    login_data ={
        "username": request.json["username"],
        "password": request.json["password"]
    }

    user_login = c.login_users(login_data)
    
    if not user_login:
        return make_response(jsonify({"message":"Username does not exist"}), 404)
    pass_check = c.check_password(user_login["password"], login_data["password"])
        
    if user_login and pass_check:
        access_token = create_access_token(identity=user_login)
        return make_response(jsonify({"message": 'login successful', "access_token":access_token}), 200)
    else:
        return make_response(jsonify({"message": "username or password is wrong"}), 400)
