// OpenRouteService API Key
const ORS_API_KEY = "5b3ce3597851110001cf62485c8ef8997b5a46b6b0cf38fca040016e"; // Ganti dengan API Key Anda

// Fungsi untuk menampilkan saran alamat
function displaySuggestions(suggestions, textarea, modal) {
    let suggestionBox = textarea.nextElementSibling; // Cek apakah ada kotak saran yang sudah ada

    if (suggestionBox && suggestionBox.classList.contains("suggestion-box")) {
        suggestionBox.remove();
    }

    // Buat elemen untuk menampilkan saran
    suggestionBox = document.createElement('div');
    suggestionBox.classList.add("suggestion-box");
    suggestionBox.style.position = 'absolute';
    suggestionBox.style.backgroundColor = '#fff';
    suggestionBox.style.border = '1px solid #ccc';
    suggestionBox.style.zIndex = '1050'; // Pastikan berada di atas modal
    suggestionBox.style.maxHeight = '150px';
    suggestionBox.style.overflowY = 'auto';
    suggestionBox.style.width = `${textarea.offsetWidth}px`;
    
    // Posisi kotak saran relatif terhadap textarea dalam modal
    const rect = textarea.getBoundingClientRect();
    const modalRect = modal.getBoundingClientRect();
    suggestionBox.style.left = `${rect.left - modalRect.left}px`;
    suggestionBox.style.top = `${rect.bottom - modalRect.top}px`;

    // Tambahkan saran ke kotak
    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.style.padding = '8px';
        item.style.cursor = 'pointer';
        item.textContent = suggestion.properties.label;

        // Event saat saran diklik
        item.addEventListener('click', () => {
            // Isi textarea dengan alamat yang dipilih
            textarea.value = suggestion.properties.label;

            // Masukkan koordinat ke form (pastikan ada elemen ini di HTML)
            const [lon, lat] = suggestion.geometry.coordinates;
            if (textarea.id === 'alamat') {
                document.getElementById('latitude').value = lat;
                document.getElementById('longitude').value = lon;
            } else if (textarea.id === 'edit_alamat') {
                document.getElementById('edit_latitude').value = lat;
                document.getElementById('edit_longitude').value = lon;
            }

            // Update marker pada peta jika ada
            if (typeof map !== 'undefined') {
                if (textarea.id === 'alamat') {
                    if (marker) {
                        marker.setLatLng([lat, lon]).update();
                    } else {
                        marker = L.marker([lat, lon]).addTo(map);
                    }
                    map.setView([lat, lon], 14);
                } else if (textarea.id === 'edit_alamat' && typeof edit_map !== 'undefined') {
                    if (edit_marker) {
                        edit_marker.setLatLng([lat, lon]).update();
                    } else {
                        edit_marker = L.marker([lat, lon]).addTo(edit_map);
                    }
                    edit_map.setView([lat, lon], 14);
                }
            }

            // Hapus kotak saran setelah dipilih
            suggestionBox.remove();
        });

        suggestionBox.appendChild(item);
    });

    modal.appendChild(suggestionBox); // Pastikan kotak saran berada di dalam modal
}

// Fungsi untuk mengambil saran alamat dari OpenRouteService
function fetchAddressSuggestions(query, textarea, modal) {
    if (!query) {
        const existingBox = textarea.nextElementSibling;
        if (existingBox && existingBox.classList.contains("suggestion-box")) {
            existingBox.remove();
        }
        return;
    }

    const geocodeURL = `https://api.openrouteservice.org/geocode/search?api_key=${ORS_API_KEY}&text=${encodeURIComponent(query)}&boundary.country=ID&boundary.rect.min_lon=105.00&boundary.rect.min_lat=-8.90&boundary.rect.max_lon=114.60&boundary.rect.max_lat=-5.60`;

    fetch(geocodeURL)
        .then(response => response.json())
        .then(data => {
            if (data.features && data.features.length > 0) {
                displaySuggestions(data.features, textarea, modal);
            } else {
                const existingBox = textarea.nextElementSibling;
                if (existingBox && existingBox.classList.contains("suggestion-box")) {
                    existingBox.remove();
                }
            }
        })
        .catch(error => {
            console.error("Error fetching geocoding data:", error);
        });
}

// Event Listener untuk modal Add
const alamatTextarea = document.getElementById('alamat');
const addModal = document.getElementById('addModal'); // Pastikan ID modal benar
alamatTextarea.addEventListener('input', function () {
    fetchAddressSuggestions(alamatTextarea.value, alamatTextarea, addModal);
});

// Event Listener untuk modal Edit
const editAlamatTextarea = document.getElementById('edit_alamat');
const editModal = document.getElementById('editModal'); // Pastikan ID modal benar
editAlamatTextarea.addEventListener('input', function () {
    fetchAddressSuggestions(editAlamatTextarea.value, editAlamatTextarea, editModal);
});

// Event untuk menutup saran saat klik di luar kotak
document.addEventListener('click', function (e) {
    document.querySelectorAll('.suggestion-box').forEach(box => {
        if (!box.contains(e.target) && e.target !== alamatTextarea && e.target !== editAlamatTextarea) {
            box.remove();
        }
    });
});
