if (window.whenVendor) {
    whenVendor('leaflet', function () {
        var mapEl = document.getElementById('neshanMapContact');
        if (!mapEl || typeof L === 'undefined' || mapEl._leaflet_id) return;

        var lat = 35.75431655694686;
        var lng = 51.41248217613625;

        var map = L.map('neshanMapContact', {
            center: [lat, lng],
            zoom: 16,
            zoomControl: true,
            attributionControl: true
        });

        // آدرس قدیمی کاشی نشان ۴۰۴ است و tile.openstreetmap.org هم به‌خاطر
        // Referrer-Policy: same-origin تصویر «Access blocked» برمی‌گرداند.
        L.tileLayer('https://tile.openstreetmap.de/{z}/{x}/{y}.png', {
            attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>',
            maxZoom: 19,
            referrerPolicy: 'strict-origin-when-cross-origin'
        }).addTo(map);

        L.marker([lat, lng])
            .addTo(map)
            .bindPopup(
                '<div dir="rtl" style="font-family:Vazirmatn,Tahoma,sans-serif;font-size:13px;padding:4px 8px;">' +
                '<strong>مطب دکتر وحید عبدالرحیمی</strong><br>' +
                '<span style="color:#64748b;">تهران، میدان ونک</span></div>'
            )
            .openPopup();

        setTimeout(function () { map.invalidateSize(); }, 300);
    });
}
