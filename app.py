import os
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fastpos-secret-key-2026'

# ضبط SocketIO ليتوافق تماماً مع بيئة Render ويمنع انقطاع الاتصال
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', ping_timeout=60, ping_interval=25)

# قاعدة بيانات مؤقتة في الذاكرة لتخزين الطلبات والمنيو
active_orders = {}
menu_items = [
    {"id": 1, "name": "بيتزا مارغريتا", "price": 500},
    {"id": 2, "name": "بيتزا دجاج", "price": 700},
    {"id": 3, "name": "طاكوس مكسيكي", "price": 450}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/server')
def server_page():
    return render_template('server.html', menu=menu_items)

@app.route('/kitchen')
def kitchen():
    return render_template('kitchen.html')

@app.route('/caisse')
def caisse():
    return render_template('caisse.html')

@app.route('/admin/menu', methods=['GET', 'POST'])
def admin_menu():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('name')
            price = float(request.form.get('price', 0))
            new_id = len(menu_items) + 1
            menu_items.append({"id": new_id, "name": name, "price": price})
        elif action == 'update':
            item_id = int(request.form.get('item_id'))
            new_price = float(request.form.get('price', 0))
            for item in menu_items:
                if item['id'] == item_id:
                    item['price'] = new_price
        return redirect(url_for('admin_menu'))
    return render_template('admin_menu.html', menu=menu_items)

# استقبال الطلبية من السيرفر وبثها مباشرة لكل من الكوزينة والصندوق في نفس الثانية
@socketio.on('new_order')
def handle_order(data):
    table_num = str(data.get('table', '1'))
    data['table'] = table_num
    active_orders[table_num] = data
    print(f"📦 تم استلام وبث طلبية الطاولة رقم {table_num}")
    emit('new_order', data, broadcast=True)

# الرد على طلب الصندوق لعرض فاتورة الطاولة
@socketio.on('get_table_order')
def get_table_order(data):
    table_num = str(data.get('table', '1'))
    order = active_orders.get(table_num)
    emit('table_order_response', order)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
