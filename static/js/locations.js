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

const data_form = document.getElementById("data-form");
const all_locations = document.getElementById("must-locations");
const all_names = document.getElementById("must-names");
const location_search = document.getElementById("location-input");

data_form.addEventListener("submit", (e) => {
  var locs = [];
  var names = [];
  const list_items = document.getElementsByClassName("loc");
  for (var li_tag of list_items) {
    locs.push(li_tag.id);
    names.push(li_tag.innerHTML);
  }
  console.log(locs);
  if (locs.length == 0) {
    location_search.setCustomValidity("You haven't entered any location!");
    e.preventDefault();
    location_search.reportValidity();
  } else {
    all_locations.value = locs.join("$");
    all_names.value = names.join("$");
  }
});

location_search.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    const new_li = document.createElement("li");
    new_li.className = "loc";
    new_li.draggable = "true";
    new_li.innerHTML = e.target.value;
    new_li.id = "";
    new_li.addEventListener("click", (e) => {
      e.target.remove();
    });

    sortableList.appendChild(new_li);

    e.target.value = "";
    e.target.setCustomValidity("");
  }
});
