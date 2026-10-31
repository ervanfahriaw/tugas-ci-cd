# Python CRUD REST API — CI/CD Pipeline Lab

Aplikasi Python REST API mandiri (menggunakan standard library `http.server`) yang dirancang untuk laboratorium praktikum CI/CD menggunakan Jenkins, GitHub, Docker, dan ngrok.

---

## 📌 Fitur Aplikasi
- **Health Check**: Endpoint verifikasi keaktifan layanan.
- **CRUD Messages**: Manajemen data pesan teks sederhana.
- **Persistent Data**: Menggunakan JSON file storage yang dipasang ke named volume Docker (`production-api-data`).
- **Fitur Tugas D (Pengembangan)**:
  1. **Detail Message (`GET /messages/{index}`)**: Mengambil 1 pesan spesifik berdasarkan index (dengan respon 404 jika tidak ditemukan).
  2. **Automated Unit Testing (`test_app.py`)**: Pengujian unit otomatis untuk health check, payload validation, dan CRUD.
  3. **Docker Native HEALTHCHECK**: Pengecekan kesehatan container langsung di level Dockerfile.
  4. **Dynamic Image Tagging**: Penandaan image Docker dengan `BUILD_NUMBER`, `latest`, serta Git Commit SHA.

---

## 🚀 Endpoint API

| Method | Endpoint | Deskripsi | Status Code |
|---|---|---|---|
| `GET` | `/health` | Memeriksa status kesehatan server | 200 OK |
| `GET` | `/messages` | Mengambil seluruh daftar pesan | 200 OK |
| `GET` | `/messages/{index}` | Mengambil detail pesan berdasarkan index | 200 OK / 404 Not Found |
| `POST` | `/messages` | Menambahkan pesan baru (JSON: `{"message": "..."}`) | 201 Created / 400 Bad Request |
| `DELETE` | `/messages?index={n}` | Menghapus pesan pada indeks tertentu | 200 OK / 404 Not Found |

---

## 🧪 Contoh Pengujian Mandiri via `curl`

### 1. Health Check
```bash
curl -i http://localhost:5000/health
```

### 2. Tambah Pesan (Create)
```bash
curl -i -X POST http://localhost:5000/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Halo dari Praktikum CI/CD Jenkins!"}'
```

### 3. Baca Seluruh Pesan (List)
```bash
curl -s http://localhost:5000/messages
```

### 4. Baca Detail Pesan (Fitur Tugas D)
```bash
curl -s http://localhost:5000/messages/0
```

### 5. Hapus Pesan (Delete)
```bash
curl -i -X DELETE "http://localhost:5000/messages?index=0"
```

---

## 🛠️ Menjalankan Unit Test Lokal
```bash
python -m unittest test_app.py
```

---

## 💾 Pengujian Persistensi Data (Volume Testing)
Data pesan disimpan secara persisten di Docker named volume `production-api-data` pada direktori `/var/lib/backend_data`.
Bahkan ketika container dihentikan, dihapus (`docker rm`), atau di-redeploy melalui CI/CD pipeline, file `messages.json` tetap utuh.

