from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response, send_from_directory
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
import requests
import numpy as np
import requests
import math
import json
from utils import login_required, admin_required, driver_required, logout_required
from datetime import datetime, timedelta
import openrouteservice
from markupsafe import escape
from livereload import Server


app = Flask(__name__, static_folder='static')

# Konfigurasi Flask dan MySQL
app.config.from_pyfile('config.cfg')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'k@li-linux30'
app.config['MYSQL_DB'] = 'db_thb'
app.config['SECRET_KEY'] = '@#$123456&*()'
app.config['MYSQL_PORT'] = 3306
navbar_admin = app.config['NAVBAR_ADMIN']
navbar_driver = app.config['NAVBAR_DRIVER']
app.config['SESSION_TYPE'] = 'filesystem'
# Konfigurasi Flask-Session
'''

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Durasi session (7 hari)
'''
app.config['SESSION_PERMANENT'] = False # Aktifkan session permanent
app.config['SESSION_USE_SIGNER'] = False

mysql = MySQL(app)

def breadcrumb_url():
    referer = request.referrer  # Mendapatkan URL sebelumnya
    if referer and 'tsp' in referer:
        breadcrumb = [
            {'name': 'Home', 'url': '/index'},
            {'name': 'TSP', 'url': '/tsp'},
            {'name': 'Rute Detail', 'url': None}
        ]
    else:
        breadcrumb = [
            {'name': 'Home', 'url': '/index'},
            {'name': 'Daftar Pengiriman', 'url': '/daftar_pengiriman'},
            {'name': 'Rute Detail', 'url': None}
        ]
    return breadcrumb

@app.route('/', methods=['GET', 'POST'])
@logout_required
def login():
    print("Session setelah logout:", session)  # Debug setelah logout
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['user_id'] = user[0]  # ID user
            session['username'] = user[1]  # Username
            session['role'] = user[3]  # Role (admin or driver)
            
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('session')  # Hapus cookie session
    return response

@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)

@app.route('/index')
@login_required
def index():
    session_name = session.get('username', None)
    if session['role'] == 'admin':
        return render_template('index.html', navbar=navbar_admin)
    elif session['role'] == 'driver':
        
        navbar_driver_name = navbar_driver.replace("{{ session_name }}", session_name or "Guest")
        return render_template('index.html', navbar=navbar_driver_name)

@app.route('/customer', methods=['GET', 'POST'])
@admin_required
@login_required
def customer():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT `id`, `namacustomer`, `namaperusahaan`, `tanggalinput`, `tanggalkirim`, `telp`, `alamat`, `latitude`, `longitude` FROM customer"
    )
    display_customer = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        try:
            namacustomer = request.form['namacustomer']
            namaperusahaan = request.form['namaperusahaan']
            tanggalinput = request.form['tanggalinput']
            tanggalkirim = request.form['tanggalkirim']
            telp = request.form['telp']
            alamat = request.form['alamat']
            latitude = request.form['latitude']
            longitude = request.form['longitude']

            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO `customer`(`namacustomer`, `namaperusahaan`, `tanggalinput`, `tanggalkirim`, `telp`, `alamat`, `latitude`, `longitude`) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (namacustomer, namaperusahaan, tanggalinput, tanggalkirim, telp, alamat, latitude, longitude)
            )
            mysql.connection.commit()
            cursor.close()
            flash('Customer added successfully!', 'success')
            flash(f'Customer "{namacustomer}" berhasil ditambahkan!', 'success')
        except Exception as e:
            flash(f'Error adding customer: {e}', 'danger')
            print(e)
        return redirect(url_for('customer'))
    return render_template('customer.html', navbar=navbar_admin, customer = display_customer)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@admin_required
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM customer WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash("Customer berhasil dihapus", "success")
    return redirect('/customer')

