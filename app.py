
from flask import Flask, render_template, request, jsonify, session, send_file
from io import BytesIO
import qrcode
from datetime import datetime
app = Flask(__name__)
app.secret_key = "restaurant-secret-key"

orders = []
order_status = {}
order_times = {}



@app.route("/")
def menu():
    table_number = request.args.get("table", "")

    if table_number:
        session["table_number"] = table_number

    return render_template("menu.html", table_number=table_number)

@app.route("/admin")
def admin():
    return render_template("admin.html")
@app.route("/qr-codes")
def qr_codes():
    tables = range(1, 9)
    return render_template("qr_codes.html", tables=tables)
@app.route("/qr/<int:table_number>")
def generate_qr(table_number):
    menu_url = "https://restaurant-menu-1-2157.onrender.com/?table=" + str(table_number)
    qr = qrcode.make(menu_url)

    img = BytesIO()
    qr.save(img, format="PNG")
    img.seek(0)

    return send_file(img, mimetype="image/png")

@app.route("/api/orders")
def api_orders():
    return jsonify(orders)


@app.route("/api/order-statuses")
def api_order_statuses():
    return jsonify(order_status)
@app.route("/api/my-orders")
def api_my_orders():

    my_order_ids = session.get("my_orders", [])

    my_orders = []

    for order_id in my_order_ids:

        if 0 <= order_id < len(orders):

            my_orders.append({
                "order_id": order_id,
                "items": orders[order_id],
                "status": order_status.get(order_id, "Kutilmoqda")
            })

    return jsonify(my_orders)

@app.route("/order", methods=["POST"])
def order():

    data = request.json

    for item in data:
        item["table_number"] = session.get("table_number", "")

    orders.append(data)

    order_id = len(orders) - 1

    my_order_ids = session.get("my_orders", [])
    my_order_ids.append(order_id)

    session["my_orders"] = my_order_ids
    session.modified = True

    order_times[order_id] = datetime.now()

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


@app.route("/api/stats")
def api_stats():

    today = datetime.now().date()

    today_orders = 0
    today_revenue = 0

    for order_id, order in enumerate(orders):

        if order_id not in order_times:
            continue

        if order_times[order_id].date() == today:

            today_orders += 1

            for item in order:
                today_revenue += item["price"] * item["quantity"]

    active_orders = 0
    ready_orders = 0

    for index in range(len(orders)):

        if order_status.get(index) == "Tayyor":
            ready_orders += 1
        else:
            active_orders += 1

    return jsonify({
        "today_orders": today_orders,
        "today_revenue": today_revenue,
        "active_orders": active_orders,
        "ready_orders": ready_orders
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)