from flask import Flask, jsonify, request, logging, render_template, redirect, url_for, session
from .mongo import db
from .query import query_db
import re

# MongoDB adreslerini yapılandırma
mongo_addresses = {
    "bedas": "mongodb://username:password@default-mongo-address:27017/?authSource=db",
    "medas": "mongodb://mUser:t0RvSL1dtd@10.142.1.109:27017/",
    "uedas": "mongodb://mUser:t0RvSL1dtd@10.216.0.139:27017/"
}

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['SESSION_PERMANENT'] = False

# MongoDB sınıfından bir nesne oluşturun
db = db()

@app.route('/modem/<collection>/<queryBy>/post/<queryValue>/<queryLimit>', methods=['POST'])
def getModemByImeiOrIpAddress(collection, queryBy, queryValue, queryLimit):
    app.logger.info(f"Querying database for {queryBy} = {queryValue}")
    rsp = query_db(db, collection, queryBy, queryValue, queryLimit)
    return jsonify(rsp)

@app.route('/mongo', methods=['GET'])
def mongo():
    status = db.checkConnection()
    return jsonify(status)

@app.route('/modem', methods=['POST'])
def response():
    queryBy = request.form.get('queryBy')
    queryValue = request.form.get('queryValue')
    collection = request.form.get('collection')
    queryLimit = int(request.form.get('queryLimit'))

    app.logger.info(f"Querying database for {queryBy} = {queryValue}")

    return render_template('response.html', collection=collection, queryBy=queryBy, queryValue=queryValue, queryLimit=queryLimit)

@app.route('/index')
def index():
    if 'username' in session:
        username = session['username']
        password = session['password']
        mongo_uri = session.get('mongo_uri')  # Oturumdan Mongo URI'yi al

        if mongo_uri:
            db.setMongoUri(mongo_uri)  # Oturumdan gelen Mongo URI'yi kullan
        else:
            return jsonify({"mongoStatus": "-1", "error": "No Mongo URI found in session."})

        try:
            db.setup(db.getMongoUri())  # MongoDB bağlantısını başlat
        except Exception as e:
            return jsonify({"mongoStatus": "-1", "error": str(e)})

        app.logger.info('Index page')
        return render_template('index.html', collections=db.collections)

    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        selected_address = request.form['mongoAddress']  # Kullanıcının seçtiği MongoDB adresi

        if username == 'ahmetpolat' and password == 'ahmetpolat!123':  # Örnek giriş bilgileri
            session['username'] = username
            session['password'] = password

            # Seçilen MongoDB adresine göre URI ayarlama
            selected_mongo_uri = mongo_addresses.get(selected_address)
            if selected_mongo_uri:  # Eğer adres bulunursa MongoDB URI'sini ayarla
                session['mongo_uri'] = selected_mongo_uri  # Mongo URI'yi oturuma ekle
                db.setMongoUri(selected_mongo_uri)
            else:
                return 'Selected MongoDB address is not valid.'

            return redirect(url_for('index'))
        return 'Invalid credentials. Please try again.'
    return render_template('login.html')

@app.route('/functions')
def functions():
    return render_template('functions.html')

@app.route('/average_rate', methods=['GET'])
def average_rate():
    try:
        collection = db.get_collection('mng-status')  # İlgili koleksiyonu tanımlayın
        if collection is None:  # Koleksiyon yoksa hata ver
            raise ValueError("Collection 'mng-status' does not exist.")
        
        messages = collection.find()
        
        rates = []
        for message in messages:
            if 'rate:' in message.get('text', ''):
                match = re.search(r'rate:(\d+)', message['text'])
                if match:
                    rate = int(match.group(1))
                    rates.append(rate)
        
        if rates:
            average = sum(rates) / len(rates)
        else:
            average = 0

        return jsonify({'average_rate': average})
    except Exception as e:
        app.logger.error(f"Error calculating average rate: {str(e)}")
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(host='172.22.201.236', port=8000, debug=True)
