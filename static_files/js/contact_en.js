window.addEventListener('load', function () {
    var mapEl = document.getElementById('neshanMapContact');
    if (!mapEl || typeof L === 'undefined') return;

    var lat    = 35.75431655694686;
    var lng    = 51.41248217613625;
    var apiKey = 'service.4b130a29422349a7a3210bf2972459f5';

    var map = L.map('neshanMapContact', {
        center: [lat, lng],
        zoom: 16,
        zoomControl: true,
        attributionControl: true
    });

    var neshanFailed = false;
    var neshanLayer  = L.tileLayer(
        'https://map.neshan.org/sdk/v1/map/xyz/dreamy/{z}/{x}/{y}.png?x-api-key=' + apiKey,
        { attribution: '© <a href="https://neshan.org" target="_blank">Neshan</a>', maxZoom: 18 }
    );

    neshanLayer.on('tileerror', function () {
        if (!neshanFailed) {
            neshanFailed = true;
            map.removeLayer(neshanLayer);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© <a href="https://openstreetmap.org" target="_blank">OpenStreetMap</a>'
            }).addTo(map);
        }
    });

    neshanLayer.addTo(map);

    L.marker([lat, lng])
        .addTo(map)
        .bindPopup(
            '<div style="font-family:Inter,Arial,sans-serif;font-size:13px;padding:4px 8px;">' +
            '<strong>Dr. Vahid Abdolrahimi\'s Clinic</strong><br>' +
            '<span style="color:#64748b;">Tehran, Vanak Square</span></div>'
        )
        .openPopup();

    setTimeout(function () { map.invalidateSize(); }, 300);
});
