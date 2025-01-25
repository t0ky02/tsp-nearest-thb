from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, logout_user
import requests
import os
import numpy as np
import requests
import math
import jsonify
from utils import login_required
from datetime import datetime, timedelta
app = Flask(__name__)

# Konfigurasi Flask dan MySQL
app.config.from_pyfile('config.cfg')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_thb'
app.config['SECRET_KEY'] = '@#$123456&*()'
app.config['MYSQL_PORT'] = 3306
navbar_admin = app.config['NAVBAR_ADMIN']
navbar_driver = app.config['NAVBAR_DRIVER']
# Konfigurasi Flask-Session
app.config['SESSION_PERMANENT'] = True  # Aktifkan session permanent
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)  # Durasi session (7 hari)
app.config['SESSION_USE_SIGNER'] = True

mysql = MySQL(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['user_id'] = user[1]
            login_user(user[1])
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html') 

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    session.clear()
    logout_user
    return redirect(url_for('login'))

@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)

@app.route('/index')
@login_required
def index():
    flash('Login successful!', 'success')
    return render_template('index.html', navbar=navbar_admin)

@app.route('/customer', methods=['GET', 'POST'])
@login_required
def customer():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT `id`, `namacustomer`, `namaperusahaan`, `tanggalinput`, `tanggalkirim`, `telp`, `alamat`, `latitude`, `longitude` FROM customer"
    )
    customer_data = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
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

        return redirect(url_for('customer'))
    return render_template('customer.html', navbar=navbar_admin, customer=customer_data)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM customer WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    
    cursor = mysql.connection.cursor()
    cursor.execute("CREATE TABLE temp_customer AS SELECT * FROM customer ORDER BY id")
    cursor.execute("TRUNCATE TABLE customer")
    cursor.execute("""
        INSERT INTO customer (namacustomer, namaperusahaan, tanggalinput, tanggalkirim, telp, alamat, latitude, longitude)
        SELECT namacustomer, namaperusahaan, tanggalinput, tanggalkirim, telp, alamat, latitude, longitude
        FROM temp_customer
    """)
    cursor.execute("DROP TABLE temp_customer")
    cursor.execute("ALTER TABLE customer AUTO_INCREMENT = 1")
    mysql.connection.commit()
    cursor.close()
    flash("Customer deleted successfully", "success")
    return redirect('/customer')

