// static/js/map_modal.js
(function() {
    // Popup map modal logic
    let popupMap = null, popupMarker = null;
    const mapPopupModal = document.getElementById('map-popup-modal');
    const popupMapDiv = document.getElementById('popup-map');
    const closeMapPopup = document.getElementById('close-map-popup');
    const closeMapPopupBtn = document.getElementById('close-map-popup-btn');
    const mapFullscreenBtn = document.getElementById('map-fullscreen-btn');
    const latInput = document.getElementById('latitude-input');
    const lngInput = document.getElementById('longitude-input');

    function showPopupMap() {
        mapPopupModal.classList.remove('hidden');
        setTimeout(() => {
            let lat = parseFloat(latInput.value) || 7.4475;
            let lng = parseFloat(lngInput.value) || 125.8078;
            if (!popupMap) {
                popupMap = L.map('popup-map').setView([lat, lng], 14);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors'
                }).addTo(popupMap);
                popupMarker = L.marker([lat, lng]).addTo(popupMap);
                popupMap.on('click', function(e) {
                    const { lat, lng } = e.latlng;
                    latInput.value = lat;
                    lngInput.value = lng;
                    popupMarker.setLatLng([lat, lng]);
                });
            } else {
                popupMap.setView([lat, lng], 14);
                popupMarker.setLatLng([lat, lng]);
            }
            setTimeout(() => { popupMap.invalidateSize(); }, 100);
        }, 100);
    }
    if (mapFullscreenBtn) {
        mapFullscreenBtn.addEventListener('click', showPopupMap);
    }
    function hidePopupMap() {
        mapPopupModal.classList.add('hidden');
        // No need to call popupMap.remove() anymore
    }
    if (closeMapPopup) closeMapPopup.addEventListener('click', hidePopupMap);
    if (closeMapPopupBtn) closeMapPopupBtn.addEventListener('click', hidePopupMap);
})(); 