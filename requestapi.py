import requests
from app import Produk, db

# Informasi autentikasi
username = "tesprogrammer210923C10"
password = "bisacoding-12-20-21"

# URL API
url = "https://recruitment.fastprint.co.id/tes/api_tes_programmer"

# Mengambil data dari API dengan autentikasi
response = requests.get(url, auth=(username, password))

if response.status_code == 200:
    data_api = response.json()

    # Menyimpan data ke dalam database SQLAlchemy
    for data in data_api:
        produk = Produk(
            nama_produk=data['nama_produk'],
            harga=data['harga'],
            kategori_id=data['kategori_id'],
            status_id=data['status_id']
        )
        db.session.add(produk)

    db.session.commit()
else:
    print("Gagal mengambil data dari API.")