@app.route('/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_customer(id):
    if request.method == 'POST':
        namacustomer = request.form['namacustomer']
        namaperusahaan = request.form['namaperusahaan']
        tanggalkirim = request.form['tanggalkirim']
        telp = request.form['telp']
        alamat = request.form['alamat']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        # Update data customer di database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE customer
            SET namacustomer=%s, namaperusahaan=%s, tanggalkirim=%s, telp=%s, alamat=%s, latitude=%s, longitude=%s
            WHERE id=%s
        """, (namacustomer, namaperusahaan, tanggalkirim, telp, alamat, latitude, longitude, id))
        mysql.connection.commit()
        cursor.close()
        flash('Customer updated successfully!', 'success')
        return redirect('/customer')  # Atau sesuai kebutuhan Anda
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM customer WHERE id = %s", (id,))
        customer = cursor.fetchone()
        cursor.close()
        print(customer[6])
        return render_template('edit_customer.html', customer=customer, navbar=navbar_admin)


@app.route('/driver', methods=['GET', 'POST'])
@login_required
def driver():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT `id`, `nama_driver`, `telp`, `platnomor` FROM driver"
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
        cursor.execute("SELECT * FROM driver WHERE username LIKE %s", (f"{username}%",))
        existing_usernames = cursor.fetchall()
        if existing_usernames:
            username += str(len(existing_usernames) + 1)

        # Generate password default
        password = "driver123"  # Bisa disesuaikan atau gunakan generator acak
        #hashed_password = generate_password_hash(password)

        # Masukkan data ke database
        try:
            cursor.execute("""
                INSERT INTO driver (nama_driver, telp, platnomor, username, password)
                VALUES (%s, %s, %s, %s, %s)
            """, (nama_driver, telp, platnomor, username, password))
            mysql.connection.commit()
            flash(f"Driver berhasil ditambahkan! Username: {username}, Password: {password}", "success")
        except Exception as e:
            flash(f"Terjadi kesalahan: {e}", "danger")
        finally:
            cursor.close()
            return redirect(url_for('driver'))
    return render_template('driver.html', navbar=navbar_admin, driver=driver)

@app.route('/delete_driver/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_driver(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM driver WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash("Driver deleted successfully", "success")
    return redirect('/driver')

def get_ors_route(locations):
    """
    Menggunakan OpenRouteService API untuk mendapatkan rute.
    """
    api_key = '5b3ce3597851110001cf62485c8ef8997b5a46b6b0cf38fca040016e'  # Masukkan API Key Anda
    base_url = "https://api.openrouteservice.org/v2/directions/driving-car"
    
    # Format koordinat dalam array [longitude, latitude]
    coordinates = [[lon, lat] for lat, lon in locations]
    payload = {"coordinates": coordinates}
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        # Kirimkan request POST
        response = requests.post(base_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # Ambil jarak total dari respons API (dalam meter)
            return data
        else:
            print("Error: Invalid response from API.")
            print("Status Code:", response.status_code)
            print("Response Content:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    return None

def haversine(lat1, lon1, lat2, lon2):
    """
    Menghitung jarak Haversine antara dua titik berdasarkan latitude dan longitude.
    Menghasilkan jarak dalam kilometer.
    """
    R = 6371  # Radius bumi dalam kilometer
    phi1 = math.radians(lat1)  # Mengonversi latitude dari derajat ke radian
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)  # Selisih latitude
    delta_lambda = math.radians(lon2 - lon1)  # Selisih longitude
    
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c  # Jarak dalam kilometer

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
            distance_matrix = np.array(data['distances']) / 1000.0
            return distance_matrix
        else:
            print(f"Error: API response code {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        return None


def nearest_neighbor_algorithm(distance_matrix):
    """
    Algoritma Nearest Neighbor untuk menyelesaikan TSP menggunakan matriks jarak asli.
    """
    n = len(distance_matrix)
    visited = [False] * n  # Status apakah titik sudah dikunjungi
    route = []  # Menyimpan urutan rute
    current_location = 0  # Mulai dari lokasi pertama (misalnya depot)

    visited[current_location] = True
    route.append(current_location) #memasukan data kedalam array

    for _ in range(n - 1):
        nearest_distance = float('inf')
        next_location = -1

        # Cari lokasi yang belum dikunjungi dengan jarak terdekat
        for i in range(n):
            if not visited[i] and distance_matrix[current_location][i] < nearest_distance:
                nearest_distance = distance_matrix[current_location][i]
                next_location = i

        # Pindah ke lokasi terdekat
        visited[next_location] = True
        route.append(next_location)
        current_location = next_location

    return route


@app.route('/tsp', methods=['GET', 'POST'])
@login_required
def tsp():
    # Mengambil data customer
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, namacustomer, namaperusahaan, tanggalinput, tanggalkirim, telp, alamat, latitude, longitude FROM customer")
    customers = cursor.fetchall()
    # Mengambil data driver
    cursor.execute("SELECT id, nama_driver FROM driver")
    drivers = cursor.fetchall()
    cursor.close()
    
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT routes.id, driver.nama_driver, routes.tanggal_kirim, routes.total_distance
        FROM routes
        JOIN driver ON routes.driver_id = driver.id
    """)
    routes_list = cursor.fetchall()
    cursor.close()

    company_location = -6.218400187288391, 106.4833542644175
    if request.method == 'POST':
        selected_driver = request.form.get('selected_driver')
        selected_customers = request.form.getlist('selected_customers')  # List of customer IDs
        tanggal_kirim = request.form['tanggal_kirim']
        print(f"Selected Customers: {selected_customers}")
        print(f"Selected Driver: {selected_driver}")
        if not selected_driver or not selected_customers:
            return "Driver atau customer belum dipilih!", 400

        # Ambil data customer yang dipilih
        selected_customers = [c for c in customers if str(c[0]) in selected_customers]
        coordinates = [company_location] + [(float(c[7]), float(c[8])) for c in selected_customers]
        
        # Membuat matriks jarak
        distance_matrix = build_actual_distance_matrix(coordinates)
        route = nearest_neighbor_algorithm(distance_matrix)

        # Urutkan koordinat berdasarkan rute
        ordered_coordinates = [coordinates[i] for i in route]
        ordered_coordinates.append(ordered_coordinates[0])

        # Menyimpan data rute dalam database
        route_details = {
            'coordinates': ordered_coordinates,
            'total_distance': round(sum(distance_matrix[route[i]][route[i+1]] for i in range(len(route) - 1)), 2),
            'route_order': route
        }

        print(f"Driver ID: {selected_driver}")
        print(f"Total Distance: {route_details['total_distance']}")
        print(f"Route Details: {route_details}")
        print(f"Route Order: {route_details['route_order']}")
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO routes (driver_id, total_distance, tanggal_kirim, route)
            VALUES (%s, %s, %s, %s)
        """, (selected_driver, route_details['total_distance'], tanggal_kirim, str(route_details['coordinates'])))
        mysql.connection.commit()

        route_id = cursor.lastrowid

    # Menyimpan data detail rute ke tabel `route_details`
        for order_number, customer in enumerate(route_details['route_order']):
            if customer == 0:  # Lewati titik awal (perusahaan)
                continue
            customer_id = selected_customers[customer - 1][0]
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
        route_list = routes_list
    )

@app.route('/delete_route/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_route(id):
    cursor = mysql.connection.cursor()  
    cursor.execute("DELETE FROM routes WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()

    flash("Route deleted successfully", "success")
    return redirect(url_for('tsp'))


@app.route('/login_driver')
def login_driver():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM driver WHERE username = %s AND password = %s", (username, password))
        driver = cursor.fetchone()
        cursor.close()
        if driver and 'user_id' in session:
            session['user_id'] = driver[0]
            session['driver_name'] = driver[3]
            flash('Login successful!', 'success')
            print(f"Driver Name Stored in Session: {session['driver_name']}")  # Debugging
            return redirect(url_for('index_driver'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
            return redirect(url_for('login_driver'))
    return render_template('login_driver.html')

@app.route('/index_driver', methods=['GET', 'POST'])
@login_required
def index_driver():
    session['user_id'] = driver[0]
    session['driver_name'] = driver[3]
    driver_name = session.get('driver_name', None)

    navbar_with_driver_name = navbar_driver.replace("{{ driver_name }}", driver_name or "Guest")

    return render_template('index_driver.html', navbar=navbar_with_driver_name)
    #return render_template('index_driver.html', driver_name=driver_name,navbar=navbar_driver)

@app.route('/driver_rute', methods=['GET'])
@login_required
def driver_routes():
    cursor = mysql.connection.cursor()
    driver_id = session.get('user_id')
    cursor.execute("""
        SELECT routes.id, driver.nama_driver, routes.total_distance ,routes.tanggal_kirim, routes.route
        FROM routes
        JOIN driver ON routes.driver_id = driver.id
        WHERE routes.driver_id = %s
    """, [driver_id])
    routes = cursor.fetchall()
    cursor.close()
    print(f"Session user_id: {session.get('user_id')}")
    driver_name = session.get('driver_name', None)

    navbar_with_driver_name = navbar_driver.replace("{{ driver_name }}", driver_name or "Guest")

    return render_template('driver_rute.html', routes_list=routes, navbar=navbar_with_driver_name)

@app.route('/route_detail/<int:route_id>', methods=['GET'])
@login_required
def route_detail(route_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT routes.id, driver.nama_driver, routes.total_distance, routes.created_at ,routes.tanggal_kirim, routes.route
        FROM routes
        JOIN driver ON routes.driver_id = driver.id
        WHERE routes.id = %s
    """, [route_id])
    route = cursor.fetchone()
    cursor.close()
    
    return render_template('route_detail.html', route_id=route, navbar=navbar_admin)                


if __name__ == '__main__':
    app.run(debug=True)