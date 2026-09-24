
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = "restaurant-secret-key"

orders = []
order_status = {}
customer_orders = {}


@app.route("/")
def menu():
    return render_template("menu.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/api/orders")
def api_orders():
    return jsonify(orders)


@app.route("/api/order-statuses")
def api_order_statuses():
    return jsonify(order_status)
@app.route("/api/my-orders")
def api_my_orders():

    customer_id = session.get("customer_id")

    if not customer_id:
        return jsonify([])

    my_order_ids = customer_orders.get(customer_id, [])

    my_orders = []

    for order_id in my_order_ids:
        my_orders.append({
            "order_id": order_id,
            "items": orders[order_id],
            "status": order_status.get(order_id, "Kutilmoqda")
        })

    return jsonify(my_orders)


@app.route("/order", methods=["POST"])
def order():
    data = request.json

    if "customer_id" not in session:
        session["customer_id"] = str(len(customer_orders) + 1)

    customer_id = session["customer_id"]

    orders.append(data)

    order_id = len(orders) - 1

    if customer_id not in customer_orders:
        customer_orders[customer_id] = []

    customer_orders[customer_id].append(order_id)

    return jsonify({
        "success": True,
        "message": "Buyurtma qabul qilindi!",
        "order_id": order_id
    })

@app.route("/order-ready/<int:order_id>", methods=["POST"])
def order_ready(order_id):
    order_status[order_id] = "Tayyor"

    return jsonify({
        "success": True,
        "message": "Buyurtma tayyor deb belgilandi!"
    })


@app.route("/order-status/<int:order_id>")
def order_status_check(order_id):
    status = order_status.get(order_id, "Kutilmoqda")

    return jsonify({
        "status": status
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)