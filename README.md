# Proyek Akhir: Menyelesaikan Permasalahan Perusahaan Edutech

## Business Understanding

Jaya Jaya Institut adalah institusi pendidikan tinggi yang sudah berdiri sejak tahun 2000 dan selama ini punya reputasi baik dari lulusannya. Masalahnya, jumlah siswa yang tidak menyelesaikan pendidikan alias dropout masih tinggi dan belum tertangani.

Dropout ini merugikan dua pihak sekaligus. Buat siswa, waktu dan biaya yang sudah dikeluarkan hilang tanpa gelar. Buat institusi, dropout menurunkan tingkat kelulusan, mengurangi pendapatan, sekaligus merusak reputasi yang sudah dibangun bertahun tahun. Karena itu institusi ingin bisa mendeteksi siswa berisiko sedini mungkin supaya bimbingan khusus bisa diberikan sebelum siswa benar benar keluar.

### Permasalahan Bisnis

1. Jumlah siswa yang tidak menyelesaikan pendidikan masih tinggi dan menjadi masalah besar bagi institusi.
2. Institusi belum tahu faktor apa saja yang paling berkaitan dengan dropout.
3. Institusi belum punya alat untuk memahami data dan memantau performa siswa secara berkala.
4. Institusi belum mampu mengidentifikasi siswa berisiko sebelum mereka keluar, sehingga bimbingan baru diberikan setelah terlambat.

### Cakupan Proyek

1. Eksplorasi data siswa untuk menemukan faktor yang berkaitan dengan dropout.
2. Membangun business dashboard untuk memantau performa siswa.
3. Membangun model klasifikasi yang memprediksi apakah seorang siswa berpotensi Dropout atau Graduate.
4. Membangun prototype prediksi berbasis Streamlit yang dapat diakses secara online.
5. Menyusun rekomendasi action items untuk institusi.

### Persiapan

Sumber data.

```
https://github.com/dicodingacademy/dicoding_dataset/tree/main/students_performance
```

Dataset berisi 4424 baris dan 37 kolom. Kolom `Status` adalah target dengan tiga nilai, yaitu Graduate, Dropout, dan Enrolled. Berkas memakai titik koma sebagai pemisah kolom, dan seluruh kolom kategorik sudah dikodekan menjadi angka oleh penyedia data.

Setup environment.

```
conda create -n bpds python=3.12
conda activate bpds
pip install -r requirements.txt
```

Menjalankan database dan Metabase.

```
docker run -d --name postgres-institut -e POSTGRES_USER=root -e POSTGRES_PASSWORD=root123 -e POSTGRES_DB=institut_db -p 5433:5432 postgres:16
docker run -d --name metabase-institut -p 3000:3000 metabase/metabase
```

Notebook mengirim data ke PostgreSQL lewat SQLAlchemy, lalu Metabase membaca tabel `students` dari database itu. Di dalam Metabase, koneksi database diisi dengan host `host.docker.internal` dan port `5433`.

## Business Dashboard

Dashboard dibuat di Metabase dengan nama `Dashboard Monitoring Dropout Siswa` dan berisi sepuluh kartu.

Tiga kartu ringkasan di baris paling atas menampilkan dropout rate keseluruhan, total siswa, dan jumlah siswa aktif yang ditandai berisiko oleh model. Kartu ketiga sengaja dibatasi hanya pada siswa berstatus Enrolled, karena siswa yang sudah lulus atau sudah keluar tidak lagi bisa ditindaklanjuti.

Lima kartu berikutnya memecah dropout rate berdasarkan status pelunasan biaya kuliah, status debitur dan beasiswa, program studi, kelompok usia, serta komposisi status siswa secara keseluruhan. Satu kartu lain membandingkan rata rata mata kuliah lulus dan nilai semester satu antara siswa Graduate, Enrolled, dan Dropout.

Kartu terakhir berupa tabel berisi dua puluh siswa aktif dengan probabilitas dropout tertinggi, lengkap dengan program studi, usia, hasil akademik semester satu, dan status pembayaran, supaya bagian bimbingan konseling bisa langsung menindaklanjuti.

Akses dashboard.

