
const routes = {{route_id.route | tojson}};

var map = L.map('map').setView([-7.614529, 110.712247], 8); // Inisialisasi peta          

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

routes.forEach(([lat, lng], index) => {
    L.marker([lat, lng]).addTo(map)
        .bindPopup(`Point ${index + 1}: (${lat}, ${lng})`);
});

const polyline = L.polyline(routes, {color: 'red', weight: 3}).addTo(map);

map.fitBounds(polyline.getBounds());
console.log("Route data:", route);
