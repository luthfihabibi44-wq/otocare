import sqlite3
from datetime import datetime
import os
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS kendaraan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                plat TEXT NOT NULL,
                jenis TEXT NOT NULL DEFAULT 'Matic',
                km_sekarang INTEGER NOT NULL,
                tgl_oli TEXT NOT NULL,
                km_oli INTEGER NOT NULL,
                tgl_mesin TEXT NOT NULL,
                km_mesin INTEGER NOT NULL,
                tgl_cvt TEXT NOT NULL,
                km_cvt INTEGER NOT NULL,
                tgl_kaki TEXT NOT NULL,
                km_kaki INTEGER NOT NULL,
                tgl_listrik TEXT NOT NULL,
                km_listrik INTEGER NOT NULL
            )
        ''')
        conn.commit()

# 1. Halaman Beranda Utama - KHUSUS FORM REGISTRASI FULL PAGE
@app.route('/')
def index():
    return render_template('index.html')

# 2. Halaman Baru - KHUSUS DAFTAR ARMADA TERPANTAU
@app.route('/armada')
def armada():
    conn = get_db()
    try:
        kendaraan_list = conn.execute('SELECT * FROM kendaraan').fetchall()
    except sqlite3.OperationalError:
        conn.close()
        if os.path.exists(DATABASE):
            os.remove(DATABASE)
        init_db()
        conn = get_db()
        kendaraan_list = conn.execute('SELECT * FROM kendaraan').fetchall()
    conn.close()
    return render_template('armada.html', kendaraan=kendaraan_list)

@app.route('/tambah', methods=['POST'])
def tambah():
    # 1. Ambil data utama dari form dasar
    nama = request.form.get('nama')
    plat = request.form.get('plat')
    jenis = request.form.get('jenis')
    km_sekarang = int(request.form.get('km_sekarang', 0))
    
    # Ambil tanggal hari ini sebagai cadangan otomatis jika user lupa membuka modal sektor
    hari_ini_str = datetime.now().strftime('%Y-%m-%d')
    
    # 2. Ambil data sektor (Gunakan nilai default hari ini dan KM saat ini jika kosong)
    tgl_oli = request.form.get('tgl_oli') or hari_ini_str
    km_oli = request.form.get('km_oli') or km_sekarang
    
    tgl_mesin = request.form.get('tgl_mesin') or hari_ini_str
    km_mesin = request.form.get('km_mesin') or km_sekarang
    
    tgl_cvt = request.form.get('tgl_cvt') or hari_ini_str
    km_cvt = request.form.get('km_cvt') or km_sekarang
    
    tgl_kaki = request.form.get('tgl_kaki') or hari_ini_str
    km_kaki = request.form.get('km_kaki') or km_sekarang
    
    tgl_listrik = request.form.get('tgl_listrik') or hari_ini_str
    km_listrik = request.form.get('km_listrik') or km_sekarang

    # 3. Masukkan data terstruktur ke dalam database SQLite
    conn = get_db()
    conn.execute('''
        INSERT INTO kendaraan (
            nama, plat, jenis, km_sekarang, 
            tgl_oli, km_oli, tgl_mesin, km_mesin, 
            tgl_cvt, km_cvt, tgl_kaki, km_kaki, tgl_listrik, km_listrik
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nama, plat, jenis, km_sekarang, 
          tgl_oli, int(km_oli), tgl_mesin, int(km_mesin), 
          tgl_cvt, int(km_cvt), tgl_kaki, int(km_kaki), tgl_listrik, int(km_listrik)))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('armada'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    motor = conn.execute('SELECT * FROM kendaraan WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        nama = request.form['nama']
        plat = request.form['plat']
        jenis = request.form['jenis']
        km_sekarang = int(request.form['km_sekarang'])
        
        tgl_oli = request.form['tgl_oli']
        km_oli = int(request.form['km_oli'])
        
        tgl_mesin = request.form['tgl_mesin']
        km_mesin = int(request.form['km_mesin'])
        
        tgl_cvt = request.form['tgl_cvt']
        km_cvt = int(request.form['km_cvt'])
        
        tgl_kaki = request.form['tgl_kaki']
        km_kaki = int(request.form['km_kaki'])
        
        tgl_listrik = request.form['tgl_listrik']
        km_listrik = int(request.form['km_listrik'])

        conn.execute('''
            UPDATE kendaraan SET 
                nama=?, plat=?, jenis=?, km_sekarang=?, 
                tgl_oli=?, km_oli=?, tgl_mesin=?, km_mesin=?, 
                tgl_cvt=?, km_cvt=?, tgl_kaki=?, km_kaki=?, 
                tgl_listrik=?, km_listrik=?
            WHERE id=?
        ''', (nama, plat, jenis, km_sekarang, tgl_oli, km_oli, tgl_mesin, km_mesin, tgl_cvt, km_cvt, tgl_kaki, km_kaki, tgl_listrik, km_listrik, id))
        conn.commit()
        conn.close()
        return redirect(url_for('armada'))
        
    conn.close()
    return render_template('edit.html', motor=motor)

@app.route('/hapus/<int:id>')
def hapus(id):
    with get_db() as conn:
        conn.execute('DELETE FROM kendaraan WHERE id = ?', (id,))
        conn.commit()
    return redirect(url_for('armada'))

@app.route('/analisis/<int:id>', methods=['GET'])
def analisis(id):
    conn = get_db()
    motor = conn.execute('SELECT * FROM kendaraan WHERE id = ?', (id,)).fetchone()
    conn.close()

    hari_ini = datetime.now()
    km_skrg = motor['km_sekarang']

    s_hari_oli = (hari_ini - datetime.strptime(motor['tgl_oli'], '%Y-%m-%d')).days
    s_km_oli = max(0, km_skrg - motor['km_oli'])

    s_hari_mesin = (hari_ini - datetime.strptime(motor['tgl_mesin'], '%Y-%m-%d')).days
    s_km_mesin = max(0, km_skrg - motor['km_mesin'])

    s_hari_cvt = (hari_ini - datetime.strptime(motor['tgl_cvt'], '%Y-%m-%d')).days
    s_km_cvt = max(0, km_skrg - motor['km_cvt'])

    s_hari_kaki = (hari_ini - datetime.strptime(motor['tgl_kaki'], '%Y-%m-%d')).days
    s_km_kaki = max(0, km_skrg - motor['km_kaki'])

    s_hari_listrik = (hari_ini - datetime.strptime(motor['tgl_listrik'], '%Y-%m-%d')).days
    s_km_listrik = max(0, km_skrg - motor['km_listrik'])

    if motor['jenis'] == 'Matic':
        nama_transmisi = "Sektor Transmisi (CVT & Gardan)"
        lim_h_trans = 120
        lim_k_trans = 10000
    else:
        nama_transmisi = "Sektor Transmisi (Rantai & Kopling)"
        lim_h_trans = 150
        lim_k_trans = 12000

    p_oli = min(100, int((s_km_oli / 2000) * 100))
    p_mesin = min(100, int((s_km_mesin / 6000) * 100))
    p_cvt = min(100, int((s_km_cvt / lim_k_trans) * 100))
    p_kaki = min(100, int((s_km_kaki / 8000) * 100))
    p_listrik = min(100, int((s_km_listrik / 15000) * 100))

    perlu_oli = s_hari_oli > 60 or s_km_oli > 2000
    perlu_mesin = s_hari_mesin > 120 or s_km_mesin > 6000
    perlu_transmisi = s_hari_cvt > lim_h_trans or s_km_cvt > lim_k_trans
    perlu_kaki = s_hari_kaki > 90 or s_km_kaki > 8000
    perlu_listrik = s_hari_listrik > 180 or s_km_listrik > 15000

    sektor_bermasalah = []
    if perlu_oli:
        sektor_bermasalah.append("📌 <b>Sektor Pelumasan (Oli Mesin)</b>: Sudah melewati ambang batas efisiensi penggantian berkala (Ambang batas: 2.000 KM / 60 Hari).")
    if perlu_mesin:
        sektor_bermasalah.append("📌 <b>Sektor Mesin & Pengapian (Tune-Up)</b>: Penumpukan karbon ruang bakar diindikasikan tinggi, butuh pembersihan komponen throttle body.")
    if perlu_transmisi:
        sektor_bermasalah.append(f"📌 <b>{nama_transmisi}</b>: Batas keausan operasional komponen penggerak terlampaui. Risiko terjadi selip friksi atau anomali mekanis.")
    if perlu_kaki:
        sektor_bermasalah.append("📌 <b>Sistem Pengendalian & Rem</b>: Terdeteksi penurunan viskositas minyak rem atau keausan material gesek (kampas), inspeksi keamanan wajib dilakukan.")
    if perlu_listrik:
        sektor_bermasalah.append("📌 <b>Sistem Elektrikal & Aki</b>: Umur pakai cadangan daya sistem kelistrikan memasuki fase rawan penurunan tegangan konstan.")

    if not sektor_bermasalah:
        status_fisik = "Normal"
        warna_fisik = "success"
        kesimpulan_matriks = "Seluruh parameter matriks telemetri operasional unit terpantau dalam kondisi optimal. Tidak ditemukan anomali mekanis maupun komponen yang melewati siklus ambang batas servis untuk saat ini."
    else:
        if (s_hari_oli > 90 or s_km_oli > 3500) or (perlu_transmisi and s_km_cvt > (lim_k_trans + 3000)):
            status_fisik = "Kritis"
            warna_fisik = "danger"
        else:
            status_fisik = "Atensi"
            warna_fisik = "warning"
        
        kesimpulan_matriks = "Analisis komparasi algoritma mendeteksi penyimpangan efisiensi komponen akibat batas pakai. <b>Berikut daftar sektor operasional utama yang direkomendasikan untuk segera dilakukan tindakan perawatan mekanis:</b><br><br>" + "<br>".join(sektor_bermasalah)

    return render_template('dashboard.html', motor=motor, 
                           s_h_oli=s_hari_oli, s_k_oli=s_km_oli, p_oli=p_oli,
                           s_h_mesin=s_hari_mesin, s_k_mesin=s_km_mesin, p_mesin=p_mesin,
                           s_h_cvt=s_hari_cvt, s_k_cvt=s_km_cvt, p_cvt=p_cvt,
                           s_h_kaki=s_hari_kaki, s_k_kaki=s_km_kaki, p_kaki=p_kaki,
                           s_h_lis=s_hari_listrik, s_k_lis=s_km_listrik, p_listrik=p_listrik,
                           nama_transmisi=nama_transmisi, kesimpulan_matriks=kesimpulan_matriks,
                           status_fisik=status_fisik, warna_fisik=warna_fisik)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)