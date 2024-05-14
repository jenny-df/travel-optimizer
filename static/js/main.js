////////////////////////////// GENERAL SETUP //////////////////////////////

// Initial value of the slider
var slider = document.getElementById("myRange");
var output = document.getElementById("sliderValue");

output.innerHTML = slider.value + " Days";

// When users move the slider the number of days changes
slider.addEventListener("input", (e) => {
  output.innerHTML = e.target.value + " Days";
});

// Set up data-form's initial value for the date input
var now = new Date();
var currentDate = now.toISOString().split("T")[0];
now.setFullYear(now.getFullYear() + 3);
var farFutureDate = now.toISOString().split("T")[0];
document.getElementById("arrivalDate").setAttribute("min", currentDate);
document.getElementById("arrivalDate").setAttribute("max", farFutureDate);

////////////////////////////// GOOGLE API //////////////////////////////

const markers = {};
let hotel_name = "";

function liTagLocation(loc_name, longitude, latitude, className) {
  const new_li = document.createElement("li");
  new_li.className = className;
  new_li.draggable = "true";
  new_li.innerHTML = loc_name;
  new_li.id = latitude + "$" + longitude;
  new_li.addEventListener("click", (e) => {
    e.target.remove();
    removeMarker(loc_name); // Remove pin from map
  });

  document.getElementById("sortable").appendChild(new_li);
}

function addMarkerToMap(location, map, loc_name, viewport) {
  const marker = new google.maps.Marker({
    position: location,
    map: map,
    title: loc_name,
  });
  markers[loc_name] = marker;

  // Set the best viewing settings on the map to accomodate for
  // the new location (either by Google's recommended view or not.)
  if (viewport) {
    map.fitBounds(viewport);
  } else {
    map.setCenter(location);
    map.setZoom(17);
  }
}

function removeMarker(loc_name) {
  if (markers[loc_name]) {
    markers[loc_name].setMap(null); // Remove marker from the map
    delete markers[loc_name]; // Remove marker from the tracker
  }
}

window.addEventListener("load", (e) => {
  // Autocomplete for MUST SEE locations
  var loc_input = document.getElementById("location-input");
  var loc_autocomplete = new google.maps.places.Autocomplete(loc_input);

  // Listener for when a users selects an option from the autocomplete
  // dropdown menu.
  loc_autocomplete.addListener("place_changed", (e) => {
    const place = loc_autocomplete.getPlace();

    if (!place.geometry) {
      window.alert("No details available for input");
      return;
    }

    const latitude = place.geometry.location.lat();
    const longitude = place.geometry.location.lng();

    // It adds a list element with the autocompleted location and sets its
    // ID to be the longitude and latitude.
    liTagLocation(place.name, longitude, latitude, "loc");

    // Add marker to the map
    addMarkerToMap(
      place.geometry.location,
      map,
      place.name,
      place.geometry.viewport
    );

    // Clear input field and warnings.
    loc_input.value = "";
    loc_input.setCustomValidity("");
  });

  // Autocomplete for hotel location
  var hotel_input = document.getElementsByClassName("hotel_input")[0];
  var hotel_autocomplete = new google.maps.places.Autocomplete(hotel_input);
  var hotel = document.getElementsByClassName("hotel")[0];

  // Listener for when a users selects an option from the autocomplete
  // dropdown menu.
  hotel_autocomplete.addListener("place_changed", (e) => {
    const place = hotel_autocomplete.getPlace();

    if (!place.geometry) {
      window.alert("No details available for this hotel");
      return;
    }

    const latitude = place.geometry.location.lat();
    const longitude = place.geometry.location.lng();

    hotel.value = latitude + "$" + longitude + "$" + place.name;

    // Remove previous hotel (if applicable)
    if (hotel_name !== "") {
      removeMarker(hotel_name);
    }

    // Add marker to the map
    addMarkerToMap(
      place.geometry.location,
      map,
      place.name,
      place.geometry.viewport
    );
    hotel_name = place.name;
  });

  // Map for all locations selected
  const map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: -34.397, lng: 150.644 },
    zoom: 8,
  });

  // Gives priority to search results in the area the user is looking at
  loc_autocomplete.bindTo("bounds", map);
  hotel_autocomplete.bindTo("bounds", map);
});
