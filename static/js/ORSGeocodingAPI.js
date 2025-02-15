
    // OpenRouteService API Key
    const ORS_API_KEY = "5b3ce3597851110001cf62485c8ef8997b5a46b6b0cf38fca040016e"; // Ganti dengan API Key Anda

    // Referensi elemen textarea dan modal
    const alamatTextarea = document.getElementById('alamat');
    const modal = document.querySelector('.modal'); // Pastikan ini referensi ke modal Anda
    let suggestionBox;
    

    // Fungsi untuk menampilkan saran alamat
    function displaySuggestions(suggestions) {
        if (suggestionBox) {
            suggestionBox.remove(); // Hapus kotak saran jika sudah ada
        }

        // Buat elemen untuk menampilkan saran
        suggestionBox = document.createElement('div');
        suggestionBox.style.position = 'absolute';
        suggestionBox.style.backgroundColor = '#fff';
        suggestionBox.style.border = '1px solid #ccc';
        suggestionBox.style.zIndex = '1050'; // Pastikan berada di atas modal konten
        suggestionBox.style.maxHeight = '150px';
        suggestionBox.style.overflowY = 'auto';
        suggestionBox.style.width = `${alamatTextarea.offsetWidth}px`;

        // Posisi kotak saran relatif terhadap textarea dalam modal
        const rect = alamatTextarea.getBoundingClientRect();
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
                alamatTextarea.value = suggestion.properties.label;

                // Masukkan koordinat ke form (jika ada elemen untuk menyimpan koordinat)
                const [lon, lat] = suggestion.geometry.coordinates;
                if (document.getElementById('latitude')) {
                    document.getElementById('latitude').value = lat;
                }
                if (document.getElementById('longitude')) {
                    document.getElementById('longitude').value = lon;
                }

                // Pindahkan marker ke lokasi yang dipilih (jika ada peta)
                if (typeof map !== 'undefined') {
                    if (marker) {
                        marker.setLatLng([lat, lon]).update();
                    } else {
                        marker = L.marker([lat, lon]).addTo(map);
                    }
                    map.setView([lat, lon], 14);
                }

                // Hapus kotak saran setelah dipilih
                suggestionBox.remove();
                suggestionBox = null;
            });

            suggestionBox.appendChild(item);
        });

        modal.appendChild(suggestionBox); // Pastikan kotak saran berada di dalam modal
    }

    // Fungsi untuk mengambil saran alamat dari OpenRouteService
    function fetchAddressSuggestions(query) {
        if (!query) {
            if (suggestionBox) suggestionBox.remove();
            return;
        }

        const geocodeURL = `https://api.openrouteservice.org/geocode/search?api_key=${ORS_API_KEY}&text=${encodeURIComponent(query)}&boundary.rect.min_lon=105.0&boundary.rect.min_lat=-8.0&boundary.rect.max_lon=115.0&boundary.rect.max_lat=-5.5`;

        fetch(geocodeURL)
            .then(response => response.json())
            .then(data => {
                if (data.features && data.features.length > 0) {
                    displaySuggestions(data.features);
                } else {
                    if (suggestionBox) suggestionBox.remove();
                }
            })
            .catch(error => {
                console.error("Error fetching geocoding data:", error);
            });
    }

    // Event Listener untuk input pada textarea
    alamatTextarea.addEventListener('input', function () {
        const query = alamatTextarea.value;
        fetchAddressSuggestions(query);
    });

    // Event untuk menutup saran saat klik di luar kotak
    document.addEventListener('click', function (e) {
        if (suggestionBox && !suggestionBox.contains(e.target) && e.target !== alamatTextarea) {
            suggestionBox.remove();
            suggestionBox = null;
        }
    });

