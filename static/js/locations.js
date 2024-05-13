////////////////////////////// DRAGGABILITY //////////////////////////////

const sortableList = document.getElementById("sortable");
let draggedItem = null;

sortableList.addEventListener("dragstart", (e) => {
  draggedItem = e.target;
  setTimeout(() => {
    e.target.style.display = "none";
  }, 0);
});

sortableList.addEventListener("dragend", (e) => {
  setTimeout(() => {
    e.target.style.display = "";
    draggedItem = null;
  }, 0);
});

sortableList.addEventListener("dragover", (e) => {
  e.preventDefault();
  const afterElement = getDragAfterElement(sortableList, e.clientY);
  const currentElement = document.querySelector(".dragging");
  if (afterElement == null) {
    sortableList.appendChild(draggedItem);
  } else {
    sortableList.insertBefore(draggedItem, afterElement);
  }
});

const getDragAfterElement = (container, y) => {
  const draggableElements = [
    ...container.querySelectorAll("li:not(.dragging)"),
  ];

  return draggableElements.reduce(
    (closest, child) => {
      const box = child.getBoundingClientRect();
      const offset = y - box.top - box.height / 2;
      if (offset < 0 && offset > closest.offset) {
        return {
          offset: offset,
          element: child,
        };
      } else {
        return closest;
      }
    },
    {
      offset: Number.NEGATIVE_INFINITY,
    }
  ).element;
};

////////////////////////////// SUBMISSIONS //////////////////////////////

const data_form = document.getElementById("data-form");
const all_locations = document.getElementById("must-locations");
const all_names = document.getElementById("must-names");
const location_search = document.getElementById("location-input");
var hotel = document.getElementsByClassName("hotel")[0];

data_form.addEventListener("submit", (e) => {
  var locs = [];
  var names = [];

  // Finds all the names, longitudes and latitudes for all locations
  // the user inputted from the autocomplete locations form.
  const list_items = document.getElementsByClassName("loc");
  for (var li_tag of list_items) {
    locs.push(li_tag.id);
    names.push(li_tag.innerHTML);
  }

  // If they didn't enter any location, a warning will be shown and the form
  // won't submit
  if (locs.length == 0) {
    location_search.setCustomValidity("You haven't entered any location!");
    e.preventDefault();
    location_search.reportValidity();
  } else {
    // Otherwise, the data found will be put into hidden inputs so it can
    // reach the backend when the submission goes through after this.
    all_locations.value = locs.join("*");
    all_names.value = names.join("$");
    hotel.value = hotel.id;
  }
});
