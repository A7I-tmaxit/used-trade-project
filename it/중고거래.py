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
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _respond(self, response):
        self.wfile.write(json.dumps(response).encode())

    def serve_static_file(self, file_path, content_type="text/html"):
        try:
            with open(file_path, 'rb') as file:
                self._set_headers(200, content_type)
                self.wfile.write(file.read())
        except FileNotFoundError:
            self._set_headers(404)
            self._respond({"message": "File not found"})

    def do_GET(self):
        if self.path == "/":
            self.serve_static_file("index.html", "text/html")
        elif self.path == "/script.js":
            self.serve_static_file("script.js", "application/javascript")
        elif self.path == "/style.css":
            self.serve_static_file("style.css", "text/css")
        elif self.path == "/products":
            self.handle_get_products()
        elif self.path.startswith("/products/"):
            self.handle_get_product_by_id()
        elif self.path.startswith("/user_sales"):
            self.handle_user_sales()
        elif self.path.startswith("/get_favorites"):
            self.handle_get_favorites()
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
        elif self.path == "/edit_product":
            self.handle_update_product()
        elif self.path.startswith("/purchase/"):  # 구매 요청을 처리하도록 추가
            self.handle_purchase()
        elif self.path == "/toggle_favorite":  # Add this line
            self.handle_toggle_favorite()
        elif self.path == "/charge_points":  # 포인트 충전 엔드포인트
            self.handle_charge_points()
        else:
            self._set_headers(404)
            self._respond({"message": "Endpoint not found"})

    def do_DELETE(self):
        if self.path.startswith("/delete_product/"):
            self.handle_delete_product()
        else:
            self._set_headers(404)
            self._respond({"message": "Endpoint not found"})

    def handle_delete_product(self):
        product_id = self.path.split("/")[-1]
        products = load_data(MARKET_DATA_FILE)
        
        if product_id in products:
            del products[product_id]
            save_data(MARKET_DATA_FILE, products)
            self._set_headers(200)
            self._respond({"success": True, "message": "Product deleted successfully"})
        else:
            self._set_headers(404)
            self._respond({"success": False, "message": "Product not found"})
    def handle_get_products(self):
        try:
            products = load_data(MARKET_DATA_FILE)
            self._set_headers()
            self._respond(products)
        except json.JSONDecodeError:
            print("Error: Failed to parse market.json")
            self._set_headers(500)
            self._respond({"error": "Failed to load products. Please check the server log for details."})
    def handle_get_product_by_id(self):
        product_id = self.path.split("/")[-1]
        products = load_data(MARKET_DATA_FILE)
        
        if product_id in products:
            self._set_headers()
            self._respond(products[product_id])
        else:
            self._set_headers(404)
            self._respond({"message": "Product not found"})

    def handle_update_product(self):
        length = int(self.headers.get('Content-Length'))
        post_data = json.loads(self.rfile.read(length))
        product_id = post_data.get("productId")
        products = load_data(MARKET_DATA_FILE)

        if product_id in products:
            products[product_id].update({
                "name": post_data.get("name"),
                "description": post_data.get("description"),
                "price": post_data.get("price"),
                "images": post_data.get("images"),
                "mainImage": post_data.get("mainImage"),
                "dateUpdated": datetime.now().isoformat()
            })
            save_data(MARKET_DATA_FILE, products)
            self._set_headers(200)
            self._respond({"success": True, "message": "Product updated successfully"})
        else:
            self._set_headers(404)
            self._respond({"success": False, "message": "Product not found"})

    def handle_register(self):
        length = int(self.headers.get('Content-Length'))
        post_data = json.loads(self.rfile.read(length))
        username, password, name, balance = post_data.get("username"), post_data.get("password"), post_data.get("name"), post_data.get("balance")
        users = load_data(USER_DATA_FILE)

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
        products = load_data(MARKET_DATA_FILE)

        seller_id = post_data.get("userId")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        product_key = f"{seller_id}_{timestamp}"

        products[product_key] = {
            "name": post_data.get("name"),
            "description": post_data.get("description"),
            "price": int(post_data.get("price")),
            "images": post_data.get("images"),
            "mainImage": post_data.get("mainImage"),
            "sellerName": post_data.get("sellerName"),
            "sellerId": seller_id,
            "dateAdded": datetime.now().isoformat()
        }
        save_data(MARKET_DATA_FILE, products)
        self._set_headers()
        self._respond({"message": "Product added successfully"})

    def handle_get_favorites(self):
        user_id = self.path.split("userId=")[-1]
        users = load_data(USER_DATA_FILE)
        products = load_data(MARKET_DATA_FILE)

        if user_id in users:
            # Get the list of product IDs that the user has favorited
            favorite_ids = users[user_id].get("favorites", [])
            
            # Collect the actual product details for each favorited product
            favorite_products = {pid: products[pid] for pid in favorite_ids if pid in products}

            # Respond with the list of favorited products
            self._set_headers()
            self._respond(favorite_products)
        else:
            self._set_headers(404)
            self._respond({"success": False, "message": "User not found"})
    def handle_charge_points(self):
            length = int(self.headers.get('Content-Length'))
            post_data = json.loads(self.rfile.read(length))
            user_id = post_data.get("userId")
            amount = post_data.get("amount")

            if not user_id or not amount or amount <= 0:
                self._set_headers(400)
                self._respond({"success": False, "message": "유효하지 않은 요청입니다."})
                return

            users = load_data(USER_DATA_FILE)

            if user_id in users:
                users[user_id]["balance"] = users[user_id].get("balance", 0) + amount
                save_data(USER_DATA_FILE, users)

                self._set_headers(200)
                self._respond({"success": True, "newBalance": users[user_id]["balance"]})
            else:
                self._set_headers(404)
                self._respond({"success": False, "message": "사용자를 찾을 수 없습니다."})

    def handle_user_sales(self):
        user_id = self.path.split("userId=")[-1]
        try:
            products = load_data(MARKET_DATA_FILE)
            user_sales = {pid: prod for pid, prod in products.items() if prod.get("sellerId") == user_id}
            self._set_headers()
            self._respond(user_sales)
        except Exception as e:
            print("Error fetching user sales:", e)
            self._set_headers(500)
            self._respond({"error": "Failed to load user sales."})
    def handle_purchase(self):
        product_id = self.path.split("/")[-1]
        length = int(self.headers.get('Content-Length'))
        post_data = json.loads(self.rfile.read(length))
        buyer_username = post_data.get("buyer")
        buyer_balance = int(post_data.get("buyerBalance"))  # 문자열을 정수로 변환

        products = load_data(MARKET_DATA_FILE)
        users = load_data(USER_DATA_FILE)

        # 해당 상품 정보 가져오기
        if product_id in products:
            product = products[product_id]
            product_price = int(product["price"])  # 문자열을 정수로 변환
            seller_username = product["sellerId"]

            # 잔액 확인 및 업데이트
            if buyer_balance >= product_price:
                # 정수 변환 후 연산
                users[buyer_username]["balance"] = int(users[buyer_username]["balance"]) - product_price
                users[seller_username]["balance"] = int(users[seller_username]["balance"]) + product_price

                # 상품의 상태를 "거래 완료"로 변경
                products[product_id]["status"] = "거래 완료"

                # 변경 사항을 파일에 저장
                save_data(USER_DATA_FILE, users)
                save_data(MARKET_DATA_FILE, products)

                # 응답 반환
                self._set_headers()
                self._respond({"success": True, "productPrice": product_price})
            else:
                # 잔액 부족 에러 처리
                self._set_headers(400)
                self._respond({"success": False, "message": "잔액이 부족합니다."})
        else:
            # 상품을 찾을 수 없을 때 에러 처리
            self._set_headers(404)
            self._respond({"success": False, "message": "상품을 찾을 수 없습니다."})
    def handle_favorite_product(self):
        length = int(self.headers.get('Content-Length'))
        post_data = json.loads(self.rfile.read(length))
        product_id = post_data.get("productId")
        user_id = post_data.get("userId")

        products = load_data(MARKET_DATA_FILE)
        users = load_data(USER_DATA_FILE)

        if product_id in products and user_id in users:
            # 찜 횟수 증가
            products[product_id]["favorites"] = products[product_id].get("favorites", 0) + 1

            # 사용자의 찜리스트에 추가
            if "favorites" not in users[user_id]:
                users[user_id]["favorites"] = []
            if product_id not in users[user_id]["favorites"]:
                users[user_id]["favorites"].append(product_id)

            save_data(MARKET_DATA_FILE, products)
            save_data(USER_DATA_FILE, users)

            self._set_headers()
            self._respond({"success": True, "favorites": products[product_id]["favorites"]})
        else:
            self._set_headers(404)
            self._respond({"success": False, "message": "상품 또는 사용자를 찾을 수 없습니다."})
    def handle_toggle_favorite(self):
        length = int(self.headers.get('Content-Length'))
        post_data = json.loads(self.rfile.read(length))
        product_id = post_data.get("productId")
        user_id = post_data.get("userId")

        products = load_data(MARKET_DATA_FILE)
        users = load_data(USER_DATA_FILE)

        if product_id in products and user_id in users:
            if "favorites" not in products[product_id]:
                products[product_id]["favorites"] = 0

            # Toggle favorite status
            if product_id in users[user_id].get("favorites", []):
                # Unfavorite the item
                products[product_id]["favorites"] -= 1
                users[user_id]["favorites"].remove(product_id)
                favorite_status = False
            else:
                # Favorite the item
                products[product_id]["favorites"] += 1
                users[user_id].setdefault("favorites", []).append(product_id)
                favorite_status = True

            # Save updated data
            save_data(MARKET_DATA_FILE, products)
            save_data(USER_DATA_FILE, users)

            self._set_headers()
            self._respond({
                "success": True,
                "favorites": products[product_id]["favorites"],
                "favoriteStatus": favorite_status
            })
        else:
            self._set_headers(404)
            self._respond({"success": False, "message": "Product or user not found"})


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd server on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
