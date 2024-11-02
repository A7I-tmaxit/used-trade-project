from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime

USER_DATA_FILE = 'users.json'
MARKET_DATA_FILE = 'market.json'

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

def save_data(file_path, data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully saved to {file_path}")
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _respond(self, response):
        self.wfile.write(json.dumps(response).encode())
    def do_GET(self):
        if self.path == "/products":
            self.handle_get_products()
        elif self.path.startswith("/user_sales"):
            self.handle_user_sales()
        else:
            self._set_headers(404)
            self._respond({"message": "Endpoint not found"})

    def do_OPTIONS(self):
        self._set_headers()

    def do_POST(self):
        if self.path == "/register":
            self.handle_register()
        elif self.path == "/login":
            self.handle_login()
        elif self.path == "/add_product":
            self.handle_add_product()
        elif self.path.startswith("/purchase/"):
            self.handle_purchase()
        else:
            self._set_headers(404)
            self._respond({"message": "Endpoint not found"})

    def do_GET(self):
        if self.path == "/products":
            self.handle_get_products()
        elif self.path.startswith("/user_sales"):
            self.handle_user_sales()
        else:
            self._set_headers(404)
            self._respond({"message": "Endpoint not found"})


    def handle_register(self):
        length = int(self.headers.get('Content-Length'))
        post_data = json.loads(self.rfile.read(length))
        username, password, name, balance = post_data.get("username"), post_data.get("password"), post_data.get("name"), post_data.get("balance")
        users = load_data(USER_DATA_FILE)
        users[username] = {"password": password, "name": name, "balance": balance}
        save_data(USER_DATA_FILE, users)

        if username in users:
            self._set_headers(400)
            self._respond({"message": "User already exists"})
        else:
            users[username] = {"password": password, "name": name, "balance": int(balance)}
            save_data(USER_DATA_FILE, users)
            self._set_headers()
            self._respond({"message": "User registered successfully"})

    def handle_login(self):
        length = int(self.headers.get('Content-Length'))
        post_data = json.loads(self.rfile.read(length))
        username, password = post_data.get("username"), post_data.get("password")
        users = load_data(USER_DATA_FILE)
        
        if users.get(username, {}).get("password") == password:
            self._set_headers()
            user = users[username]

            self._respond({"message": "Login successful", "userId": username, "name": user["name"], "balance": user["balance"]})
        else:
            self._set_headers(401)
            self._respond({"message": "Invalid username or password"})


    def handle_add_product(self):
        length = int(self.headers.get('Content-Length'))
        post_data = json.loads(self.rfile.read(length))
        print("Received product data:", post_data)  # Log product data

        products = load_data(MARKET_DATA_FILE)
        seller_id = post_data.get("userId")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Use current time for unique key
        product_key = f"{seller_id}_{timestamp}"

        products[product_key] = {
            "name": post_data.get("name"),
            "description": post_data.get("description"),
            "price": int(post_data.get("price")),
            "images": post_data.get("images"),  # Store all images
            "mainImage": post_data.get("mainImage"),  # Store main image separately
            "sellerName": post_data.get("sellerName"),
            "sellerId": seller_id,
            "dateAdded": datetime.now().isoformat()  # Store date added
        }
        save_data(MARKET_DATA_FILE, products)
        self._set_headers()
        self._respond({"message": "Product added successfully"})



    def handle_get_products(self):
        try:
            products = load_data(MARKET_DATA_FILE)
            self._set_headers()
            self._respond(products)
        except json.JSONDecodeError:
            print("Error: Failed to parse market.json")
            self._set_headers(500)
            self._respond({"error": "Failed to load products. Please check the server log for details."})

        
    def handle_purchase(self):
        product_id = self.path.split("/")[-1]
        length = int(self.headers.get('Content-Length'))
        post_data = json.loads(self.rfile.read(length))
        buyer_balance = post_data.get("buyerBalance")
        buyer_username = post_data.get("buyer")
        users = load_data(USER_DATA_FILE)
        products = load_data(MARKET_DATA_FILE)

        if product_id in products:
            product_price = products[product_id]["price"]
            seller_username = products[product_id]["seller"]

            if buyer_balance >= product_price:
                users[buyer_username]["balance"] -= product_price
                users[seller_username]["balance"] += product_price
                del products[product_id]
                save_data(USER_DATA_FILE, users)
                save_data(MARKET_DATA_FILE, products)
                self._set_headers()
                self._respond({"success": True, "productPrice": product_price})
            else:
                self._set_headers(400)
                self._respond({"success": False, "message": "Insufficient balance"})
        else:
            self._set_headers(404)
            self._respond({"success": False, "message": "Product not found"})
    def handle_user_sales(self):
        user_id = self.path.split("userId=")[-1]
        print(f"Fetching sales for user: {user_id}")
        try:
            products = load_data(MARKET_DATA_FILE)
            user_sales = {pid: prod for pid, prod in products.items() if prod.get("sellerId") == user_id}
            self._set_headers()
            self._respond(user_sales)
        except Exception as e:
            print("Error fetching user sales:", e)
            self._set_headers(500)
            self._respond({"error": "Failed to load user sales."})


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd server on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
