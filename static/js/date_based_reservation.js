console.log("javascript")
document.addEventListener('DOMContentLoaded', (event) => {
    // Set today's date as the default value for the date input
    const date = new Date();
    const today = new Date(date.getTime() - (date.getTimezoneOffset() * 60000))
        .toISOString()
        .split("T")[0];
    document.getElementById('dateInput').value = today;

    // Variables to keep track of the reservation start and end
    let startCell = null;
    let endCell = null;
    let currentUnitId = null;

    // Load the schedule on form submission
    var form = document.getElementById('date-form');
    console.log("Form found:", form); // Confirm the form is found
    
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); 
            var selectedDate = this.elements['selected_date'].value;
            console.log("Selected date:", selectedDate); // Log the selected date

            fetch(`?selected_date=${selectedDate}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json()) // Parse the JSON response
            .then(data => {
                let htmlWithoutNewlines = data.html.replace(/\n/g, ''); // Remove newlines
                document.getElementById('reservation-table').innerHTML = htmlWithoutNewlines;
                attachClickableCellListeners(); // Re-attach listeners to the new content
            })
            .catch(error => console.error('Error loading the table:', error));
        });
    }

    // Prevent row click action from covering button click action
    preventButtonEventPropagation('.btn-reservation-calendar', '/new_reservation_timetable/');
    preventButtonEventPropagation('.btn-reservation-form', '/new_reservation/');

    function preventButtonEventPropagation(selector, basePath) {
        document.querySelectorAll(selector).forEach(function(button) {
            button.addEventListener('click', function(event) {
                event.stopPropagation();
                var offerId = this.getAttribute('data-offer-id');
                var categoryId = this.getAttribute('data-category-id');
                var url = `${basePath}${offerId}/${categoryId}`;
                console.log("Navigation triggered to:", url);
                window.location.href = url;
            });
        });
    }

    // Attach click listeners to clickable cells
    //attachClickableCellListeners();

    function attachClickableCellListeners() {
        const table = document.getElementById('reservation-table');
        console.log("Table found:", table);
    
        if (table) {
            table.addEventListener('click', function(event) {
                const cell = event.target.closest('.clickable-cell');
                if (!cell) {
                    return; // If the click wasn't on a cell, do nothing
                }
    
                const unitId = cell.getAttribute('data-unit-id');
                const hour = cell.getAttribute('data-hour');
    
                console.log("Cell clicked for unit ID:", unitId, "at hour:", hour);
    
                // Check if clicking on a different unit or starting a new selection
                if (currentUnitId !== unitId) {
                    console.log("New unit selected or first selection. Resetting.");
                    // Reset previous selections if any
                    resetSelection();
    
                    // Set the new start
                    startCell = cell;
                    currentUnitId = unitId;
                    cell.style.backgroundColor = '#ccffcc'; // Highlight start cell
                    console.log("Start time set for unit ID:", unitId, "at hour:", hour);
                } else {
                    // If we're clicking in the same row/unit
                    if (!startCell) {
                        // If somehow startCell is not set, make this the startCell
                        startCell = cell;
                        cell.style.backgroundColor = '#ccffcc'; // Highlight start cell
                        console.log("Start time set for unit ID:", unitId, "at hour:", hour);
                    } else if (!endCell) {
                        // If startCell is set but endCell is not, set endCell
                        if (cell.cellIndex > startCell.cellIndex) {
                            endCell = cell;
                            cell.style.backgroundColor = '#ccffcc'; // Highlight end cell
                            highlightRange(startCell, endCell); // Highlight all cells between start and end
                            console.log("End time set for unit ID:", unitId, "at hour:", hour);
                        } else {
                            console.log("Selected cell is before the start cell, not setting as end time.");
                        }
                    } else {
                        // If both startCell and endCell are already set, reset and start new selection
                        console.log("Both start and end times were already set. Resetting for a new selection.");
                        resetSelection();
                        startCell = cell;
                        currentUnitId = unitId;
                        cell.style.backgroundColor = '#ccffcc'; // Highlight start cell
                        console.log("Start time set for unit ID:", unitId, "at hour:", hour);
                    }
                }
            });
        }
    }
    
    function resetSelection() {
        // This function will clear the selection background color
        if (startCell) startCell.style.backgroundColor = '';
        if (endCell) {
        [...document.querySelectorAll('.clickable-cell')].forEach(cell => cell.style.backgroundColor = '');
        }
        startCell = null;
        endCell = null;
        console.log("Selection reset.");
    }
    
    function highlightRange(start, end) {
        // This function will highlight all cells between start and end
        let currentCell = start.nextElementSibling;
        while (currentCell && currentCell !== end) {
            currentCell.style.backgroundColor = '#ccffcc';
            currentCell = currentCell.nextElementSibling;
        }
        console.log("Range highlighted.");
    }
});