```
URL       http://localhost:3000
Email     root@mail.com
Password  root123
```

Berkas `metabase.db.mv.db` ada di folder submission. Untuk membukanya, jalankan container Metabase dengan me-mount berkas itu ke `/metabase.db/metabase.db.mv.db`.

## Menjalankan Sistem Machine Learning

Prototype dibuat dengan Streamlit dan sudah di-deploy ke Streamlit Community Cloud sehingga bisa diakses tanpa instalasi apa pun.

```
https://jaya-jaya-institut-dropout-ken.streamlit.app/
```

Menjalankan secara lokal.

```
streamlit run app.py
```

Aplikasi terbuka di `http://localhost:8501`. Pengguna mengisi profil siswa, kondisi finansial, dan hasil akademik semester satu, lalu menekan tombol Prediksi. Keluarannya berupa probabilitas dropout beserta status apakah siswa masuk kategori berisiko atau tidak.

Form hanya menampilkan empat belas isian yang paling berpengaruh sekaligus paling masuk akal diisi manusia. Enam belas kolom administratif sisanya diisi otomatis memakai nilai median dataset supaya petugas tidak perlu mengisi tiga puluh isian setiap kali memeriksa satu siswa.

Pemodelan hanya memakai siswa berstatus Dropout dan Graduate, totalnya 3630 baris dengan 1421 Dropout dan 2209 Graduate. Targetnya biner, 1 untuk Dropout dan 0 untuk Graduate. Siswa berstatus Enrolled sebanyak 794 orang tidak ikut dilatih karena statusnya belum final, mereka belum lulus tapi juga belum keluar, sehingga kalau dipaksa masuk salah satu kelas targetnya jadi ambigu. Kelompok ini justru dipakai sebagai data prediksi, karena merekalah siswa aktif yang masih bisa diselamatkan.

Model yang dipakai Random Forest Classifier dengan `class_weight="balanced"` karena proporsi dropout ada di 39 persen. Data dibagi 80 persen latih dan 20 persen uji secara stratified.

Enam kolom hasil akademik semester dua sengaja dibuang dari fitur. Kalau dipakai AUC memang lebih tinggi, tapi model jadi baru bisa dipakai setelah siswa menjalani satu tahun penuh, padahal institusi minta deteksi secepat mungkin. Model ini dibatasi hanya memakai data sampai akhir semester satu.

Pada threshold bawaan 0.5, model sudah cukup baik dengan recall 0.85 dan precision 0.88. Tapi dari 284 siswa yang benar benar dropout di data uji, masih ada 42 orang yang lolos dari deteksi. Buat institusi, kehilangan satu siswa jauh lebih mahal daripada memanggil siswa yang ternyata baik baik saja, jadi threshold diturunkan sedikit ke 0.4.

Performa pada threshold 0.4.

| Metrik | Graduate | Dropout |
|---|---|---|
| Precision | 0.92 | 0.82 |
| Recall | 0.88 | 0.89 |
| F1-score | 0.90 | 0.85 |

Akurasi keseluruhan 0.88 dan ROC AUC 0.9470. Model menangkap 252 dari 284 siswa yang benar benar dropout pada data uji, dengan 55 siswa yang sebenarnya lulus ikut tertandai. Dari 794 siswa aktif berstatus Enrolled, model menandai 417 orang sebagai berisiko dropout.

## Conclusion

Angka dropout Jaya Jaya Institut ada di 32.12 persen, yaitu 1421 dari 4424 siswa. Angka ini tinggi untuk sebuah institusi pendidikan dan sejalan dengan keluhan yang disampaikan pihak institusi.

Yang paling mencolok dari hasil analisis adalah faktor finansial. Siswa yang tunggakan biaya kuliahnya belum lunas mengalami dropout di angka 86.55 persen, jauh di atas 24.74 persen dari siswa yang sudah lunas. Siswa berstatus debitur juga tinggi di 62.03 persen, sementara penerima beasiswa justru paling aman di 12.19 persen. Selisih sebesar ini tidak muncul di faktor mana pun yang lain.

