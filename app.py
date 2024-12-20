from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_session import Session
import requests
import os
import numpy as np
import requests
import math
import jsonify
app = Flask(__name__)

# Konfigurasi Flask dan MySQL
app.config.from_pyfile('config.cfg')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_pt_thb'
app.config['SECRET_KEY'] = '@#$123456&*()'
app.config['MYSQL_PORT'] = 3306
navbar_admin = app.config['NAVBAR_ADMIN']
navbar_driver = app.config['NAVBAR_DRIVER']
# Konfigurasi Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'  # Menggunakan penyimpanan file untuk session
app.config['SESSION_FILE_DIR'] = './flask_sessions/'  # Direktori penyimpanan
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

# Membuat direktori sesi jika belum ada
if not os.path.exists('./flask_sessions/'):
    os.makedirs('./flask_sessions/')

mysql = MySQL(app)

@app.route('/')
def login():
    return render_template('login.html')

@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['user_id'] = user[0]
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
            return redirect(url_for('login'))
    return render_template('index.html', navbar=navbar_admin)

@app.route('/customer', methods=['GET', 'POST'])
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
def driver():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT `id`, `nama_driver`, `telp`, `platnomor` FROM driver"
    )
    driver = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        nama_driver = request.form['nama_driver']
        telp = request.form['telp']
        platnomor = request.form['platnomor']

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO `driver`(`nama_driver`, `telp`, `platnomor`) "
            "VALUES (%s, %s, %s)",
            (nama_driver, telp, platnomor)
        )
        mysql.connection.commit()
        cursor.close()

        flash('Driver added successfully!', 'success')
        return redirect(url_for('driver'))
    return render_template('driver.html', navbar=navbar_admin, driver=driver)

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

def build_actual_distance_matrix(customers):
    """
    Membangun matriks jarak asli menggunakan OpenRouteService API berdasarkan jalan.
    """
    api_key = '5b3ce3597851110001cf62485c8ef8997b5a46b6b0cf38fca040016e'
    base_url = "https://api.openrouteservice.org/v2/matrix/driving-car"

    # Format koordinat [longitude, latitude]
    coordinates = [[float(c[8]), float(c[7])] for c in customers]
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
def tsp():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, namacustomer, namaperusahaan, tanggalinput, tanggalkirim, telp, alamat, latitude, longitude FROM customer")
    customers = cursor.fetchall()
    cursor.execute("SELECT id, nama_driver FROM driver")
    drivers = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        selected_driver = request.form.get('selected_driver')
        selected_customers = request.form.getlist('customers')  # List of customer IDs
        print(f"Selected Customers: {selected_customers}")
        print(f"Selected Driver: {selected_driver}")
        if not selected_driver or not selected_customers:
            return "Driver atau customer belum dipilih!", 400

        # Ambil data customer yang dipilih
        selected_customers = [c for c in customers if str(c[0]) in selected_customers]
        coordinates = [(float(c[3]), float(c[4])) for c in selected_customers]

        # Membuat matriks jarak
        distance_matrix = build_actual_distance_matrix(selected_customers)
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

        cursor = mysql.connection.cursor()
        for customer in selected_customers:
            cursor.execute("""
                INSERT INTO route (driver_id, customer_id, route_details, total_distance)
                VALUES (%s, %s, %s, %s)
            """, (selected_driver, customer[0], jsonify(route_details), route_details['total_distance']))
        mysql.connection.commit()
        cursor.close()
        
        flash('Route successfully created and saved!', 'success')
        return redirect(url_for('driver_routes'))

    return render_template(
        'tsp.html',
        navbar=navbar_admin,
        customers=customers,
        drivers=drivers
    )

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/login_driver')
def login_driver():
    return render_template('login_driver.html')

@app.route('/index_driver', methods=['GET', 'POST'])
def index_driver():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM driver WHERE username = %s AND password = %s", (username, password))
        driver = cursor.fetchone()
        cursor.close()
        if driver:
            session['user_id'] = driver[0]
            session['driver_name'] = driver[3]
            flash('Login successful!', 'success')
            print(f"Driver Name Stored in Session: {session['driver_name']}")  # Debugging
            return redirect(url_for('index_driver'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
            return redirect(url_for('login_driver'))
    

    driver_name = session.get('driver_name', None)

    navbar_with_driver_name = navbar_driver.replace("{{ driver_name }}", driver_name or "Guest")

    return render_template('index_driver.html', navbar=navbar_with_driver_name)
    #return render_template('index_driver.html', driver_name=driver_name,navbar=navbar_driver)

@app.route('/admin_routes', methods=['GET'])
def admin_routes():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT route.id, driver.nama_driver, customer.namacustomer, route.route_details, route.total_distance
        FROM route
        JOIN driver ON route.driver_id = driver.id
        JOIN customer ON route.customer_id = customer.id
    """)
    routes = cursor.fetchall()
    cursor.close()

    return render_template('admin_routes.html', routes=routes, navbar=navbar_admin)

@app.route('/driver_routes', methods=['GET'])
def driver_routes():
    cursor = mysql.connection.cursor()
    driver_id = session.get('user_id')
    cursor.execute("""
        SELECT route.id, driver.nama_driver, customer.namacustomer, route.route_details, route.total_distance
        FROM route
        JOIN driver ON route.driver_id = driver.id
        JOIN customer ON route.customer_id = customer.id
        WHERE route.driver_id = %s
    """, [driver_id])
    routes = cursor.fetchall()
    cursor.close()

    return render_template('driver_routes.html', routes=routes, navbar=navbar_driver)

    if __name__ == '__main__':
        app.run(debug=True)