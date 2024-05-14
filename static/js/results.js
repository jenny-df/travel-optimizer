window.addEventListener("load", (e) => {
  const allMaps = document.getElementsByClassName("maps");

  for (const mapNode of allMaps) {
    // Map for all locations selected
    const map = new google.maps.Map(mapNode, {
      center: { lat: -34.397, lng: 150.644 },
      zoom: 8,
    });
  }
});
