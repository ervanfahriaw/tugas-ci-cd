# LAPORAN LENGKAP PRAKTIKUM CI/CD PIPELINE
## Otomasi CI/CD Menggunakan Jenkins, GitHub, Docker, dan ngrok

---

**Mata Kuliah / Lab**: Praktikum Continuous Integration & Continuous Deployment (CI/CD)  
**Dokumen Acuan**: Panduan Hands-On Praktikum CI/CD (`CICD_Jenkins.pdf`)  
**Penulis / Praktikan**: Ervan Fahrian (`ervanfahriaw`)  
**Repository GitHub**: [https://github.com/ervanfahriaw/tugas-ci-cd.git](https://github.com/ervanfahriaw/tugas-ci-cd.git)  
**Branch Utama**: `main`  
**Status Implementasi**: **100% Selesai & Terverifikasi (Tugas A, Tugas B, Tugas C, Tugas D.1, D.2, D.3, D.5)**  

---

## DAFTAR ISI
1. [Ringkasan Eksekutif & Tujuan Praktikum](#1-ringkasan-eksekutif--tujuan-praktikum)
2. [Arsitektur Sistem & Diagram Alur CI/CD](#2-arsitektur-sistem--diagram-alur-cicd)
3. [Implementasi Kode & Konfigurasi Pipeline](#3-implementasi-kode--konfigurasi-pipeline)
   - 3.1 [Aplikasi Python REST API (`app.py`)](#31-aplikasi-python-rest-api-apppy)
   - 3.2 [Otomasi Pengujian Unit (`test_app.py`) — Tugas D.2](#32-otomasi-pengujian-unit-test_apppy--tugas-d2)
   - 3.3 [Spesifikasi Container (`Dockerfile`) & Docker Native Healthcheck — Tugas D.3](#33-spesifikasi-container-dockerfile--docker-native-healthcheck--tugas-d3)
   - 3.4 [Declarative Pipeline as Code (`Jenkinsfile`) & Tag Commit SHA — Tugas D.5](#34-declarative-pipeline-as-code-jenkinsfile--tag-commit-sha--tugas-d5)
4. [Implementasi Tugas Praktikum (A, B, C, D)](#4-implementasi-tugas-praktikum-a-b-c-d)
   - 4.1 [Tugas A (Wajib) — Base CI/CD Pipeline](#41-tugas-a-wajib--base-cicd-pipeline)
   - 4.2 [Tugas B (Wajib) — Webhook Otomatis via Tunneling ngrok](#42-tugas-b-wajib--webhook-otomatis-via-tunneling-ngrok)
   - 4.3 [Tugas C (Wajib) — Uji Persistensi Data dengan Docker Named Volume](#43-tugas-c-wajib--uji-persistensi-data-dengan-docker-named-volume)
   - 4.4 [Tugas D (Pengembangan) — 4 Fitur Tambahan Terverifikasi](#44-tugas-d-pengembangan--4-fitur-tambahan-terverifikasi)
5. [Matriks Pengujian & Bukti Eksekusi (Empirical Evidence)](#5-matriks-pengujian--bukti-eksekusi-empirical-evidence)
   - 5.1 [Tabel Matriks Uji Endpoint API](#51-tabel-matriks-uji-endpoint-api)
   - 5.2 [Log Eksekusi Unit Test (5/5 Passed)](#52-log-eksekusi-unit-test-55-passed)
   - 5.3 [Log Console Jenkins Build Otomatis (#5 & #6)](#53-log-console-jenkins-build-otomatis-5--6)
   - 5.4 [Log Webhook Subscriber & Tunneling ngrok](#54-log-webhook-subscriber--tunneling-ngrok)
   - 5.5 [Bukti Persistensi Data Sebelum & Sesudah Redeployment](#55-bukti-persistensi-data-sebelum--sesudah-redeployment)
6. [Studi Kasus Masalah & Troubleshooting](#6-studi-kasus-masalah--troubleshooting)
   - 6.1 [Kasus 1: Permission Denied pada Host Docker Socket (`docker.sock`)](#61-kasus-1-permission-denied-pada-host-docker-socket-dockersock)
   - 6.2 [Kasus 2: Isolasi Network Namespace & Health Check Cross-Container](#62-kasus-2-isolasi-network-namespace--health-check-cross-container)
   - 6.3 [Kasus 3: Windows Hyper-V Virtual Interface & Port Forwarding](#63-kasus-3-windows-hyper-v-virtual-interface--port-forwarding)
7. [Jawaban Pertanyaan Analisis (8 Soal Akademik)](#7-jawaban-pertanyaan-analisis-8-soal-akademik)
8. [Checklist Kelayakan Sebelum Pengumpulan (Submission Checklist)](#8-checklist-kelayakan-sebelum-pengumpulan-submission-checklist)

---

## 1. Ringkasan Eksekutif & Tujuan Praktikum

Praktikum ini bertujuan untuk merancang, mengimplementasikan, dan menguji rantai otomasi **Continuous Integration / Continuous Deployment (CI/CD)** secara penuh. Pipeline mengintegrasikan repository Git pada GitHub, server otomasi Jenkins (berjalan di dalam kontainer Docker), mekanisme tunneling publik ngrok, dan Docker Engine sebagai target deployment aplikasi Python REST API mandiri.

### Capaian Kunci:
1. **Otomasi Pemicu Penuh (Zero-Click Trigger)**: Setiap perintah `git push` pada branch `main` langsung memicu pipeline Jenkins secara otomatis melalui GitHub Webhook yang disalurkan via ngrok HTTPS tunnel tanpa intervensi manual.
2. **Keamanan Kredensial (Least Privilege)**: Menggunakan GitHub Fine-grained Personal Access Token (PAT) dengan hak akses minimum (`Contents: Read-only`), tersimpan secara terenkripsi pada Jenkins Credentials Store (`github-pat-readonly`). Tidak ada token, secret, atau authtoken yang terekspos di source code, riwayat Git commit, maupun tampilan antarmuka publik.
3. **Jaminan Kualitas Kode Terintegrasi**: Tahap CI mencakup verifikasi kompilasi sintaks Python (`py_compile`) serta 5 pengujian unit otomatis (`unittest`) yang memvalidasi integritas logika API sebelum container image dibangun.
4. **Ketahanan Data Operasional (Data Persistence)**: Container aplikasi runtime menggunakan Docker named volume (`production-api-data`) yang dipetakan ke `/var/lib/backend_data`. Terbukti secara empiris bahwa data pesan tersimpan tidak hilang saat container lama dihentikan, dihapus (`docker rm`), dan diperbarui dengan container baru hasil build pipeline.
5. **Penyelesaian Fitur Pengembangan (Tugas D)**: Mengimplementasikan 4 opsi pengembangan (melampaui syarat minimal 2 opsi):
   - Endpoint Detail Pesan `GET /messages/{index}` dengan penanganan error status 404/400.
   - Otomasi pengujian unit (`test_app.py`) mencakup 5 test cases.
   - Pemeriksaan kesehatan kontainer ganda: Docker native `HEALTHCHECK` dan curl HTTP probe dari Jenkins.
   - Pelabelan citra kontainer dinamis berbasis Git Commit SHA (`python-crud-api:61b028b`).

---

## 2. Arsitektur Sistem & Diagram Alur CI/CD

Arsitektur praktikum dirancang menggunakan pola hybrid host-container dengan isolasi jaringan Docker bridge (`jenkins-net`):

```
+---------------------------------------------------------------------------------------------------+
| LINGKUNGAN PENGEMBANG (Host Windows & WSL2 Ubuntu)                                                |
|                                                                                                   |
|  [ Developer ] --( git push )--> [ GitHub Remote Repository: ervanfahriaw/tugas-ci-cd ]           |
|                                         |                                                         |
|                                         v (HTTP POST PushEvent)                                   |
|                          [ ngrok Cloud Edge Public Tunnel ]                                       |
|                                         |                                                         |
|                                         v (HTTPS -> HTTP Forward)                                 |
|                       [ ngrok Client Daemon (Port 8080) ]                                         |
|                                         |                                                         |
|                                         v (Forward to Jenkins)                                    |
|   +-------------------------------------------------------------------------------------------+   |
|   | DOCKER BRIDGE NETWORK: jenkins-net                                                        |   |
|   |                                                                                           |   |
|   |  +-------------------------------------+      +-----------------------------------------+ |   |
|   |  | Container: jenkins-server           |      | Container: production-api-container     | |   |
|   |  | - Port: 8080, 50000                 |      | - Port: 5000:5000                       | |   |
|   |  | - Volume: jenkins-data              |      | - Volume: production-api-data           | |   |
|   |  | - Mount: /var/run/docker.sock       |      |           (/var/lib/backend_data)       | |   |
|   |  | - Plugin: GitHub Hook Subscriber    |      | - Health: CMD curl localhost:5000/health| |   |
|   |  +-------------------------------------+      +-----------------------------------------+ |   |
|   |                   |                                                 ^                     |   |
|   |                   +---( docker build / docker run via host socket )-+                     |   |
|   |                   +---( curl http://production-api-container:5000 )--+                     |   |
|   +-------------------------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------------------------+
```

### Tabel Komponen, Alamat, dan Peran Sistem

| Komponen | Alamat / Port Jaringan | Kredensial / Identitas | Peran Utama |
|---|---|---|---|
| **GitHub Repo** | `https://github.com/ervanfahriaw/tugas-ci-cd.git` | Akun: `ervanfahriaw` | Source Code Management (SCM) & Webhook Emitter |
| **ngrok Tunnel** | `https://subtext-tableful-smashing.ngrok-free.dev` | Authtoken tersimpan di client ngrok | Reverse proxy pembuka akses publik ke Jenkins lokal |
| **Jenkins Server** | `http://localhost:8080` (Internal port 8080) | Credential ID: `github-pat-readonly` | Otomasi eksekusi pipeline CI/CD (Checkout, Test, Build, Deploy) |
| **Docker Engine** | Unix Socket: `/var/run/docker.sock` | Group GID 106 (`docker`) | Container runtime pembangun image & pengelola container |
| **Aplikasi REST API** | `http://localhost:5000` (Container internal: 5000) | Port mapping: `0.0.0.0:5000->5000/tcp` | Runtime backend API dengan endpoint CRUD & Health |
| **Named Volume** | Host path: `/var/lib/docker/volumes/...` | Driver: `local` (`production-api-data`) | Penyimpanan persisten file `messages.json` |

---

## 3. Implementasi Kode & Konfigurasi Pipeline

### 3.1 Aplikasi Python REST API (`app.py`)
Aplikasi REST API dibangun mandiri tanpa dependensi pihak ketiga menggunakan modul bawaan Python `http.server`, `urllib.parse`, `json`, dan `pathlib`.

Fitur yang diimplementasikan:
- `GET /health` dan `GET /`: Health check probe menghasilkan JSON status aktif.
- `GET /messages`: Menampilkan daftar seluruh pesan beserta total item.
- `GET /messages/{index}`: **Fitur Tugas D.1** mengambil data spesifik berdasarkan indeks array, menghasilkan `200 OK`, `404 Not Found` jika indeks di luar jangkauan, atau `400 Bad Request` jika format bukan angka.
- `POST /messages`: Menyimpan pesan baru ke storage persisten JSON dengan validasi non-empty dan maksimal 500 karakter.
- `DELETE /messages?index={index}`: Menghapus pesan berdasarkan indeks query parameter.
- Konfigurasi path file data fleksibel melalui variabel lingkungan `DATA_FILE`, default `/var/lib/backend_data/messages.json`.

```python
# Potongan Kode Kunci: Detail Endpoint & Storage Management (app.py)
DATA_FILE = Path(os.getenv("DATA_FILE", "/var/lib/backend_data/messages.json"))

def read_messages():
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

def write_messages(messages):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(messages, indent=2, ensure_ascii=False), encoding="utf-8")

# Tugas D.1: Endpoint GET /messages/{index}
if self.path.startswith("/messages/"):
    parts = self.path.split("/")
    if len(parts) == 3 and parts[2].isdigit():
        index = int(parts[2])
        messages = read_messages()
        if 0 <= index < len(messages):
            return self.send_json(200, {"index": index, "item": messages[index]})
        return self.send_json(404, {"error": "Message not found"})
    return self.send_json(400, {"error": "Invalid index path parameter"})
```

### 3.2 Otomasi Pengujian Unit (`test_app.py`) — Tugas D.2
Pengujian unit otomatis diintegrasikan langsung ke dalam build pipeline menggunakan framework standar `unittest`. Server API dijalankan di background thread selama pengetesan dengan temporary file storage terisolasi.

Daftar 5 Uji Unit Otomatis:
1. `test_health_endpoint`: Memverifikasi respons HTTP 200 dan payload status active dari `/health`.
2. `test_create_and_get_messages`: Memverifikasi operasi POST penambahan pesan (201 Created) dan GET list (200 OK).
3. `test_get_message_by_index_detail`: Memverifikasi endpoint detail pesan indeks spesifik (200 OK) dan respons error (404 Not Found) untuk indeks yang tidak terdaftar.
4. `test_post_empty_message_validation`: Memvalidasi respons proteksi HTTP 400 Bad Request saat payload message kosong.
5. `test_delete_message`: Memverifikasi operasi penghapusan item melalui parameter query string.

### 3.3 Spesifikasi Container (`Dockerfile`) & Docker Native Healthcheck — Tugas D.3
Dockerfile menggunakan base image ringan `python:3.11-slim`, menyertakan utilitas `curl`, serta mendefinisikan instruksi native `HEALTHCHECK`.

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app.py .

EXPOSE 5000

# Tugas D.3: Docker Native HEALTHCHECK
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"]
```

### 3.4 Declarative Pipeline as Code (`Jenkinsfile`) & Tag Commit SHA — Tugas D.5
Pipeline terdiri dari 5 stages terstruktur:
1. `Checkout Code`: Mengambil commit terbaru dari GitHub menggunakan kredensial Jenkins PAT.
2. `Code Syntax & Automated Tests`: Menjalankan validasi `python3 -m py_compile app.py` dan `python3 -m unittest test_app.py`.
3. `Build Docker Image`: Menangkap Git Commit SHA pendek (`git rev-parse --short HEAD`), membangun Docker image dengan tag `${BUILD_NUMBER}`, `latest`, dan commit SHA (Tugas D.5).
4. `Automated Deployment`: Menghentikan container aktif lama, memastikan Docker named volume `production-api-data` tersedia, dan menjalankan container baru di dalam bridge network `jenkins-net`.
5. `Health Check`: Menguji ketersediaan layanan melalui HTTP probe `curl -fsS http://${CONTAINER_NAME}:5000/health` dan menampilkan log runtime container.

```groovy
pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
        REGISTRY_NAME    = 'python-crud-api'
        CONTAINER_NAME   = 'production-api-container'
        PORT_MAPPING     = '5000:5000'
        VOLUME_NAME      = 'production-api-data'
        NETWORK_NAME     = 'jenkins-net'
    }

    stages {
        stage('1. Checkout Code') {
            steps {
                echo 'Checking out source code from GitHub...'
                checkout scm
            }
        }

        stage('2. Code Syntax & Automated Tests') {
            steps {
                echo 'Running Python syntax verification and unit tests...'
                sh '''
                    python3 -m py_compile app.py
                    python3 -m unittest test_app.py
                '''
            }
        }

        stage('3. Build Docker Image') {
            steps {
                script {
                    def gitCommit = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    echo "Building Docker image with build number ${BUILD_NUMBER} and commit SHA ${gitCommit}..."
                    sh "docker build -t ${REGISTRY_NAME}:${BUILD_NUMBER} ."
                    sh "docker tag ${REGISTRY_NAME}:${BUILD_NUMBER} ${REGISTRY_NAME}:latest"
                    sh "docker tag ${REGISTRY_NAME}:${BUILD_NUMBER} ${REGISTRY_NAME}:${gitCommit}"
                }
            }
        }

        stage('4. Automated Deployment') {
            steps {
                sh """
                    echo "Stopping and removing existing container if present..."
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    echo "Ensuring named volume exists for data persistence..."
                    docker volume create ${VOLUME_NAME}
                    echo "Starting production container with named volume on ${NETWORK_NAME} network..."
                    docker run -d \\
                        --name ${CONTAINER_NAME} \\
                        --network ${NETWORK_NAME} \\
                        -p ${PORT_MAPPING} \\
                        -v ${VOLUME_NAME}:/var/lib/backend_data \\
                        --restart unless-stopped \\
                        ${REGISTRY_NAME}:latest
                """
            }
        }

        stage('5. Health Check') {
            steps {
                echo 'Waiting for container application startup...'
                sh 'sleep 3'
                echo 'Performing automated HTTP health check...'
                sh "curl -fsS http://${CONTAINER_NAME}:5000/health"
                echo 'Displaying recent container runtime logs...'
                sh "docker logs --tail 20 ${CONTAINER_NAME}"
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully. Deployment is healthy and active.'
        }
        failure {
            echo 'Pipeline execution failed. Review stage logs above.'
        }
    }
}
```

---

## 4. Implementasi Tugas Praktikum (A, B, C, D)

### 4.1 Tugas A (Wajib) — Base CI/CD Pipeline
- **Status**: Berhasil 100%.
- Pipeline `python-crud-api-pipeline` berhasil didefinisikan sebagai *Pipeline script from SCM* yang mengarah ke `https://github.com/ervanfahriaw/tugas-ci-cd.git`.
- Tahap checkout berhasil mengambil source code menggunakan credential `github-pat-readonly`.
- Tahap validasi sintaks dan unit tests berhasil mengeksekusi 5 unit tests tanpa kegagalan.
- Image Docker berhasil dibangun, di-deploy secara otomatis ke container `production-api-container`, dan lulus tahap pemeriksaan kesehatan dengan status `200 OK`.

### 4.2 Tugas B (Wajib) — Webhook Otomatis via Tunneling ngrok
- **Status**: Berhasil 100%.
- Tunnel ngrok aktif menghubungkan internet ke port 8080 Jenkins: `https://subtext-tableful-smashing.ngrok-free.dev`.
- GitHub Webhook dikonfigurasikan dengan Payload URL `https://subtext-tableful-smashing.ngrok-free.dev/github-webhook/` pada event `push`.
- Bukti pengujian otomatis:
  - Commit `553f615`: Dipush ke GitHub `main`, Webhook mengirim `PushEvent` (status `200 OK`), Jenkins otomatis memulai **Build #5** (`Started by GitHub push by ervanfahriaw`) dan selesai dengan status **SUCCESS**.
  - Commit `61b028b`: Dipush ke GitHub `main`, Webhook otomatis memicu **Build #6** tanpa klik manual tombol "Build Now". Seluruh tahapan pipeline berjalan sukses.

### 4.3 Tugas C (Wajib) — Uji Persistensi Data dengan Docker Named Volume
- **Status**: Berhasil 100%.
- **Pengujian Tahap 1**: Dua pesan diinputkan ke API container aktif melalui perintah HTTP POST:
  - Pesan 1: `"Halo dari CI/CD Jenkins Pipeline!"`
  - Pesan 2: `"Data persisten kedua untuk testing volume"`
  - Total data diverifikasi melalui `GET /messages` (total: 2 pesan).
- **Pengujian Tahap 2 (Redeployment Ekstrem)**:
  - Dilakukan push commit baru `61b028b` ke GitHub yang memicu pipeline otomatis Build #6.
  - Pada Stage 4, Jenkins mengeksekusi:
    - `docker stop production-api-container`
    - `docker rm production-api-container` (Container beserta lapisan layer writable-nya dihancurkan total).
    - Menjalankan container baru dari image `python-crud-api:6` yang me-mount kembali volume `production-api-data:/var/lib/backend_data`.
- **Pengujian Tahap 3 (Verifikasi Keutuhan Data Pasca Redeploy)**:
  - Perintah `curl -s http://localhost:5000/messages` dieksekusi pada container baru.
  - Hasil: Kedua pesan yang dibuat sebelum container lama dihapus **tetap ada secara utuh 100%**.
- **Analisis Teoretis**:
  Container layer bersifat *ephemeral* (sementara) dan terikat pada runtime ID container. Ketika container dihapus, layer CoW (Copy-on-Write) ikut musnah. Sebaliknya, Docker *named volume* beroperasi langsung pada filesystem host di luar lifecycle container (`/var/lib/docker/volumes/production-api-data/_data`). Karena pipeline tidak memanggil `docker volume rm`, data di volume tetap persisten dan terisolasi dari proses build/redeploy.

### 4.4 Tugas D (Pengembangan) — 4 Fitur Tambahan Terverifikasi

| Fitur | Kategori Tugas D | Status | Rincian Implementasi & Bukti |
|---|---|---|---|
| **1. Detail Endpoint & Filter** | Pilihan 1 | **TERVERIFIKASI** | Endpoint `GET /messages/{index}` diimplementasikan di `app.py`. Menghasilkan `200 OK` untuk index valid, `404 Not Found` untuk index tidak terdaftar, dan `400 Bad Request` jika index bukan integer. |
| **2. Automated Unit Testing** | Pilihan 2 | **TERVERIFIKASI** | Skrip `test_app.py` berisi 5 unit test menggunakan framework `unittest`. Diintegrasikan pada Stage 2 `Jenkinsfile`. Semua test lolos (Ran 5 tests, OK). |
| **3. Docker Native HEALTHCHECK** | Pilihan 3 | **TERVERIFIKASI** | Didefinisikan pada Dockerfile: `CMD curl -f http://localhost:5000/health || exit 1`. Status container terverifikasi melalui `docker inspect`: `Status: running, Health: healthy`. Dibandingkan dengan curl probe Jenkins pada bab analisis. |
| **4. Tag Commit SHA Dinamis** | Pilihan 5 | **TERVERIFIKASI** | Ekstraksi Git SHA (`git rev-parse --short HEAD`) di Stage 3 Jenkinsfile. Menghasilkan tag image ganda: `python-crud-api:BUILD_NUMBER`, `python-crud-api:latest`, dan `python-crud-api:61b028b`. |

---

## 5. Matriks Pengujian & Bukti Eksekusi (Empirical Evidence)

### 5.1 Tabel Matriks Uji Endpoint API

| No | Endpoint / Aksi | HTTP Method | Payload / Parameter | Status Code Diharapkan | Status Code Aktual | Respons Payload Aktual | Status Uji |
|---|---|---|---|---|---|---|---|
| 1 | `/health` | `GET` | - | `200 OK` | `200 OK` | `{"status": "active", "service": "Backend API"}` | **PASSED** |
| 2 | `/messages` (Awal) | `GET` | - | `200 OK` | `200 OK` | `{"messages": [], "total": 0}` | **PASSED** |
| 3 | `/messages` (Tambah 1) | `POST` | `{"message": "Halo dari CI/CD Jenkins Pipeline!"}` | `201 Created` | `201 Created` | `{"status": "created", "message": {"message": "...", "created_at": "..."}}` | **PASSED** |
| 4 | `/messages` (Tambah 2) | `POST` | `{"message": "Data persisten kedua untuk testing volume"}` | `201 Created` | `201 Created` | `{"status": "created", "message": {"message": "...", "created_at": "..."}}` | **PASSED** |
| 5 | `/messages` (List 2 data) | `GET` | - | `200 OK` | `200 OK` | `{"messages": [... 2 items ...], "total": 2}` | **PASSED** |
| 6 | `/messages/0` (Detail ID 0) | `GET` | - | `200 OK` | `200 OK` | `{"index": 0, "item": {"message": "Halo dari CI/CD Jenkins Pipeline!", ...}}` | **PASSED** |
| 7 | `/messages/1` (Detail ID 1) | `GET` | - | `200 OK` | `200 OK` | `{"index": 1, "item": {"message": "Data persisten kedua untuk testing volume", ...}}` | **PASSED** |
| 8 | `/messages/99` (ID Invalid) | `GET` | - | `404 Not Found` | `404 Not Found` | `{"error": "Message not found"}` | **PASSED** |
| 9 | `/messages` (Body Kosong) | `POST` | `{"message": ""}` | `400 Bad Request` | `400 Bad Request` | `{"error": "message must not be empty"}` | **PASSED** |
| 10 | `/messages?index=0` (Delete) | `DELETE` | `index=0` | `200 OK` | `200 OK` | `{"status": "deleted", "removed": {"message": "Halo dari CI/CD..."}}` | **PASSED** |
| 11 | `/messages` (Pasca Delete) | `GET` | - | `200 OK` | `200 OK` | `{"messages": [{"message": "Data persisten kedua...", ...}], "total": 1}` | **PASSED** |

### 5.2 Log Eksekusi Unit Test (5/5 Passed)
Eksekusi pengujian otomatis pada Stage 2 Jenkinsfile:
```
Running Python syntax verification and unit tests...
+ command -v python3
+ python3 -m py_compile app.py
+ python3 -m unittest test_app.py
[31/Oct/2026 02:42:57] "DELETE /messages?index=0 HTTP/1.1" 200 -
.[31/Oct/2026 02:42:57] "GET /messages/0 HTTP/1.1" 200 -
[31/Oct/2026 02:42:57] "GET /messages/99 HTTP/1.1" 404 -
.[31/Oct/2026 02:42:57] "GET /health HTTP/1.1" 200 -
.[31/Oct/2026 02:42:57] "POST /messages HTTP/1.1" 400 -
.[31/Oct/2026 02:42:57] "POST /messages HTTP/1.1" 201 -
.
----------------------------------------------------------------------
Ran 5 tests in 0.528s

OK
```

### 5.3 Log Console Jenkins Build Otomatis (#5 & #6)
Cuplikan log konsol Build #6 yang dipicu otomatis oleh webhook GitHub:
```
Started by GitHub push by ervanfahriaw
Obtained Jenkinsfile from git https://github.com/ervanfahriaw/tugas-ci-cd.git
[Pipeline] Start of Pipeline
[Pipeline] node
Running on Jenkins in /var/jenkins_home/workspace/python-crud-api-pipeline
[Pipeline] { (Declarative: Checkout SCM)
[Pipeline] checkout
using credential github-pat-readonly
Fetching changes from the remote Git repository
 > git fetch --tags --force --progress -- https://github.com/ervanfahriaw/tugas-ci-cd.git +refs/heads/*:refs/remotes/origin/*
Checking out Revision 61b028b9c4154da75803ca7d14ea4b046da542b5 (refs/remotes/origin/main)
Commit message: "docs: update README with volume persistence testing documentation"

[Pipeline] stage: (1. Checkout Code)
Checking out source code from GitHub...

[Pipeline] stage: (2. Code Syntax & Automated Tests)
Running Python syntax verification and unit tests...
+ python3 -m py_compile app.py
+ python3 -m unittest test_app.py
Ran 5 tests in 0.528s - OK

[Pipeline] stage: (3. Build Docker Image)
+ git rev-parse --short HEAD
Building Docker image with build number 6 and commit SHA 61b028b...
+ docker build -t python-crud-api:6 .
Successfully built ae76e665bfb1
Successfully tagged python-crud-api:6
+ docker tag python-crud-api:6 python-crud-api:latest
+ docker tag python-crud-api:6 python-crud-api:61b028b

[Pipeline] stage: (4. Automated Deployment)
Stopping and removing existing container if present...
+ docker stop production-api-container
production-api-container
+ docker rm production-api-container
production-api-container
Ensuring named volume exists for data persistence...
+ docker volume create production-api-data
production-api-data
Starting production container with named volume on jenkins-net network...
+ docker run -d --name production-api-container --network jenkins-net -p 5000:5000 -v production-api-data:/var/lib/backend_data --restart unless-stopped python-crud-api:latest
aecf9cd0927a25fe8da3273755f4cfa5156da07b48a11821c6b3e8abb8c67a5b

[Pipeline] stage: (5. Health Check)
Waiting for container application startup...
+ sleep 3
Performing automated HTTP health check...
+ curl -fsS http://production-api-container:5000/health
{"status": "active", "service": "Backend API"}
Displaying recent container runtime logs...
+ docker logs --tail 20 production-api-container
Backend API listening on 0.0.0.0:5000
[31/Oct/2026 02:43:14] "GET /health HTTP/1.1" 200 -

[Pipeline] echo
Pipeline completed successfully. Deployment is healthy and active.
Finished: SUCCESS
```

### 5.4 Log Webhook Subscriber & Tunneling ngrok
Bukti log penerimaan Webhook dari GitHub IP oleh daemon Jenkins di `/var/jenkins_home`:
```
2026-10-31 02:31:15.284+0000 [id=18] INFO o.j.p.g.w.s.PingGHEventSubscriber#onEvent: PING webhook received from repo <https://github.com/ervanfahriaw/tugas-ci-cd>!
2026-10-31 02:40:26.868+0000 [id=15] INFO o.j.p.g.w.s.DefaultPushGHEventSubscriber#onEvent: Received PushEvent for https://github.com/ervanfahriaw/tugas-ci-cd from 140.82.115.27 ⇒ https://subtext-tableful-smashing.ngrok-free.dev:8080/github-webhook/
2026-10-31 02:40:28.076+0000 [id=373] INFO c.c.jenkins.GitHubPushTrigger$1#run: SCM changes detected in python-crud-api-pipeline. Triggering #5
2026-10-31 02:42:45.593+0000 [id=78] INFO o.j.p.g.w.s.DefaultPushGHEventSubscriber#onEvent: Received PushEvent for https://github.com/ervanfahriaw/tugas-ci-cd from 140.82.115.31 ⇒ https://subtext-tableful-smashing.ngrok-free.dev:8080/github-webhook/
2026-10-31 02:42:46.763+0000 [id=497] INFO c.c.jenkins.GitHubPushTrigger$1#run: SCM changes detected in python-crud-api-pipeline. Triggering #6
```

### 5.5 Bukti Persistensi Data Sebelum & Sesudah Redeployment
1. **Sebelum Redeployment (Container ID: `39726ede2cc3`):**
   ```bash
   $ curl -s http://localhost:5000/messages
   {
     "messages": [
       {"message": "Halo dari CI/CD Jenkins Pipeline!", "created_at": "2026-10-31T02:42:03.656147+00:00"},
       {"message": "Data persisten kedua untuk testing volume", "created_at": "2026-10-31T02:42:08.275631+00:00"}
     ],
     "total": 2
   }
   ```
2. **Eksekusi Redeployment**:
   Pipeline Build #6 menghancurkan container lama (`docker rm production-api-container`) dan membuat container baru (`aecf9cd0927a`).
3. **Sesudah Redeployment pada Container Baru (Container ID: `aecf9cd0927a`):**
   ```bash
   $ curl -s http://localhost:5000/messages
   {
     "messages": [
       {"message": "Halo dari CI/CD Jenkins Pipeline!", "created_at": "2026-10-31T02:42:03.656147+00:00"},
       {"message": "Data persisten kedua untuk testing volume", "created_at": "2026-10-31T02:42:08.275631+00:00"}
     ],
     "total": 2
   }
   ```
   *Data terbukti 100% utuh tanpa ada satu pun record yang hilang.*

---

## 6. Studi Kasus Masalah & Troubleshooting

### 6.1 Kasus 1: Permission Denied pada Host Docker Socket (`docker.sock`)
- **Gejala Masalah**: Pada Build #3, pipeline gagal pada Stage 3 (Build Docker Image) dengan error:
  `Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock`.
- **Akar Masalah**: Docker daemon di host Linux (WSL2) dimiliki oleh group `docker` yang memiliki Group ID (GID) `106`. Di dalam container resmi `jenkins/jenkins:lts-jdk17`, proses build dijalankan oleh user bawaan `jenkins` (UID `1000`). User ini belum didaftarkan sebagai anggota group dengan GID 106 di dalam container, sehingga kernel Linux menolak akses baca-tulis ke berkas UNIX socket `/var/run/docker.sock`.
- **Solusi yang Diterapkan**:
  1. Menambahkan user `jenkins` ke group GID 106 di dalam container Jenkins:
     `docker exec -u 0 jenkins-server usermod -aG 106 jenkins`
  2. Memberikan izin akses longgar pada socket host untuk sesi lab:
     `chmod 666 /var/run/docker.sock`
  3. Memasang binary CLI `docker` dan interpreter `python3` ke dalam container Jenkins agar tahap build dan syntax check dapat dieksekusi langsung oleh agent.

### 6.2 Kasus 2: Isolasi Network Namespace & Health Check Cross-Container
- **Gejala Masalah**: Pada Build #4, seluruh tahapan build dan deployment container berhasil, namun pipeline gagal pada Stage 5 (Health Check) dengan error:
  `curl: (7) Failed to connect to localhost port 5000 after 1 ms: Could not connect to server`.
- **Akar Masalah**: Jenkins berjalan di dalam sebuah container terisolasi (`jenkins-server`). Ketika Jenkinsfile mengeksekusi `curl http://localhost:5000/health`, kata kunci `localhost` merujuk pada *network namespace loopback* milik container Jenkins itu sendiri, bukan port host ataupun container aplikasi. Karena di dalam container Jenkins tidak ada proses yang mendengarkan port 5000, koneksi langsung ditolak (*connection refused*).
- **Solusi yang Diterapkan**:
  1. Memanfaatkan Docker bridge network bersama, yaitu `jenkins-net` yang telah dibuat pada Fase 4.
  2. Mengubah perintah penjalanan container di Stage 4 `Jenkinsfile` dengan menyertakan argumen `--network jenkins-net`.
  3. Mengubah target health check di Stage 5 `Jenkinsfile` dari `localhost:5000` menjadi nama DNS internal container: `http://${CONTAINER_NAME}:5000/health`.
  4. Docker Embedded DNS Server secara otomatis me-resolve nama `production-api-container` ke alamat IP internalnya di dalam bridge network `jenkins-net`, sehingga curl berhasil memperoleh status HTTP 200 OK.

### 6.3 Kasus 3: Windows Hyper-V Virtual Interface & Port Forwarding
- **Gejala Masalah**: Pengujian akses browser host Windows ke URL Jenkins WSL2 `http://172.24.103.207:8080` mengalami timeout (`ERR_CONNECTION_TIMED_OUT`).
- **Akar Masalah**: Adapter virtual network switch Hyper-V Windows menyaring (filter) paket TCP masuk ke subnet internal WSL2 karena kebijakan Windows Firewall.
- **Solusi yang Diterapkan**:
  Membuat script TCP loopback reverse proxy ringan (`proxy.py`) di host Windows yang mendengarkan pada `127.0.0.1:8081` dan menyalurkan aliran byte TCP secara bidirectional langsung ke socket WSL2 `172.24.103.207:8080`. Melalui jalur ini, akses browser lokal dan pemantauan antarmuka Jenkins berjalan stabil tanpa hambatan firewall.

---

## 7. Jawaban Pertanyaan Analisis (8 Soal Akademik)

### Soal 1: Jelaskan urutan peristiwa dari `git push` hingga container baru berjalan.
**Jawaban**:
Rangkaian peristiwa dari eksekusi `git push` hingga aplikasi berjalan di container baru adalah sebagai berikut:
1. **Developer Push**: Pengembang mengeksekusi `git push origin main` dari mesin lokal, mengirim commit objek Git ke repository GitHub remote.
2. **Pemicu Event GitHub**: GitHub menerima commit, memperbarui referensi branch `main`, dan memeriksa konfigurasi Webhook yang terdaftar. Mengetahui ada event `push`, GitHub mengemas metadata commit ke dalam format JSON payload.
3. **Pengiriman Payload Webhook**: GitHub mengirimkan HTTP POST request ke alamat Payload URL publik: `https://subtext-tableful-smashing.ngrok-free.dev/github-webhook/`.
4. **Tunneling Terowongan ngrok**: Server ngrok di cloud menerima request HTTPS, mencocokkan sesi terowongan aktif, dan meneruskan paket ke agen ngrok lokal di komputer pengembang, yang selanjutnya mem-forward request ke `http://localhost:8080/github-webhook/`.
5. **Penerimaan oleh Jenkins**: Plugin `GitHub Integration` di Jenkins menerima event push melalui subscriber HTTP, mencocokkan URL repositori Git, dan memicu eksekusi antrean job pada pipeline `python-crud-api-pipeline`.
6. **Stage 1 (Checkout Code)**: Jenkins agent mengalokasikan workspace, menggunakan credential `github-pat-readonly` untuk melakukan autentikasi ke GitHub over HTTPS, dan men-checkout source code pada commit SHA terbaru.
7. **Stage 2 (Syntax & Unit Test Verification)**: Agent memvalidasi keabsahan sintaks via `python3 -m py_compile app.py` dan mengeksekusi 5 pengujian unit `python3 -m unittest test_app.py`. Jika ditemukan error logika atau sintaks, build langsung dihentikan (*fail-fast*).
8. **Stage 3 (Build Docker Image)**: Jenkins berinteraksi dengan Docker daemon host melalui socket `/var/run/docker.sock` untuk membangun image `python-crud-api:${BUILD_NUMBER}` berdasarkan instruksi `Dockerfile`, lalu memberikan tag `latest` dan tag Git Commit SHA.
9. **Stage 4 (Automated Deployment)**: Jenkins menghentikan container lama yang sedang berjalan (`docker stop production-api-container`), menghapus instans container lama (`docker rm`), memastikan ketersediaan volume persisten `production-api-data`, lalu menjalankan container baru dengan perintah `docker run` dengan port mapping `5000:5000`, network `jenkins-net`, dan volume mount `/var/lib/backend_data`.
10. **Stage 5 (Health Check Probe)**: Jenkins memberi jeda startup (`sleep 3`) lalu mengirim probe HTTP `curl -fsS http://production-api-container:5000/health`. Setelah respons `200 OK` diterima, pipeline mencatat status `Finished: SUCCESS`.

---

### Soal 2: Apa perbedaan PAT, webhook secret, dan ngrok authtoken?
**Jawaban**:
Ketiganya memiliki tujuan keamanan, arah komunikasi, dan lapisan operasional yang berbeda:
- **Personal Access Token (PAT)**:
  - *Peran*: Kredensial autentikasi pengguna GitHub yang digunakan oleh Jenkins (arah **Jenkins -> GitHub**) untuk mendapatkan hak membaca (*read-only*) atau menulis pada repository privat melalui protokol Git over HTTPS.
  - *Sifat*: Menggantikan password akun dengan masa berlaku tertentu dan hak akses (scope) granular.
- **Webhook Secret**:
  - *Peran*: Kunci rahasia bersama (*shared secret*) yang digunakan GitHub untuk menghasilkan tanda tangan kriptografis HMAC-SHA256 pada header `X-Hub-Signature-256` dari setiap HTTP request webhook (arah **GitHub -> Jenkins**).
  - *Sifat*: Digunakan oleh Jenkins untuk memvalidasi integritas dan keaslian payload, memastikan bahwa permintaan webhook benar-benar dikirim oleh GitHub dan bukan hasil pemalsuan (*spoofing*) dari pihak ketiga di internet.
- **ngrok Authtoken**:
  - *Peran*: Token autentikasi akun ngrok yang digunakan oleh client ngrok lokal ke server cloud ngrok pada lapisan **infrastruktur/jaringan**.
  - *Sifat*: Berfungsi membuka terowongan tunneling publik aman (HTTPS URL) yang menghubungkan lalu lintas internet publik ke port server internal lokal (localhost:8080), serta mengatur batas kuota dan fitur tunneling.

---

### Soal 3: Mengapa PAT read-only cukup untuk checkout source code, tetapi tidak cukup untuk push kembali ke repository?
**Jawaban**:
- Operasi `checkout` atau `git fetch` pada dasarnya adalah operasi *baca* (read) metadata Git, tree objek, commit hash, dan blob file. Dalam prinsip rekayasa perangkat lunak dan arsitektur CI, Jenkins bertindak sebagai *consumer* kode yang hanya memerlukan hak untuk mengunduh versi snapshot source code. Izin `Contents: Read-only` dan `Metadata: Read-only` menyediakan otoritas penuh bagi Git client untuk menarik data tanpa memerlukan hak modifikasi.
- Menerapkan izin read-only mematuhi prinsip keamanan **Least Privilege** (hak akses terendah). Jika credential Jenkins disusupi penyerang, repositori sumber tidak dapat diubah atau disisipkan kode jahat.
- Sebaliknya, operasi `git push` merupakan operasi *tulis* (write) yang memodifikasi pointer branch remote refs, menambahkan commit hash baru ke riwayat repository, dan mengubah status remote GitHub. GitHub API secara ketat memeriksa otorisasi tulis; jika token hanya memiliki hak *Read-only*, GitHub menolak transaksi dengan kode status `HTTP 403 Forbidden` untuk mencegah modifikasi data yang tidak sah.

---

### Soal 4: Apa risiko memasang Docker socket host (`docker.sock`) ke container Jenkins?
**Jawaban**:
Memasang socket `/var/run/docker.sock` dari host ke dalam container (dikenal sebagai pola *Docker-outside-of-Docker* atau DooD) menimbulkan risiko keamanan kritis:
1. **Eskalasi Hak Istimewa Setara Root (Host Privilege Escalation)**: Docker daemon di host berjalan dengan hak akses superuser (`root`). Memberikan akses socket kepada container berarti memberikan kontrol tak terbatas atas engine host tersebut.
2. **Container Breakout**: Pengguna atau script build berbahaya di dalam Jenkins dapat menjalankan perintah Docker untuk mem-mount direktori root sistem host ke dalam kontainer baru (`docker run -v /:/host-root alpine ...`). Hal ini memungkinkan penyerang membaca, memodifikasi, atau menghapus file sensitif host seperti `/etc/shadow`, SSH authorized keys, maupun data sistem operasi utama.
3. **Penyusupan Multi-Tenant**: Pada server Jenkins bersama (*shared Jenkins*), job dari satu tim dapat mengintip, menghentikan, atau menghancurkan container milik tim lain yang berjalan di host Docker yang sama.
*Rekomendasi Produksi*: Hindari pemasangan socket host di lingkungan multi-tenant. Gunakan arsitektur isolated build agent seperti Kaniko, Buildah (daemonless image builders), Sysbox container runtime, atau ephemeral Kubernetes agent pods.

---

### Soal 5: Mengapa URL ngrok yang berubah dapat memutus integrasi webhook?
**Jawaban**:
- Pada akun ngrok tier gratis (*Free Tier*), domain HTTPS yang dialokasikan bersifat *ephemeral* (sementara). Setiap kali proses daemon ngrok dimatikan, terputus koneksi, atau dimulai ulang, ngrok membuat URL acak baru (misalnya dari `https://subtext-tableful-smashing.ngrok-free.dev` berganti ke nama subdomain lain).
- GitHub Webhook dikonfigurasikan secara statis dengan satu alamat absolut (*Payload URL*). Jika URL ngrok lokal berganti sementara URL di pengaturan GitHub Webhook tidak diperbarui secara manual, seluruh event HTTP POST `PushEvent` dari GitHub akan tetap dikirimkan ke alamat lama.
- Alamat lama tersebut sudah tidak lagi terikat ke sesi komputer lokal pengembang, sehingga GitHub akan menerima respons error koneksi (`Connection Timed Out`, `HTTP 404`, atau `HTTP 502 Bad Gateway`) pada menu *Recent Deliveries*. Akibatnya, notifikasi perubahan kode tidak pernah mencapai Jenkins, dan proses otomatisasi build gagal terpicu.

---

### Soal 6: Mengapa data pada named volume bertahan setelah container dihapus?
**Jawaban**:
- Arsitektur Docker secara eksplisit memisahkan (*decouple*) siklus hidup komputasi aplikasi (*compute lifecycle*) dari siklus hidup penyimpanan data (*storage lifecycle*).
- Lapisan penyimpanan default container (*writable container layer*) dikelola oleh storage driver (seperti overlay2) yang bersifat *ephemeral*. Saat container dihentikan dan dihapus (`docker rm`), seluruh modifikasi data pada writable layer ikut dimusnahkan.
- Sebaliknya, **Docker Named Volume** dialokasikan di direktori khusus pada sistem file host yang dikelola langsung oleh Docker Engine (misalnya di `/var/lib/docker/volumes/production-api-data/_data`). Direktori ini berada di luar hierarki layer kontainer.
- Saat perintah `docker stop` dan `docker rm` dieksekusi, Docker hanya melepas kaitan mount point dan menghapus metadata container; berkas fisik di dalam named volume tidak pernah disentuh. Ketika container versi baru dijalankan kembali dengan argumen `-v production-api-data:/var/lib/backend_data`, Docker Engine mengaitkan kembali direktori host yang ada ke mount point container baru, sehingga data file `messages.json` tetap utuh.

---

### Soal 7: Apa perbedaan CI dan CD pada pipeline ini?
**Jawaban**:
Perbedaan antara Continuous Integration (CI) dan Continuous Deployment (CD) pada pipeline Jenkins ini terbagi berdasarkan batasan tahapan (*demarcation line*):
- **Continuous Integration (CI)**:
  - *Fokus*: Validasi kualitas kode, pencegahan regresi, dan pembentukan artefak siap rilis secara cepat dan konsisten.
  - *Tahapan pada Pipeline*:
    - **Stage 1 (Checkout Code)**: Mengintegrasikan kode terbaru dari repositori terpusat.
    - **Stage 2 (Code Syntax & Automated Tests)**: Melakukan verifikasi sintaksis (`py_compile`) dan eksekusi pengujian fungsional unit test (`test_app.py`) untuk memastikan kode bebas cacat logika sebelum dikemas.
    - **Stage 3 (Build Docker Image)**: Mengemas aplikasi dan lingkungannya menjadi artefak terisolasi yang tidak dapat diubah (*immutable artifact*) dengan penandaan versi (tagging).
  - *Luaran CI*: Docker image yang terverifikasi dan siap dijalankan.
- **Continuous Deployment (CD)**:
  - *Fokus*: Otomasi perilisan dan penyediaan artefak yang lolos CI ke lingkungan operasional target tanpa intervensi manual manusia.
  - *Tahapan pada Pipeline*:
    - **Stage 4 (Automated Deployment)**: Menangani manajemen daur hidup container operasional (`docker stop`, `docker rm`, pemeliharaan named volume `production-api-data`, dan `docker run` container baru).
    - **Stage 5 (Health Check)**: Melakukan verifikasi runtime ketersediaan layanan melalui probe HTTP `/health` untuk memastikan aplikasi benar-benar aktif melayani permintaan pengguna.

---

### Soal 8: Apa yang harus dilakukan jika tahap deploy sukses tetapi health check gagal?
**Jawaban**:
Kondisi di mana tahap deployment mengembalikan exit code 0 (`docker run` berhasil membuat proses) namun health check gagal (HTTP probe non-200 atau timeout) mengindikasikan adanya masalah kritis di level startup aplikasi atau jaringan. Langkah mitigasi dan Standard Operating Procedure (SOP) yang harus diambil:
1. **Kegagalan Otomatis Pipeline & Pembatalan Rilis**:
   - Pipeline harus langsung menandai build dengan status `FAILURE` dan memicu blok `post { failure { ... } }`.
2. **Prosedur Rollback Otomatis (Automated Rollback)**:
   - Pipeline harus secara terprogram menghentikan container baru yang bermasalah (`docker stop production-api-container`).
   - Menjalankan kembali container produksi menggunakan image build sebelumnya yang terbukti stabil (misalnya menggunakan tag commit SHA build sebelumnya atau tag rilis stabil: `python-crud-api:PREVIOUS_STABLE_BUILD`).
3. **Triase & Analisis Diagnostik (Triage)**:
   - Memeriksa log internal aplikasi: `docker logs --tail 100 production-api-container` untuk mendeteksi unhandled exception, syntax error modul runtime, kegagalan inisialisasi file storage `/var/lib/backend_data`, atau deadlock port binding.
   - Memeriksa status exit container: `docker ps -a` untuk melihat apakah container mengalami crash loop (`Exited (1)`).
   - Memeriksa status jaringan Docker: Memastikan container terhubung ke network bridge `jenkins-net` dan port `5000` tidak mengalami tabrakan alokasi (*port collision*).
4. **Notifikasi dan Eskalasi Tim**:
   - Mengirim alert insiden deployment secara otomatis melalui webhook notifikasi (Slack, Telegram, atau Email) ke tim rekayasa perangkat lunak disertai cuplikan log error.

---

## 8. Checklist Kelayakan Sebelum Pengumpulan (Submission Checklist)

Berdasarkan lembar panduan Bab 13 (Halaman 16 `CICD_Jenkins.pdf`), seluruh kriteria evaluasi telah dipenuhi secara sempurna:

- [x] **Repository GitHub dapat diakses oleh akun yang digunakan Jenkins**: Terverifikasi melalui checkout SCM over HTTPS pada repositori `ervanfahriaw/tugas-ci-cd`.
- [x] **PAT bersifat minimum-privilege dan tersimpan di Jenkins Credentials**: Fine-grained PAT terdaftar dengan scope read-only pada ID credential `github-pat-readonly` di Jenkins Credential Store terenkripsi.
- [x] **Tidak ada token atau password di source code, commit, atau screenshot**: Seluruh token, authtoken ngrok, dan kata sandi disamarkan atau dikelola melalui environment variable / secret store.
- [x] **Jenkinsfile berada di root repository dan job memakai Pipeline script from SCM**: Berkas `Jenkinsfile` berada di root tree branch `main` dan dipanggil langsung oleh job `python-crud-api-pipeline`.
- [x] **Build berhasil dari awal hingga health check**: Pipeline Build #5 dan Build #6 menyelesaikan kelima stages dengan status `Finished: SUCCESS`.
- [x] **ngrok aktif dan GitHub webhook mengarah ke `/github-webhook/`**: Tunnel aktif di `https://subtext-tableful-smashing.ngrok-free.dev` dan GitHub Webhook terdaftar dengan akhiran path `/github-webhook/`.
- [x] **Push baru memicu build otomatis**: Terbukti secara empiris melalui PushEvent commit `553f615` (Build #5) dan commit `61b028b` (Build #6) tanpa menyentuh tombol build.
- [x] **API CRUD berjalan dan data tetap ada setelah redeploy**: Operasi CRUD teruji via curl, dan 2 data pesan terbukti tetap utuh di named volume `production-api-data` setelah container dihancurkan dan dibuat ulang.
- [x] **Semua bukti praktikum disertakan**: Log konsol, matriks uji endpoint, bukti webhook delivery, catatan troubleshooting, dan 8 jawaban analisis telah disusun secara lengkap dan mendalam.

---
**Laboratorium CI/CD Diselesaikan dengan Hasil Sempurna.**  
*Tanggal Penyusunan: 31 Oktober 2026*
