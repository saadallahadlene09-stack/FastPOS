import os
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

active_orders = {}
menu_items = []

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

@socketio.on('new_order')
def handle_order(data):
    table_num = str(data['table'])
    data['table'] = table_num
    active_orders[table_num] = data
    emit('new_order', data, broadcast=True)

@socketio.on('get_table_order')
def get_table_order(data):
    table_num = str(data['table'])
    order = active_orders.get(table_num)
    emit('table_order_response', order)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)