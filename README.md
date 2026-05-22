# GitPulse - GitHub Activity Visualizer & Persona Analyzer

GitPulse adalah aplikasi CLI/TUI berbasis Python premium yang dirancang untuk menganalisis aktivitas pengkodean terbaru dari pengguna GitHub mana pun. Aplikasi ini memeriksa bahasa pemrograman teratas, pola waktu commit, kontribusi mingguan, serta secara otomatis mengklasifikasikan pengembang ke dalam tipe karakter unik (Developer Persona). 

Aplikasi ini juga mengekspor laporan komparatif atau individu serta menyediakan kartu profil ASCII siap-pakai untuk README Profil GitHub Anda.

---

## Fitur Utama

- **Ringkasan Profil:** Menampilkan nama, bio, lokasi, jumlah pengikut (followers), dan repositori publik dengan tata letak minimalis dan bersih.
- **Analitik Pengkodean:**
  - **Grafik Bahasa Teratas:** Menghitung dan memvisualisasikan persentase kontribusi bahasa pemrograman Anda.
  - **Pola Waktu Kontribusi:** Menganalisis jam pengerjaan kode Anda (Pagi, Siang, Sore, Malam).
  - **Ritme Mingguan:** Menampilkan visualisasi ritme kontribusi harian dari Senin sampai Minggu.
- **Analisis Karakter Developer (Developer Persona):** Mengelompokkan karakter coding Anda secara otomatis berdasarkan data aktivitas:
  - *Night Owl* - Pengembang yang aktif dan fokus di malam hari.
  - *Early Bird* - Pengembang fajar yang produktif di pagi hari.
  - *Commit Machine* - Pengembang dengan frekuensi push tinggi secara berkala.
  - *Team Collaborator* - Pengembang yang fokus pada integrasi tim (Pull Request & Review).
  - *Problem Solver* - Detektif bug yang aktif melacak masalah lewat Issues.
  - *Focused Craftsman* - Pengembang tenang yang menulis kode terencana dan minim bug.
- **Tabel Repositori Terpopuler:** Menyajikan tabel repositori teratas lengkap dengan indikator status keaktifan (Sangat Aktif, Aktif, Arsip, atau Stabil).
- **Mode Perbandingan (Compare Mode):** Memungkinkan Anda membandingkan statistik dua akun GitHub secara berdampingan (side-by-side) lengkap dengan keputusan pemenang metrik.
- **Eksportir Kartu Profil ASCII:** Menghasilkan 3 gaya kartu ASCII yang sangat menarik untuk disalin langsung ke README profil GitHub Anda.
- **Mode Offline (Mock Mode):** Menggunakan data mock demo jika koneksi internet terputus atau batas limit API GitHub terlampaui.

---

## Persyaratan Sistem & Instalasi

1. **Masuk ke direktori proyek:**
   ```bash
   cd D:\folder_coding\gitpulse
   ```

2. **Instal pustaka yang dibutuhkan:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Cara Menjalankan Aplikasi

### 1. Menjalankan Menu Interaktif (Sangat Direkomendasikan):
Jalankan perintah berikut untuk membuka menu pilihan interaktif:
```bash
python main.py
```

### 2. Menganalisis Akun GitHub Tertentu secara Langsung:
Ganti `username_github` dengan nama pengguna yang ingin dianalisis:
```bash
python main.py --username username_github
```

### 3. Menggunakan Token Akses GitHub (Untuk Menghindari Limit API):
GitHub membatasi permintaan tidak autentik sebanyak 60 per jam. Untuk analisis intensif, sertakan Personal Access Token Anda:
```bash
python main.py --username username_github --token TOKEN_AKSES_ANDA
```

### 4. Membandingkan Dua Pengguna secara Langsung:
```bash
python main.py --compare username1 username2
```

### 5. Menjalankan Uji Coba Demo Instan (Mock Mode):
```bash
python main.py --mock
```

---

## Struktur Proyek

- `main.py` - Logika inti penarikan API GitHub, kalkulasi statistik mingguan/harian, render TUI, dan penulisan laporan.
- `requirements.txt` - Dependensi aplikasi (`requests` dan `rich`).
- `README.md` - Panduan instalasi dan dokumentasi penggunaan bahasa Indonesia.

---
*Dikembangkan sebagai bagian dari tantangan 1 Day 1 Project!*
