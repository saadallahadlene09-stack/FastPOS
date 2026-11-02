from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# قاموس لتخزين طلبات كل طاولة نشطة
active_orders = {}

@app.route('/')
def index():
    return render_template('server.html')

@app.route('/kitchen')
def kitchen():
    return render_template('kitchen.html')

@app.route('/caisse')
def caisse():
    return render_template('caisse.html')

@socketio.on('new_order')
def handle_order(data):
    table_num = data['table']
    # حفظ الطلب حسب رقم الطاولة
    active_orders[table_num] = data
    # إرسال الطلب لكل الشاشات (الكوزينة والكاص)
    emit('new_order', data, broadcast=True)

@socketio.on('get_table_order')
def get_table_order(data):
    table_num = data['table']
    order = active_orders.get(table_num)
    emit('table_order_response', order)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)