@app.route('/getedit/<int:id>', methods=['GET'])
@admin_required
@login_required
def getedit(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM customer WHERE id = %s", (id,))
    edit_customer = cursor.fetchone()
    cursor.close()
    if edit_customer:
        # Ubah data ke format JSON
        print("edit_customer", edit_customer, flush=True)
        return jsonify({
            'id': edit_customer[0],
            'namacustomer': edit_customer[1],
            'namaperusahaan': edit_customer[2],
            'tanggalinput': edit_customer[3],
            'tanggalkirim': edit_customer[4],
            'telp': edit_customer[5],
            'alamat': edit_customer[6],
            'latitude': edit_customer[7],
            'longitude': edit_customer[8]
        })
    else:
        return jsonify({'error': 'Data tidak ditemukan'}), 404

@app.route('/edit/<int:id>', methods=['POST'])
@admin_required
@login_required
def edit_customer(id):
    if request.method == 'POST':
        try:
            namacustomer = request.form['namacustomer']
            namaperusahaan = request.form['namaperusahaan']
            tanggalinput = request.form['tanggalinput']
            tanggalkirim = request.form['tanggal_kirim']
            telp = request.form['telp']
            alamat = request.form['alamat']
            latitude = request.form['latitude']
            longitude = request.form['longitude']
            # Update data customer di database
            cursor = mysql.connection.cursor()
            cursor.execute("""
                UPDATE customer
                SET namacustomer=%s, namaperusahaan=%s, tanggalinput=%s, tanggalkirim=%s, telp=%s, alamat=%s, latitude=%s, longitude=%s
                WHERE id=%s
            """, (namacustomer, namaperusahaan, tanggalinput, tanggalkirim, telp, alamat, latitude, longitude, id))

            cursor.execute("SELECT DISTINCT route_id FROM route_details WHERE customer_id = %s", (id,))
            routes_to_update = cursor.fetchall()

    # Jalankan perhitungan ulang untuk setiap rute yang terdampak
            for route in routes_to_update:
                recalculate_tsp(route[0])
            mysql.connection.commit()
            cursor.close()
            flash(f"Customer '{namacustomer}' berhasil diperbarui", "success")
            return redirect(url_for('customer'))
        except Exception as e:
            flash(f'Error updating customer: {e}', 'danger')
            print(e)
            return redirect(url_for('customer'))

@app.route('/driver', methods=['GET', 'POST'])
@admin_required
@login_required
def driver():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT `driver_id`, `nama`, `telp`, `platnomor` FROM driver"
    )
    driver = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        nama_driver = request.form['nama_driver']
        platnomor = request.form['platnomor']
        telp = request.form['telp']
        # Buat username otomatis
        username = nama_driver.lower().replace(" ", ".")
        
        # Validasi username unik
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username LIKE %s", (f"{username}%",))
        existing_usernames = cursor.fetchall()
        if existing_usernames:
            username += str(len(existing_usernames) + 1)

        # Generate password default
        password = "driver123"  # Bisa disesuaikan atau gunakan generator acak
        #hashed_password = generate_password_hash(password)

        # Masukkan data ke database
        try:
            cursor.execute("""
                INSERT INTO user (username, password, role)
                VALUES (%s, %s, 'driver')
            """, (username, password))
            
            # Ambil ID driver yang baru ditambahkan
            driver_id = cursor.lastrowid

            # Masukkan data driver ke tabel driver
            cursor.execute("""
                INSERT INTO driver (driver_id, nama, platnomor, telp)
                VALUES (%s, %s, %s, %s)
            """, (driver_id, nama_driver, platnomor, telp))

            # Commit transaksi
            mysql.connection.commit()
            flash(f"Driver berhasil ditambahkan! Username: {username}, Password: {password}", "success")
        except Exception as e:
            flash(f"Terjadi kesalahan: {e}", "danger")
        finally:
            cursor.close()
            return redirect(url_for('driver'))
    return render_template('driver.html', navbar=navbar_admin, driver=driver)

