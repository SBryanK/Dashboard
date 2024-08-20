import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import mysql.connector
from pymongo import MongoClient
from datetime import datetime
import plotly.express as px

# Set Page Config with header and title
st.set_page_config(page_title="Dashboard Penjualan", page_icon="📊", layout="wide")

# Connect to SQLite as SQL editor choice
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        st.error(f"Gagal membuat koneksi ke SQLite: {e}")
        return None

# Create User Table for authentication
def create_user_table(conn):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        nomor_hp INTEGER NOT NULL UNIQUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        st.error(f"Gagal membuat tabel pengguna: {e}")

# Adding new USER
def add_user(conn, username, password, email):
    hashed_password = generate_password_hash(password)
    sql = ''' INSERT INTO users(username, password, email)
              VALUES(?, ?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, (username, hashed_password, email))
    conn.commit()
    return cur.lastrowid

# Checking USER Credentials
def verify_user(conn, username, password):
    sql = "SELECT password FROM users WHERE username = ?"
    cur = conn.cursor()
    cur.execute(sql, (username,))
    result = cur.fetchone()
    if result and check_password_hash(result[0], password):
        return True
    return False

# Database setup
DATABASE = "users.db"
conn = create_connection(DATABASE)
create_user_table(conn)

# Connect to POSTGRESQL
def connect_postgresql(host, dbname, user, password):
    try:
        conn = psycopg2.connect(
            host=host,
            database=dbname,
            user=user,
            password=password
        )
        return conn
    except Exception as e:
        st.error(f"Gagal terhubung ke PostgreSQL: {e}")
        return None

# Connect to MySQL
def connect_mysql(host, dbname, user, password):
    try:
        conn = mysql.connector.connect(
            host=host,
            database=dbname,
            user=user,
            password=password
        )
        return conn
    except Exception as e:
        st.error(f"Gagal terhubung ke MySQL: {e}")
        return None

# Connect to MongoDB
def connect_mongodb(uri, dbname):
    try:
        client = MongoClient(uri)
        db = client[dbname]
        return db
    except Exception as e:
        st.error(f"Gagal terhubung ke MongoDB: {e}")
        return None
    
# User login function
def login():
    st.markdown("<h1 style='text-align: center; color: #0fb824; font-size: 108px;'>LOGIN <br>PIKKAT</h1>", unsafe_allow_html=True)
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    username = st.text_input("Username", key="login_username_{}".format(st.session_state["show_login"]))
    password = st.text_input("Password", type="password", key="login_password_{}".format(st.session_state["show_login"]))
    if st.button("LOGIN", key="login_button"):
        if verify_user(conn, username, password):
            st.session_state["logged_in"] = True
            st.session_state["current_page"] = "data_input"
        else:
            st.error("Username / Password salah")
    st.markdown("</div>", unsafe_allow_html=True)

# Checking the validity of the username
def is_valid_username(username):
    if len(username) < 6:
        return False
    has_alpha = any(c.isalpha() for c in username)
    has_digit = any(c.isdigit() for c in username)
    return has_alpha and has_digit

# Checking the validity of the password
def is_valid_password(password):
    if len(password) < 6:
        return False
    has_special = any(c in '!@#$%^&*()-_=+[]{}|;:",.<>?/~`' for c in password)
    has_alpha_or_digit = any(c.isalnum() for c in password)
    return has_special and has_alpha_or_digit

# Checking the validity of the email
def is_valid_number(hp):
    return hp.startswith("08")

# User registration function
def register():
    st.markdown("<h1 style='text-align: center; font-size: 70px; font-family: Inter; color: #0fb824'>DAFTAR</h1>", unsafe_allow_html=True)
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    new_username = st.text_input("USERNAME", key="register_username_{}".format(st.session_state["show_login"]))
    new_password = st.text_input("PASSWORD", type="password", key="register_password_{}".format(st.session_state["show_login"]))
    hp = st.text_input("Nomor HP", key="register_hp_{}".format(st.session_state["show_login"]))
    
    if st.button("DAFTAR", key="register_button"):
        if not is_valid_username(new_username):
            st.error("Username Minimal 6 Karakter dan Kombinasi Huruf dan Angka.")
        elif not is_valid_password(new_password):
            st.error("Password Minimal 6 Karakter Dengan Minimal 1 Karakter Khusus.")
        elif not is_valid_number(hp):
            st.error("Nomor HP Tidak Berlaku, harus diawali dengan 08")
        else:
            try:
                add_user(conn, new_username, new_password, hp)
                st.success("Pendaftaran berhasil! Silakan login.")
                st.session_state["show_login"] = True
            except sqlite3.IntegrityError:
                st.error("Pendaftaran gagal. Username atau Nomor HP Sudah Digunakan.")
    st.markdown("</div>", unsafe_allow_html=True)

# Login and Register Function
def show_login_or_register():
    if st.session_state["show_login"]:
        login()
        st.markdown("<p style='text-align: center;'>Belum Punya Akun? Yuk Daftar</p>", unsafe_allow_html=True)
        if st.button("DAFTAR", key="switch_to_register"):
            st.session_state["show_login"] = False
    else:
        register()
        st.markdown("<p style='text-align: center;'>Sudah Punya Akun?</p>", unsafe_allow_html=True)
        if st.button("LOGIN", key="switch_to_login"):
            st.session_state["show_login"] = True

# Main Page
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "show_login" not in st.session_state:
    st.session_state["show_login"] = True

if "df" not in st.session_state:
    st.session_state["df"] = None

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "data_input"

if st.session_state["logged_in"]:
    if st.session_state["current_page"] == "data_input":
        st.markdown(
            """
            <style>
            body {
                font-family: 'Inter';
                background-color: #f9f9f9;
            }
            .main {
                font-family: 'Inter';
                background-color: #e7fce6;
            }

            h1, h2, h3 {
                text-align: center;
            }
            h1 {
                color: #0fb824;
                font-size: 96px;

            }
            h2 {
                color: #cf3c3e;
                font-size: 64px;
                font-family: Inter;
            }

            .block-container {
                padding-top: 1rem;
            }
            .box {
                background-color: #76db43; /* Green fill */
                padding: 20px;
                border-radius: 15px;
                margin: 10px 0;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
            }
            .stSidebar {
                background-color: #76db43;
                font-size: 30px;
            }

            .stTextInput > div > div > input {
                margin-left: auto;
                margin-right: auto;
                width: 50%;  /* Set the width to half the container */
                background-color: #e0f2e9; /* Light green background */
                color: #0fb824; /* Light green text */
            }
            .stButton > button {
                display: block;
                margin-left: auto;
                margin-right: auto;
                color: #0fb824  
            }
            </style>
            """, unsafe_allow_html=True)

        df = st.session_state["df"]

        st.markdown("<h1 style='text-align: center; color: #0fb824; font-family: Inter;'>INPUT<br>DATA</h1>", unsafe_allow_html=True)

        data_source = st.radio("Pilih Sumber Data", ["Upload CSV", "Koneksi Database"], key="data_source", horizontal=True)

        if data_source == "Upload CSV":
            uploaded_file = st.file_uploader("Upload file CSV", type=["csv"], key="uploaded_file")
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file)
                st.session_state["df"] = df
                        # Tampilkan tombol kembali di halaman input data
            if st.button("Kembali"):
                st.session_state["logged_in"] = False
                st.session_state["current_page"] = "login"

            # Menampilkan dashboard hanya jika data tersedia
            if df is not None:
                st.sidebar.title("Filters")
                
                # Pastikan tanggal diformat dengan benar
                df['tgl_transaksi'] = pd.to_datetime(df['tgl_transaksi'], format='%d/%m/%Y %H:%M', dayfirst=True)

                # Tambahkan filter tanggal
                start_date = st.sidebar.date_input("Tanggal Mulai", value=df['tgl_transaksi'].min(), key="start_date")
                end_date = st.sidebar.date_input("Tanggal Selesai", value=df['tgl_transaksi'].max(), key="end_date")
                
                # Filter berdasarkan tanggal
                df_filtered_by_date = df[(df['tgl_transaksi'] >= pd.to_datetime(start_date)) & (df['tgl_transaksi'] <= pd.to_datetime(end_date))]

                # Tambahkan kolom 'periode' berdasarkan panjang rentang tanggal
                date_range_days = (end_date - start_date).days

                if date_range_days <= 7:  # Jika rentang tanggal <= 7 hari, tampilkan data harian
                    df_filtered_by_date['periode'] = df_filtered_by_date['tgl_transaksi'].dt.to_period('D').apply(lambda r: r.start_time)
                    period_label = 'Harian'
                elif 7 < date_range_days <= 30:  # Jika rentang tanggal antara 7 dan 30 hari, tampilkan data mingguan
                    df_filtered_by_date['periode'] = df_filtered_by_date['tgl_transaksi'].dt.to_period('W').apply(lambda r: r.start_time)
                    period_label = 'Mingguan'
                else:  # Jika rentang tanggal lebih dari 30 hari, tampilkan data bulanan
                    df_filtered_by_date['periode'] = df_filtered_by_date['tgl_transaksi'].dt.to_period('M').apply(lambda r: r.start_time)
                    period_label = 'Bulanan'

                # Pastikan total_penghasilan dihitung setelah filtering
                if 'total_penghasilan' not in df_filtered_by_date.columns:
                    df_filtered_by_date['total_penghasilan'] = df_filtered_by_date['jumlah'] * df_filtered_by_date['harga']

                # Lakukan agregasi data berdasarkan periode yang baru dibuat
                revenue_by_period = df_filtered_by_date.groupby('periode')['total_penghasilan'].sum().reset_index()
                revenue_by_period = revenue_by_period.sort_values(by='periode')  # Pastikan periode diurutkan secara kronologis

                # Grouping data untuk mendapatkan top 5 toko berdasarkan total_penghasilan
                top_5_toko_propinsi = df_filtered_by_date.groupby('nama_toko')['total_penghasilan'].sum().nlargest(5).reset_index()

                selected_propinsi = st.sidebar.selectbox("Pilih Provinsi", ["Pilih"] + list(df_filtered_by_date['propinsi'].unique()), key="filter_propinsi")

                if selected_propinsi != "Pilih":
                    filtered_df_propinsi = df_filtered_by_date[df_filtered_by_date['propinsi'] == selected_propinsi]
                    selected_kabupaten = st.sidebar.selectbox("Pilih Kabupaten", ["Pilih"] + list(filtered_df_propinsi['kabupaten'].unique()), key="filter_kabupaten")
                    
                    if selected_kabupaten != "Pilih":
                        filtered_df_kabupaten = filtered_df_propinsi[df_filtered_by_date['kabupaten'] == selected_kabupaten]
                        selected_kelurahan = st.sidebar.selectbox("Pilih Kelurahan", ["Pilih"] + list(filtered_df_kabupaten['kelurahan'].unique()), key="filter_kelurahan")
                        
                        if selected_kelurahan != "Pilih":
                            filtered_df_kelurahan = filtered_df_kabupaten[df_filtered_by_date['kelurahan'] == selected_kelurahan]
                            selected_toko = st.sidebar.selectbox("Pilih Toko", ["Pilih"] + list(filtered_df_kelurahan['nama_toko'].unique()), key="filter_toko")
                            
                            if selected_toko != "Pilih":
                                filtered_df = filtered_df_kelurahan[df_filtered_by_date['nama_toko'] == selected_toko]

                                st.markdown(f"<h1 style='text-align: center; color: #3084da; font-family: Inter;'>DASHBOARD <br> {selected_toko}</h1>", unsafe_allow_html=True)

                                # Data Cleaning and Preparation
                                filtered_df['total_penghasilan'] = filtered_df['jumlah'] * filtered_df['harga']
                                
                                # Ringkasan Penghasilan
                                total_revenue = filtered_df['total_penghasilan'].sum()
                                avg_revenue_per_transaction = filtered_df['total_penghasilan'].mean()

                                # Jumlah Jenis Barang Terjual
                                total_unique_items = filtered_df['nama_barang'].nunique()

                                # Top 5 Barang Terlaris
                                top_5_items = filtered_df.groupby('nama_barang')['jumlah'].sum().nlargest(5).reset_index()

                                # Membuat baris untuk Ringkasan Penjualan
                                col1, col2, col3 = st.columns(3)
                                box_style_small = """
                                    background-color: #76db43;
                                    padding: 10px;
                                    border-radius: 15px;
                                    margin: 10px 0;
                                    display: flex;
                                    flex-direction: column;
                                    justify-content: center;
                                    align-items: center;
                                    text-align: center;
                                    color: #cf3c3e;
                                    font-family: 'Inter';
                                """
                                with col1:
                                    st.markdown(
                                        f"<div><h2 style='font-size: 45px; {box_style_small};'>TOTAL<br>PENJUALAN</h2><h3 style='font-size: 40px; color: #76db43; font-family: Inter;'>Rp {total_revenue:,.0f}</h3></div>",
                                        unsafe_allow_html=True
                                    )

                                with col2:
                                    st.markdown(
                                        f"<div><h2 style='font-size: 42px; {box_style_small}'>PENDAPATAN<br>PER {period_label}</h2><h3 style='font-size: 50px; color: #44905f; font-family: Inter;'>Rp {avg_revenue_per_transaction:,.0f}</h3></div>",
                                        unsafe_allow_html=True
                                    )

                                with col3:
                                    st.markdown(
                                        f"<div><h2 style='font-size: 45px; {box_style_small}; '>BARANG<br>TERJUAL</h2><h3 style='font-size: 70px; color: #76db43; font-family: Inter;'>{total_unique_items}</h3></div>",
                                        unsafe_allow_html=True
                                    )

                                # Creating the second row with boxes 4 and 5, making them interactive
                                col4, col5 = st.columns(2)
                                box_style_large = """
                                    background-color: #76db43;
                                    padding: 5px;
                                    border-radius: 10px;
                                    margin: 20px 0;
                                    display: flex;
                                    flex-direction: column;
                                    justify-content: center;
                                    align-items: center;
                                    text-align: center;
                                    color: #cf3c3e; 
                                    font-family: 'Inter';
                                """
                                with col4:
                                    st.markdown(
                                        f"<div style='{box_style_large}'><h3 style='font-size: 40px; color: #cf3c3e;'>PRODUK TERLARIS</h3></div>",
                                        unsafe_allow_html=True
                                    )
                                    fig = px.bar(
                                        top_5_items,
                                        x='jumlah',
                                        y='nama_barang',
                                        orientation='h',  # Mengubah posisi ke vertikal
                                        labels={'jumlah': 'jumlah terjual', 'nama_barang': 'nama_barang'},
                                        text='jumlah',
                                        color_discrete_sequence=['#76db43']  # Set the bar color to green
                                    )
                                    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside', marker=dict(color='#76db43'))
                                    fig.update_layout(xaxis=dict(autorange="reversed"))  # Reverse x-axis for better readability
                                    st.plotly_chart(fig, use_container_width=True)

                                with col5:
                                    st.markdown(
                                        f"<div style='{box_style_large}'><h3 style='font-size: 40px; color: #cf3c3e;'>PENDAPATAN {period_label.upper()}</h3></div>",
                                        unsafe_allow_html=True
                                    )
                                    fig = px.line(
                                        revenue_by_period,
                                        x='periode',
                                        y='total_penghasilan',
                                        markers=True, 
                                        labels={'total_penghasilan': 'Total Penghasilan (Rp)', 'periode': period_label},
                                        line_shape='linear',
                                        color_discrete_sequence=['#76db43']
                                    )
                                    fig.update_layout(xaxis_title=f'Penghasilan {period_label}', yaxis_title='Total Penghasilan (Rp)')
                                    fig.update_xaxes(dtick="M1", tickformat="%d/%m/%Y", tickangle=45)
                                    st.plotly_chart(fig, use_container_width=True)

                                # Button to return to data input page
                                if st.button("KEMBALI", key="back_home"):
                                    st.session_state["logged_in"] = False
                                    st.session_state["df"] = None
                            else:
                                # Menampilkan grafik toko dengan pendapatan terbanyak
                                st.markdown(f"<h2 style='text-align: center;'>Produk Terlaris Kelurahan<br>{selected_kelurahan}</h2>", unsafe_allow_html=True)
                                top_5_items_kelurahan = filtered_df_kelurahan.groupby('nama_barang')['jumlah'].sum().nlargest(5).reset_index()
                                fig1 = px.bar(
                                    top_5_items_kelurahan,
                                    x='jumlah',
                                    y='nama_barang',
                                    labels={'jumlah': 'Jumlah Terjual', 'nama_barang': 'Nama Barang'},
                                    text='jumlah',
                                    color_discrete_sequence=['#76db43']
                                )
                                fig1.update_traces(texttemplate='%{text:.2s}', textposition='outside', marker=dict(color='#76db43'))
                                fig1.update_layout(xaxis=dict(autorange="reversed"))

                                # Grafik pendapatan terbesar
                                top_5_toko_kelurahan = filtered_df_kelurahan.groupby('nama_toko')['total_penghasilan'].sum().nlargest(5).reset_index()
                                fig2 = px.bar(
                                    top_5_toko_kelurahan,
                                    x='total_penghasilan',
                                    y='nama_toko',
                                    orientation='h',  # Tetap gunakan orientasi horizontal
                                    labels={'total_penghasilan': 'Total Penghasilan (Rp)', 'nama_toko': 'Nama Toko'},
                                    text='total_penghasilan',
                                    color_discrete_sequence=['#76db43']
                                )
                                fig2.update_traces(texttemplate='%{text:,.0f}', textposition='outside', marker=dict(color='#76db43'))
                                fig2.update_layout(xaxis=dict(autorange=False), yaxis=dict(autorange="reversed"))  # Mengatur sumbu x agar tidak terbalik
                                fig2.update_layout(xaxis_range=[0, top_5_toko_kelurahan['total_penghasilan'].max() * 1.1])  # Mengatur range sumbu x dari 0 ke maksimum nilai total_penghasilan
                                # Tampilkan kedua grafik berdampingan
                                col6, col7 = st.columns(2)
                                with col6:
                                    st.plotly_chart(fig1, use_container_width=True)
                                with col7:
                                    st.plotly_chart(fig2, use_container_width=True)
                                

                        else:
                            # Hapus grafik kelurahan dan tampilkan grafik kabupaten
                            st.markdown(f"<h2 style='text-align: center;'>Produk Terlaris Kabupaten<br>{selected_kabupaten}</h2>", unsafe_allow_html=True)
                            top_5_items_kabupaten = filtered_df_kabupaten.groupby('nama_barang')['jumlah'].sum().nlargest(5).reset_index()
                            fig1 = px.bar(
                                top_5_items_kabupaten,
                                x='jumlah',
                                y='nama_barang',
                                labels={'jumlah': 'Jumlah Terjual', 'nama_barang': 'Nama Barang'},
                                text='jumlah',
                                color_discrete_sequence=['#76db43']
                            )
                            fig1.update_traces(texttemplate='%{text:.of}', textposition='outside', marker=dict(color='#76db43'))
                            fig1.update_layout(xaxis=dict(autorange="reversed"))
                            
                            # Grafik pendapatan terbesar
                            top_5_toko_kabupaten = filtered_df_kabupaten.groupby('nama_toko')['total_penghasilan'].sum().nlargest(5).reset_index()
                            fig2 = px.bar(
                                top_5_toko_kabupaten,
                                x='total_penghasilan',
                                y='nama_toko',
                                labels={'total_penghasilan': 'Total Penghasilan (Rp)', 'nama_toko': 'Nama Toko'},
                                text='total_penghasilan',
                                color_discrete_sequence=['#76db43']
                            )
                            fig2.update_traces(texttemplate='%{text:,.0f}', textposition='outside', marker=dict(color='#76db43'))
                            fig2.update_layout(xaxis=dict(autorange="reversed"))
                            fig2.update_layout(xaxis_range=[0, top_5_toko_kabupaten['total_penghasilan'].max() * 1.1])
                            # Tampilkan kedua grafik berdampingan
                            col6, col7 = st.columns(2)
                            with col6:
                                st.plotly_chart(fig1, use_container_width=True)
                            with col7:
                                st.plotly_chart(fig2, use_container_width=True)

                    else:
                        # Hapus grafik kabupaten dan tampilkan grafik provinsi
                        st.markdown(f"<h2 style='text-align: center;'>Produk Terlaris Provinsi<br>{selected_propinsi}</h2>", unsafe_allow_html=True)
                        top_5_items_propinsi = filtered_df_propinsi.groupby('nama_barang')['jumlah'].sum().nlargest(5).reset_index()
                        fig1 = px.bar(
                            top_5_items_propinsi,
                            x='jumlah',
                            y='nama_barang',
                            orientation='h',  # Tetap gunakan orientasi horizontal
                            labels={'jumlah': 'Jumlah Terjual', 'nama_barang': 'Nama Barang'},
                            text='jumlah',
                            color_discrete_sequence=['#76db43']
                        )
                        fig1.update_traces(texttemplate='%{text:.0f}', textposition='outside', marker=dict(color='#76db43'))
                        fig1.update_layout(xaxis=dict(autorange="reversed"))

                        # Grafik pendapatan terbesar
                        top_5_toko_propinsi = filtered_df_propinsi.groupby('nama_toko')['total_penghasilan'].sum().nlargest(5).reset_index()
                        fig2 = px.bar(
                            top_5_toko_propinsi,
                            x='total_penghasilan',
                            y='nama_toko',
                            labels={'total_penghasilan': 'Total Penghasilan (Rp)', 'nama_toko': 'Nama Toko'},
                            text='total_penghasilan',
                            color_discrete_sequence=['#76db43']
                        )
                        fig2.update_traces(texttemplate='%{text:,.2s}', textposition='outside', marker=dict(color='#76db43'))
                        fig2.update_layout(xaxis=dict(autorange='reversed'))

                        # Tampilkan kedua grafik berdampingan
                        col6, col7 = st.columns(2)
                        with col6:
                            st.plotly_chart(fig1, use_container_width=True)
                        with col7:
                            st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.markdown("<h3 style='text-align: center;'>Unggah File CSV atau hubungkan dengan Database</h3>", unsafe_allow_html=True)           
        elif data_source == "Koneksi Database":
            st.session_state["df"] = None  # Clear the previous data if connecting to a database
            db_type = st.selectbox("Pilih Jenis Database", ["PostgreSQL", "MySQL", "MongoDB"], key="db_type")

            if db_type == "PostgreSQL":
                host = st.text_input("Host", key="pg_host")
                dbname = st.text_input("Database Name", key="pg_dbname")
                user = st.text_input("User", key="pg_user")
                password = st.text_input("Password", type="password", key="pg_password")
                if st.button("Connect", key="pg_connect"):
                    db_conn = connect_postgresql(host, dbname, user, password)
                    if db_conn:
                        st.success("Berhasil terhubung ke PostgreSQL!")
                        query = st.text_area("Query SQL", "SELECT * FROM your_table_name")
                        if st.button("Execute Query", key="pg_execute"):
                            df = pd.read_sql(query, db_conn)
                            st.session_state["df"] = df

            elif db_type == "MySQL":
                host = st.text_input("Host", key="mysql_host")
                dbname = st.text_input("Database Name", key="mysql_dbname")
                user = st.text_input("User", key="mysql_user")
                password = st.text_input("Password", type="password", key="mysql_password")
                if st.button("Connect", key="mysql_connect"):
                    db_conn = connect_mysql(host, dbname, user, password)
                    if db_conn:
                        st.success("Berhasil terhubung ke MySQL!")
                        query = st.text_area("Query SQL", "SELECT * FROM your_table_name")
                        if st.button("Execute Query", key="mysql_execute"):
                            df = pd.read_sql(query, db_conn)
                            st.session_state["df"] = df

            elif db_type == "MongoDB":
                uri = st.text_input("MongoDB URI", key="mongodb_uri")
                dbname = st.text_input("Database Name", key="mongodb_dbname")
                if st.button("Connect", key="mongodb_connect"):
                    db_conn = connect_mongodb(uri, dbname)
                    if db_conn:
                        st.success("Berhasil terhubung ke MongoDB!")
                        collection = st.text_input("Collection Name", key="mongodb_collection")
                        if collection:
                            df = pd.DataFrame(list(db_conn[collection].find()))
                            st.session_state["df"] = df

        else:
            st.markdown("<h3 style='text-align: center;'>Unggah CSV / Hubungkan Database</h3>", unsafe_allow_html=True)
            if st.button("KEMBALI", key="back"):
                st.session_state["current_page"] = "data_input"
else:
    # Hapus sidebar pada halaman login dan register
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        .stTextInput > div > div > input {
            margin-left: auto;
            margin-right: auto;
            display: block;
        }
        .stButton > button {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    show_login_or_register()



#---- CHATGPT INTEGRATION ----#
# from openai import OpenAI
# # Set up the OpenAI client with your API key
# # client = OpenAI(api_key=st.secrets["API"])
# # ChatGPT Section
# st.subheader("ChatGPT-like Clone")
# # Set a default model
# if "openai_model" not in st.session_state:
#     st.session_state["openai_model"] = "gpt-3.5"

# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Accept user input
# if prompt := st.chat_input("Tanya Chatbot..."):
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     # Display user message in chat message container
#     with st.chat_message("user"):
#         st.markdown(prompt)
    
#     # Generate response from ChatGPT and display
#     with st.chat_message("assistant"):
#         stream = client.chat.completions.create(
#             model=st.session_state["openai_model"],
#             messages=[
#                 {"role": m["role"], "content": m["content"]}
#                 for m in st.session_state.messages
#             ],
#             stream=True,
#         )
#         response = st.write_stream(stream)
#     st.session_state.messages.append({"role": "assistant", "content": response})
