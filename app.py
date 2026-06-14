from flask import Flask , jsonify ,request,render_template
import sqlite3
import random
import hashlib
from dotenv import load_dotenv
import os
from functools import wraps
from flask_cors import CORS
#load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")




app = Flask(__name__)
# products = [
#         {"id":1 , "name":"keyboard" , "price":49} , {"id":2 , "name":"mouse" , "price":59} , {"id":3, "name":"headset" , "price":60}

#     ]
CORS(app)



#protecting our API 


def require_token(f):
    @wraps(f)
    def decorated(*args , **kwargs):
        token = request.headers.get("Authorization")
        
        if token != f"Bearer {API_TOKEN}":
            return jsonify({"error":"unauthorized"}),401
        return f(*args , **kwargs)
    return decorated









def get_db_connection():
    #how to get exact path
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR,"products.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/init", methods=["GET"])
def init_db():
    conn = get_db_connection()
    conn.execute("""CREATE TABLE IF NOT EXISTS products(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 price REAL NOT NULL) """)
    
    conn.execute("""CREATE TABLE IF NOT EXISTS users(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL unique,
                 password REAL NOT NULL) """)
    
    conn.commit()
    conn.close()
    return jsonify({"mesage":"connection successful "})
@app.route("/")

def home():
    return render_template("web_client.html")
    return jsonify({"message": "hello from flask server"}) #conver the json data
@app.route("/products", methods = ["GET"])
def get_product():
   
    conn = get_db_connection()
    
    rows= conn.execute("""SELECT * FROM products""").fetchall()
    # rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append(dict(row))
    return jsonify({"output":result})


@app.route("/products" , methods=["POST"])
@require_token
def add_products():
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products(name , price) VALUES (? , ?)" , (name , price))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    


    new_product = {
        "id": new_id, 
        "name": name,
        "price": price,


    }


    return jsonify({"message" : "data addded successfully" , "product": new_product}),201

@app.route("/register" ,methods = ["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"message" : "error give username or password "}),400
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        conn = get_db_connection()
        conn.execute(""" INSERT INTO users (username , password) values (? , ?) """, (username , hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"message":"user registered successfully"}),201
    except sqlite3.IntegrityError:
        return jsonify({"messsage" : "username already exist"}),409

@app.route("/login" , methods = ["POST"])
def login():
    data = request.get_json()
    
    username= data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"message": "you cant give empty cred"}),401
    

    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db_connection()
    user = conn.execute("""SELECT * FROM users WHERE username = ? and password = ?""" , (username , hashed_password)).fetchone()
    if user:
        return jsonify({"message":f"Welcome {username} to the app"}),201
    else:
        return jsonify({"message": "user not valida"}) ,409 

if __name__=="__main__":
    app.run(debug=True)  #auto reload