@app.route('/getedit_driver/<int:id>', methods=['GET'])
@admin_required
@login_required
def getedit_driver(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM driver WHERE driver_id = %s", (id,))
    edit_driver = cursor.fetchone()
    cursor.close()
    if edit_driver:
        # Ubah data ke format JSON
        return jsonify({
            'id': edit_driver[0],
            'nama_driver': edit_driver[2],
            'platnomor': edit_driver[3],
            'telp': edit_driver[4]
        })
    else:
        return jsonify({'error': 'Data tidak ditemukan'}), 404

@app.route('/edit_driver/<int:id>', methods=['POST'])
@admin_required
@login_required
def edit_driver(id):
    if request.method == 'POST':
        try:
            nama_driver = request.form['nama_driver']    
            platnomor = request.form['platnomor']
            telp = request.form['telp']
            # Update data driver di database
            cursor = mysql.connection.cursor()
            cursor.execute("""
                UPDATE driver
                SET nama=%s, platnomor=%s, telp=%s
                WHERE id=%s
            """, (nama_driver, platnomor, telp, id))
            mysql.connection.commit()
            cursor.close()
            flash(f"Driver '{nama_driver}' berhasil diperbarui", "success")
            return redirect(url_for('driver'))
        except Exception as e:
            flash(f'Error updating driver: {e}', 'danger')
            print(e)
            return redirect(url_for('driver'))

@app.route('/delete_driver/<int:id>', methods=['GET', 'POST'])
@admin_required
@login_required
def delete_driver(id):

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM driver where driver_id = %s", (id,))
    driver = cursor.fetchone()
    cursor.close()
    nama = driver[2]

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM user WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash(f"Driver '{nama}' berhasil dihapus", "success")
    return redirect('/driver')

def build_actual_distance_matrix(coordinates):
    """
    Membangun matriks jarak asli menggunakan OpenRouteService API berdasarkan jalan.
    """
    api_key = '5b3ce3597851110001cf62485c8ef8997b5a46b6b0cf38fca040016e'
    base_url = "https://api.openrouteservice.org/v2/matrix/driving-car"

    # Format koordinat [longitude, latitude]
    coordinates = [[c[1], c[0]] for c in coordinates]
    
    payload = {
        "locations": coordinates,
        "metrics": ["distance"]
    }

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    try:
        # Kirim request POST ke ORS untuk mendapatkan matriks jarak
        response = requests.post(base_url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Matriks jarak dalam meter (konversikan ke kilometer)
            distance_matrix = np.array(data['distances']) / 1000
            print(f"Koordinat {coordinates}")
            print(distance_matrix)
            return distance_matrix
        else:
            print(f"Error: API response code {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        return None

def nearest_neighbor_algorithm(distance_matrix, start_index=0):
    """
    Algoritma Nearest Neighbor untuk menyelesaikan TSP dengan titik awal tetap.
    """
    n = len(distance_matrix)
    visited = [False] * n
    route = [start_index]  # Mulai dari titik awal
    visited[start_index] = True
    current_location = start_index

    for _ in range(n - 1):
        nearest_distance = float('inf')
        next_location = -1

        for i in range(n):
            if not visited[i] and distance_matrix[current_location][i] < nearest_distance:
                nearest_distance = distance_matrix[current_location][i]
                next_location = i

        if next_location == -1:
            break  # Menghindari error jika tidak ada kandidat

        visited[next_location] = True
        route.append(next_location)
        current_location = next_location

    return route  # Tidak perlu menambahkan kembali start_index, bisa ditangani di luar



################## TSP ##################
@app.route('/tsp', methods=['GET', 'POST'])
@admin_required
@login_required
def tsp():


    # Mengambil data customer
    cursor = mysql.connection.cursor()
    # Mengambil hanya tanggal_kirim yang unik dari data customer
    cursor.execute("SELECT DISTINCT tanggalkirim, status FROM customer WHERE status='available' ORDER BY tanggalkirim ASC")
    unique_dates = cursor.fetchall()

    cursor.execute("SELECT id, namacustomer, namaperusahaan, tanggalinput, tanggalkirim, telp, alamat, latitude, longitude FROM customer where status='available'")
    customers = cursor.fetchall()
    # Mengambil data driver
    cursor.execute("SELECT id, nama FROM driver")
    drivers = cursor.fetchall()
    cursor.close()
    
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT routes.id, driver.nama, routes.tanggal_kirim, routes.total_distance
        FROM routes
        JOIN driver ON routes.driver_id = driver.id
    """)
    routes_list = cursor.fetchall()
    cursor.close()

    company_location =[-6.218400187288391, 106.4833542644175]
    if request.method == 'POST':
        selected_driver = request.form.get('selected_driver')
        selected_customers = request.form.getlist('selected_customers')  # List of customer IDs
        tanggal_kirim = request.form['tanggal_kirim']

        if not selected_driver or not selected_customers:
            return "Driver atau customer belum dipilih!", 400
        

        # Ambil data customer yang dipilih
        selected_customers = [c for c in customers if str(c[0]) in selected_customers]
        cursor = mysql.connection.cursor()

        # Ensure selected_customers is a list of IDs
        if selected_customers:
            customer_ids = [customer[0] for customer in selected_customers] #extract only the id's
            format_strings = ','.join(['%s'] * len(customer_ids))  # Creates (%s, %s, %s, ...)
            query = f"""
                UPDATE customer 
                SET status='no_available'
                WHERE status='available'
                AND id IN ({format_strings})
            """
            cursor.execute(query, tuple(customer_ids))  # Pass values as tuple
            mysql.connection.commit()
            cursor.close()
        else:
            print("No valid customers selected")

        coordinates = [company_location] + [[float(c[7]), float(c[8])] for c in selected_customers]
        # Membuat matriks jarak
        distance_matrix = build_actual_distance_matrix(coordinates)
        route = nearest_neighbor_algorithm(distance_matrix, start_index=0)
        route.append(0)
        # Urutkan koordinat berdasarkan rute
        ordered_coordinates = [coordinates[i] for i in route]
        

        # Menyimpan data rute dalam database
        route_details = {
            'coordinates': ordered_coordinates,
            'total_distance': round(sum(distance_matrix[route[i]][route[i+1]] for i in range(len(route) - 1)), 2),
            'route_order': route
        }
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO routes (driver_id, total_distance, tanggal_kirim, route)
            VALUES (%s, %s, %s, %s)
        """, (selected_driver, route_details['total_distance'], tanggal_kirim, str(route_details['coordinates'])))
        mysql.connection.commit()

        route_id = cursor.lastrowid

        for order_number, customer in enumerate(route_details['route_order']):
            if customer == 0 or customer == len(route_details['route_order']) - 1:  
                continue  # Lewati perusahaan (awal dan akhir)

            customer_index = customer - 1  # Kurangi 1 karena perusahaan ada di index 0
            if customer_index < len(selected_customers):  # Pastikan index valid
                customer_id = selected_customers[customer_index][0]

                cursor.execute("""
                    INSERT INTO route_details (route_id, customer_id, order_index)
                    VALUES (%s, %s, %s)
                """, (route_id, customer_id, order_number))
        

        mysql.connection.commit()
        cursor.close()
        print([route_details['total_distance']])
        flash('Route successfully created and saved!', 'success')
        return redirect(url_for('tsp'))

    return render_template(
        'tsp.html',
        navbar=navbar_admin,
        customers=customers, 
        drivers=drivers,
        route_list = routes_list,
        unique_dates = unique_dates
    )

############### PROSES ULANG TSP DAN UPDATE TABLE TERKAIT SAAT DATA CUSTOMER ADA YANG DI EDIT ##################
@app.route('/recalculate_tsp/<int:route_id>', methods=['POST'])
@admin_required
@login_required
def recalculate_tsp(route_id):
    cursor = mysql.connection.cursor()

    # Ambil data customer dalam rute ini
    cursor.execute("""
        SELECT customer.id, customer.latitude, customer.longitude
        FROM route_details
        JOIN customer ON route_details.customer_id = customer.id
        WHERE route_details.route_id = %s
    """, (route_id,))
    customers = cursor.fetchall()
    
    if not customers:
        return jsonify({"message": "Tidak ada customer dalam rute ini"}), 400

    company_location =[-6.218400187288391, 106.4833542644175]
    # Siapkan daftar koordinat
    coordinates = [company_location] + [[float(c[1]), float(c[2])] for c in customers]

    # Buat ulang matriks jarak
    distance_matrix = build_actual_distance_matrix(coordinates)
    route = nearest_neighbor_algorithm(distance_matrix, start_index=0)
    route.append(0)
    # Urutkan koordinat berdasarkan rute
    ordered_coordinates = [coordinates[i] for i in route]

    # Hitung total jarak
    total_distance = round(sum(distance_matrix[route[i]][route[i+1]] for i in range(len(route))), 2)

    # Update tabel routes
    cursor.execute("""
        UPDATE routes 
        SET total_distance = %s, route = %s
        WHERE id = %s
    """, (total_distance, json.dumps(ordered_coordinates), route_id))

    for order_number, customer in enumerate(route):
            if customer == 0 or customer == len(route) - 1:  
                continue  # Lewati perusahaan (awal dan akhir)

            customer_index = customer - 1  # Kurangi 1 karena perusahaan ada di index 0
            if customer_index < len(customer):  # Pastikan index valid
                customer_id = customer[customer_index][0]

                cursor.execute("""
                    INSERT INTO route_details (route_id, customer_id, order_index)
                    VALUES (%s, %s, %s)
                """, (route_id, customer_id, order_number))

    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Rute berhasil diperbarui!"}), 200


############### DELETE ROUTE ###################
@app.route('/delete_route/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_route(id):
    cursor = mysql.connection.cursor()

    # 1. Retrieve customer IDs from route_details
    cursor.execute("""
        SELECT customer_id FROM route_details WHERE route_id = %s
    """, (id,))
    customer_ids = [row[0] for row in cursor.fetchall()]

    # 2. Update customer statuses
    if customer_ids:  # Check if any customer IDs were found
        format_strings = ','.join(['%s'] * len(customer_ids))
        query = f"""
            UPDATE customer 
            SET status='available'
            WHERE status='no_available'
            AND id IN ({format_strings})
        """
        try:
            cursor.execute(query, tuple(customer_ids))
            mysql.connection.commit()
        except Exception as e:
            print(f"Error updating customer statuses: {e}")
            mysql.connection.rollback()
    else:
        print("No customer IDs found for this route.")

    cursor = mysql.connection.cursor()  
    cursor.execute("DELETE FROM routes WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()

    flash("Route deleted successfully", "success")
    return redirect(url_for('tsp'))

@app.route('/daftar_pengiriman', methods=['GET'])
@driver_required
@login_required
def driver_routes():
    user_id = session.get('user_id', None)
    session_name = session.get('username', None)
    navbar_driver_name = navbar_driver.replace("{{ session_name }}", session_name or "Guest")
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id from driver WHERE driver_id = %s
    """, [user_id]
    )
    get_id_from_driver = cursor.fetchall()
    driver_id = get_id_from_driver[0]
    print(driver_id)
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT routes.id, routes.total_distance, routes.tanggal_kirim, routes.route
        FROM routes
        JOIN driver ON routes.driver_id = driver.id
        WHERE routes.driver_id = %s
    """, [driver_id]
    )
    routes = cursor.fetchall()
    cursor.close()
    return render_template('daftar_rute.html', routes_list=routes, navbar=navbar_driver_name)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
@driver_required
def profile():
    session_name = session.get('username', None)
    navbar_driver_name = navbar_driver.replace("{{ session_name }}", session_name or "Guest")
    
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT username, password from user WHERE id = %s
    """, [session['user_id']]
    )
    user = cursor.fetchone()
    cursor.close()

    return render_template('profile.html', navbar=navbar_driver_name, user = user)

@app.route('/profile/account_settings', methods=['GET', 'POST'])
@login_required
@driver_required
def account_settings():
    session_name = session.get('username', None)
    navbar_driver_name = navbar_driver.replace("{{ session_name }}", session_name or "Guest")

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT username, password FROM user WHERE id = %s", [session['user_id']])
    user = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        # Cek apakah input ada dalam request
        if 'password' not in request.form or 'confirm_password' not in request.form:
            flash("Terjadi kesalahan. Pastikan semua data diisi.", "danger")
            return redirect(url_for('account_settings'))
        
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Password tidak sama dengan konfirmasi password.", "danger")
            return redirect(url_for('account_settings'))

        # Update password di database
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE user SET password=%s WHERE id=%s", (password, session['user_id']))
        mysql.connection.commit()  # Jangan lupa commit perubahan!
        cursor.close()

        flash("Password berhasil diganti.", "success")
        return redirect(url_for('profile'))

    return render_template('account_settings.html', navbar=navbar_driver_name, user=user)


################## DETAIL ROUTE ##################
@app.route('/route_detail/<int:route_id>', methods=['GET'])
@login_required
def route_detail(route_id):

    breadcrumb = breadcrumb_url()

    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("""
        SELECT routes.id, driver.nama, routes.total_distance, routes.created_at ,routes.tanggal_kirim, routes.route
        FROM routes
        JOIN driver ON routes.driver_id = driver.id ### Perbaiki baris ini
        WHERE routes.id = %s
    """, [route_id])
    route = cursor.fetchone()
    cursor.close()

    route['route'] = json.loads(route['route'])
    print("f daftar route", route['route'])

    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("""
        SELECT c.namacustomer, c.namaperusahaan, c.telp, c.alamat, rd.order_index
        FROM route_details rd
        JOIN customer c ON rd.customer_id = c.id
        WHERE rd.route_id = %s
        ORDER BY rd.order_index
    """, [route_id])
    route_detail = cursor.fetchall()
    cursor.close()

    # Proses jalur dengan OpenRouteService
    ORS_API_KEY = "5b3ce3597851110001cf62485c8ef8997b5a46b6b0cf38fca040016e"  # Ganti dengan API Key Anda
    client = openrouteservice.Client(key=ORS_API_KEY)

    # Ubah koordinat ke format yang benar untuk OpenRouteService (lng, lat)
    coordinates = [(lng, lat) for lat, lng in route['route']]

    try:
        response = client.directions(
            coordinates=coordinates,
            profile="driving-car",
            format="geojson"
        )
        if 'features' in response and response['features']:
            route_data = response['features'][0]  # Ambil fitur pertama
            geometry = route_data.get('geometry', {}).get('coordinates', [])
            properties = route_data.get('properties', {})
            segments = properties.get('segments', [])  # Ambil data segmen
            
            # Hitung jarak antar titik
            distances = []
            for segment in segments:
                distances.append(segment.get('distance', 0) / 1000.0)  # Konversi ke km
            print (f"Distance Segment: ", distances)
            print("Rute berhasil diambil!")
            # print("Koordinat geometry:", geometry)
            print("Ringkasan:", properties.get('summary', {}))
            
            route_geometry = json.dumps(geometry)
        else:
            print("Tidak ada data rute yang ditemukan dalam respons ORS")
            #print("ORS Response:", response)  # Tambahkan ini untuk debugging
            route_geometry = None
    except Exception as e:
        print(f"Error fetching route: {e}")
        route_geometry = None
    navbar = navbar_admin if session['role'] == 'admin' else navbar_driver.replace("{{ session_name }}", session.get('username', 'Guest'))

    return render_template(
        'route_detail.html',
        route_id=route,
        navbar=navbar,
        route_detail=route_detail,
        route_geometry= route_geometry,
        distances = distances,
        breadcrumb=breadcrumb
    )

if __name__ == "__main__":
    app.debug = True
    server = Server(app.wsgi_app)
    server.watch("*.py")  # Pantau perubahan file Python
    server.watch("templates/*.html")  # Pantau perubahan HTML
    server.watch("static/css/*.css")  # Pantau perubahan CSS
    server.watch("static/js/*.js")  # Pantau perubahan JavaScript
    server.watch("static/img/*.png")
    server.serve(port=5000, host='0.0.0.0', debug=True)
    app.run(debug=True)