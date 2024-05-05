// Initial value of the slider
var slider = document.getElementById("myRange");
var output = document.getElementById("sliderValue");

output.innerHTML = slider.value + " Days";

// When users move the slider the number of days changes
slider.oninput = function () {
  output.innerHTML = this.value + " Days";
};

// Set up data-form's initial value for the date input
var now = new Date();
var currentDate = now.toISOString().split("T")[0];
now.setFullYear(now.getFullYear() + 3);
var farFutureDate = now.toISOString().split("T")[0];
document.getElementById("departureDate").setAttribute("min", currentDate);
document.getElementById("departureDate").setAttribute("max", farFutureDate);

// Loading the Google Maps
let map;

async function initMap() {
  const { Map } = await google.maps.importLibrary("maps");

  map = new Map(document.getElementById("map"), {
    center: { lat: -34.397, lng: 150.644 },
    zoom: 8,
  });
}

initMap();