Performa akademik semester satu punya korelasi paling kuat dengan dropout. Siswa yang bertahan rata rata lulus 5.73 mata kuliah di semester pertama dengan nilai rata rata 12.24, sedangkan yang dropout hanya lulus 2.55 mata kuliah dengan nilai 7.26. Pola yang sama juga muncul di feature importance model, di mana jumlah mata kuliah lulus dan nilai rata rata semester satu menempati dua posisi teratas dengan porsi gabungan hampir 38 persen.

Usia saat mendaftar ikut berpengaruh dan polanya bertingkat. Siswa yang mendaftar di bawah 20 tahun dropout di angka 20.95 persen, naik ke 28.56 persen untuk kelompok 20 sampai 24 tahun, lalu melonjak ke 57.61 persen untuk kelompok 25 sampai 29 tahun dan 54.15 persen untuk 30 tahun ke atas.

Program studi juga menentukan. Equinculture berada di 55.32 persen, Informatics Engineering di 54.12 persen, dan Management kelas malam di 50.75 persen, sementara Nursing yang jumlah siswanya paling banyak justru paling aman di 15.40 persen.

Sebaliknya, nilai masuk hampir tidak membedakan apa apa, 127.93 untuk yang bertahan dan 124.96 untuk yang dropout. Artinya dropout lebih ditentukan oleh apa yang terjadi setelah siswa masuk, bukan seberapa bagus mereka waktu diterima. Indikator ekonomi makro seperti tingkat pengangguran, inflasi, dan GDP korelasinya di bawah 0.05 dan tidak layak dijadikan dasar rekomendasi.

Semua temuan ini sifatnya asosiatif, bukan sebab akibat. Beberapa faktor juga saling tumpang tindih, misalnya usia saat mendaftar, kelas malam, dan status pembayaran cenderung bergerak bersamaan. Perlu dicatat juga bahwa dari 794 siswa aktif, model menandai 417 orang atau lebih dari separuhnya sebagai berisiko. Angka setinggi itu wajar mengingat siswa Enrolled memang belum menuntaskan studinya sehingga catatan akademiknya cenderung terlihat lebih lemah, jadi daftar ini sebaiknya diurutkan berdasarkan probabilitas dan ditangani bertahap sesuai kapasitas bimbingan, bukan dikejar semua sekaligus.

### Rekomendasi Action Items

1. Bangun mekanisme peringatan dini berbasis tunggakan biaya kuliah. Status pelunasan punya selisih terbesar dari semua faktor, sekaligus paling cepat terdeteksi karena datanya sudah ada di sistem keuangan sejak awal semester. Siswa yang menunggak sebaiknya otomatis masuk antrean konsultasi, bukan sekadar ditagih.

2. Perluas dan targetkan ulang skema beasiswa serta cicilan. Penerima beasiswa dropout di 12.19 persen sementara yang bukan penerima di 38.71 persen. Kalau anggaran terbatas, prioritaskan siswa yang sudah menunjukkan tanda kesulitan pembayaran di semester pertama.

3. Jadikan hasil semester satu sebagai titik intervensi resmi, bukan sekadar catatan nilai. Siswa yang lulus kurang dari tiga mata kuliah di semester pertama perlu langsung dijadwalkan bimbingan akademik, karena rata rata siswa dropout berada persis di rentang itu.

4. Siapkan program pendampingan khusus untuk mahasiswa berusia 25 tahun ke atas dan kelas malam. Dua kelompok ini dropout di atas 50 persen dan kemungkinan besar menghadapi beban kerja atau keluarga di luar kampus, sehingga butuh fleksibilitas jadwal, bukan sekadar motivasi.

5. Audit kurikulum dan beban studi pada program dengan dropout tertinggi, yaitu Equinculture, Informatics Engineering, dan Management kelas malam. Ketiganya lebih dari tiga kali lipat dibanding Nursing yang justru punya siswa paling banyak, jadi masalahnya kemungkinan ada di program, bukan di siswanya.

6. Pakai daftar siswa aktif berisiko di dashboard sebagai antrean tindak lanjut tiap semester. Dengan precision 0.82, kira kira satu dari lima siswa yang ditandai sebenarnya akan lulus normal, jadi daftar ini adalah prioritas percakapan bimbingan, bukan vonis bahwa mereka pasti keluar.
