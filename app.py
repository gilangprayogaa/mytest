from flask import Flask, render_template, request, jsonify
import requests
import hashlib
from datetime import datetime
import mysql.connector


app = Flask(__name__)

db_connection = mysql.connector.connect(
    host="localhost", user="root", password="",
    database="tes_fastprint"
    )

@app.route('/', methods=['GET'])
def data():
    cursor = db_connection.cursor()
    cursor.execute("SELECT id_produk, nama_produk, harga, kategori, status FROM produk")
    data = cursor.fetchall()
    cursor.close()

    return render_template('data.html', data=data)

    # function menyimpan data API kedalam database
    # data_api = get_data_from_api()
    # if data_api is not None:
    #     save_data_to_database(data_api)
    #     return "Data berhasil disimpan ke database."
    # else:
    #     return "Gagal mengambil data dari API", 500
    
def get_data_from_api():
    # Informasi autentikasi
    username = "tesprogrammer260923C12"
    current_date = datetime.now()
    password = f"bisacoding-{current_date.day:02d}-{current_date.month:02d}-{current_date.year % 100:02d}"

    # URL API
    url = "https://recruitment.fastprint.co.id/tes/api_tes_programmer"

    password_md5 = hashlib.md5(password.encode()).hexdigest()

    # Menyiapkan data autentikasi
    auth_data = {
        "username": username,
        "password": password_md5
    }

    # Mengambil data dari API dengan autentikasi
    response = requests.post(url, data=auth_data)

    if response.status_code == 200:
        data_api = response.json()
        return data_api
    else:
        return None

def save_data_to_database(data):
    cursor = db_connection.cursor()
    # print(data)

    if 'data' in data and isinstance(data['data'], list):
        for item in data['data']:
            id_produk = item.get('id_produk', 0)
            nama_produk = item.get('nama_produk', '')  # Menggunakan get() untuk menghindari KeyError
            harga = item.get('harga', 0)  # Menggunakan get() untuk menghindari KeyError
            kategori = item.get('kategori', None)  # Menggunakan get() untuk menghindari KeyError
            status = item.get('status', None)  # Menggunakan get() untuk menghindari KeyError

            # Query SQL untuk menyimpan data ke tabel Produk
            insert_query = "INSERT INTO produk (id_produk, nama_produk, harga, kategori, status) VALUES (%s, %s, %s, %s, %s)"
            values = (id_produk, nama_produk, harga, kategori, status)

            try:
                cursor.execute(insert_query, values)
            except mysql.connector.Error as err :
                print(f"Error: {err}")

        db_connection.commit()
        cursor.close()
    else:
        print("Data tidak sesuai format yang diharapkan")

@app.route('/data_dijual', methods=['GET'])
def data_dijual():
    cursor = db_connection.cursor()
    cursor.execute("SELECT nama_produk, harga, kategori, status FROM produk WHERE status = 'bisa dijual'")
    datadijual = cursor.fetchall()
    cursor.close()

    return render_template('status_dijual.html', data_dijual=datadijual)

@app.route('/tambah_produk', methods=['GET', 'POST'])
def tambah_produk():
    if request.method == 'POST':
        nama_produk = request.form['nama_produk']
        harga = request.form['harga']
        kategori = request.form['kategori']
        status = request.form['status']

        if not nama_produk:
            return "Input tidak valid. Nama harus diisi."
        
        if not harga.isdigit():
            return "Input tidak valid. Harga harus berupa angka."
        
        insert_query = "INSERT INTO produk (nama_produk, harga, kategori, status) VALUES (%s, %s, %s, %s)"
        values = (nama_produk, harga, kategori, status)

        cursor = db_connection.cursor()
        try:
            cursor.execute(insert_query, values)
            db_connection.commit()
            cursor.close()

            # Notifikasi JavaScript bahwa data berhasil ditambahkan
            success_message = "Data berhasil ditambahkan."
            return render_template('tambah_produk.html', success_message=success_message)
        except mysql.connector.Error as err:
            return f"Error: {err}"
            
    return render_template('tambah_produk.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM produk WHERE id_produk = %s", (id,))
    data_produk = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        nama_produk = request.form['nama_produk']
        harga = request.form['harga']
        kategori = request.form['kategori']
        status = request.form['status']

        # Validasi inputan
        if not nama_produk:
            return "Input tidak valid. Nama harus diisi."
        
        if not harga.isdigit():
            return "Input tidak valid. Harga harus berupa angka."

        # Query SQL untuk memperbarui data produk
        update_query = "UPDATE produk SET nama_produk = %s, harga = %s, kategori = %s, status = %s WHERE id_produk = %s"
        values = (nama_produk, harga, kategori, status, id)

        cursor = db_connection.cursor()
        try:
            cursor.execute(update_query, values)
            db_connection.commit()
            cursor.close()

            # Notifikasi JavaScript bahwa data berhasil di edit
            success_message = "Data berhasil diedit."
            return render_template('edit.html', success_message=success_message)
        except mysql.connector.Error as err:
            return f"Error: {err}"

    return render_template('edit.html', data_produk=data_produk)

@app.route('/hapus/<int:id>', methods=['DELETE'])
def hapus_produk(id):
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM produk WHERE id_produk = %s", (id,))
    db_connection.commit()
    cursor.close()
    return jsonify({'message': 'Data berhasil dihapus'})

if __name__ == '__main__':
    app.run(debug=True)
