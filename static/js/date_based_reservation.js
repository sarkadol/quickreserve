document.addEventListener('DOMContentLoaded', (event) => {
    //console.log("loaded")
    preventButtonEventPropagation('.btn-reservation-calendar', '/new_reservation_timetable/');
    preventButtonEventPropagation('.btn-reservation-form', '/new_reservation/');

    //arrows by the date selection
    document.getElementById('prevDay').addEventListener('click', function () {
        adjustDate(-1);
    });

    document.getElementById('nextDay').addEventListener('click', function () {
        adjustDate(1);
    });
    // Prevent default action for buttons in clickable table rows and navigate programmatically
    function preventButtonEventPropagation(selector, basePath) {
        //console.log("prevent button")
        document.querySelectorAll(selector).forEach(function (button) {
            button.addEventListener('click', function (event) {
                event.stopImmediatePropagation(); // Prevent row click action
                var offerId = this.getAttribute('data-offer-id');
                var categoryId = this.getAttribute('data-category-id');
                var url = `${basePath}${offerId}/${categoryId}`;
                //console.log("Navigation triggered to:", url);
                window.location.href = url;
            });
        });
    }

    // Set today's date as the default value for the date input
    const setDateToToday = () => {
        const dateInput = document.getElementById('dateInput');
        // Check if the dateInput element exists
        if (dateInput) {
            const date = new Date();
            const today = new Date(date.getTime() - (date.getTimezoneOffset() * 60000))
                .toISOString()
                .split("T")[0];
            dateInput.value = today;
            console.log("ISO date set to:", today);
        } else {
            console.log("No date input element found.");
        }
    }

    setDateToToday();

    let startCell = null;
    let endCell = null;
    let currentUnitId = null;

    const form = document.getElementById('date-form');
    //console.log("Form found:", form);

    // New fetch functionality for reservations based on category and date
    if (document.getElementById('categorySelect')) {
        const categorySelect = document.getElementById('categorySelect');
        console.log("category selected: ", categorySelect.value)
    }


    //const categorySelect = document.getElementById('categorySelect');
    const dateInput = document.getElementById('dateInput');

    function fetchReservations() {
        const categoryId = categorySelect.value;
        const selectedDate = dateInput.value;
        if (categoryId && selectedDate) {
            const url = `my_schedule?category_id=${categoryId}&selected_date=${selectedDate}`;
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('reservation-table').innerHTML = data.html;
                });
        }
    }
    if (document.getElementById('categorySelect')) {
        categorySelect.addEventListener('change', fetchReservations);
    }

    dateInput.addEventListener('change', fetchReservations);


    if (form) {
        form.addEventListener('submit', function (event) {
            console.log("submitting form")
            event.preventDefault();
            resetSelection();
            const selectedDate = this.elements['selected_date'].value;
            console.log("Selected date:", selectedDate);

            fetch(`?selected_date=${selectedDate}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
                .then(response => response.json())
                .then(data => {
                    let htmlWithoutNewlines = data.html.replace(/\n/g, '');
                    document.getElementById('reservation-table').innerHTML = htmlWithoutNewlines;
                    preventButtonEventPropagation('.btn-reservation-calendar', '/new_reservation_timetable/');
                    preventButtonEventPropagation('.btn-reservation-form', '/new_reservation/');
                    attachClickableCellListeners();
                })
                .catch(error => console.error('Error loading the table:', error));
        });
        // Automatically submit the form when the date changes
        document.getElementById('dateInput').addEventListener('change', () => {
            form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
            console.log("date submitted")
        });
    }

    const updateSelectionDisplay = () => {
        if (!startCell || !endCell) return;

        const selectedDate = document.getElementById('dateInput').value;
        const dateObject = new Date(selectedDate);
        const formattedDate = dateObject.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

        const startTime = parseInt(startCell.getAttribute('data-hour'), 10);
        const endTime = parseInt(endCell.getAttribute('data-hour'), 10);
        const formattedStartTime = new Date(dateObject.setHours(startTime)).toLocaleTimeString('en-US', { hour: 'numeric', minute: 'numeric', hour12: false });
        const formattedEndTime = new Date(dateObject.setHours(endTime)).toLocaleTimeString('en-US', { hour: 'numeric', minute: 'numeric', hour12: false });

        document.getElementById('selected-date-info').textContent = formattedDate;
        document.getElementById('start-time-info').textContent = formattedStartTime;
        document.getElementById('end-time-info').textContent = formattedEndTime;

        document.getElementById('selection-info').style.display = 'block';
        document.getElementById('nextButton').disabled = false;
    }

    const resetSelection = () => {
        if (startCell) startCell.style.backgroundColor = '';
        if (endCell) [...document.querySelectorAll('.clickable-cell')].forEach(cell => cell.style.backgroundColor = '');
        startCell = null;
        endCell = null;
        currentUnitId = null;
        //console.log("Selection reset.");
        //document.getElementById('nextButton').disabled = true;
        var nextButton = document.getElementById('nextButton');
        if (nextButton) {
            nextButton.disabled = true;
        }
    }

    const highlightRange = (start, end) => {
        let currentCell = start.nextElementSibling;
        while (currentCell && currentCell !== end) {
            currentCell.style.backgroundColor = '#ccffcc';
            currentCell = currentCell.nextElementSibling;
        }
        //console.log("Range highlighted.");
    }

    // Simulate form submission to load the reservation table
    form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));

    function attachClickableCellListeners() {
        const table = document.getElementById('reservation-table');
        //console.log("Table found:", table);
        resetSelection();

        if (table) {
            table.addEventListener('click', function (event) {
                const cell = event.target.closest('.clickable-cell');
                if (!cell || cell.classList.contains('slot-reserved')) return;

                const unitId = cell.getAttribute('data-unit-id');
                const hour = cell.getAttribute('data-hour');
                //console.log("hour: ", hour)
                const categoryId = cell.getAttribute('data-category-id');
                const categoryName = cell.getAttribute('data-category-name');


                // Store the category ID and name in variables accessible to the Next button click handler
                currentCategoryId = categoryId;
                currentCategoryName = categoryName;

                //console.log("Cell clicked for unit ID:", unitId, "at hour:", cell.getAttribute('data-hour'), "in category:", cell.getAttribute('data-category-name'));

                if (startCell === cell || endCell === cell) {
                    //console.log("Clicked on an existing selection, ignoring.");
                    return; // Early return if clicked on the already selected cell
                }

                if (currentUnitId !== unitId) {
                    resetSelection();
                    startCell = cell;
                    currentUnitId = unitId;
                    cell.style.backgroundColor = '#ccffcc';
                    //console.log("Start time set for unit ID:", unitId, "at hour:", cell.getAttribute('data-hour'));
                } else {
                    if (!startCell) {
                        startCell = cell;
                        cell.style.backgroundColor = '#ccffcc';
                    } else if (!endCell && cell.cellIndex > startCell.cellIndex) {
                        // Check for any reserved slots between start and end selection
                        let isSelectionValid = true;
                        let testCell = startCell.nextElementSibling;
                        while (testCell && testCell !== cell.nextElementSibling) {
                            if (testCell.classList.contains('slot-reserved')) {
                                isSelectionValid = false;
                                break;
                            }
                            testCell = testCell.nextElementSibling;
                        }

                        if (!isSelectionValid) {
                            console.log("Selection includes a reserved slot, resetting selection.");
                            resetSelection();
                            return;
                        }
                        endCell = cell;
                        cell.style.backgroundColor = '#ccffcc';
                        highlightRange(startCell, endCell);
                        updateSelectionDisplay();
                    } else {
                        //console.log("Invalid selection. Resetting.");
                        resetSelection();
                    }
                }
            });
        }
        const clickableCells = document.querySelectorAll('.clickable-cell');
        clickableCells.forEach(cell => {
            // Existing click event listener code here

            cell.addEventListener('mouseenter', function () {
                if (!this.style.backgroundColor) { // Only change color if not part of a selection
                    this.style.backgroundColor = 'lightblue';
                }
            });

            cell.addEventListener('mouseleave', function () {
                if (this.style.backgroundColor === 'lightblue') { // Reset only if it was changed on hover
                    this.style.backgroundColor = ''; // Reset to default or you can set it to the initial color
                }
            });
        });
    }

    document.getElementById('nextButton').addEventListener('click', () => {
        //console.log("Next button clicked");
        const dateInput = document.getElementById('dateInput').value;
        let startHour = startCell ? startCell.getAttribute('data-hour') : 'null';
        let endHour = endCell ? endCell.getAttribute('data-hour') : 'null';
        //console.log("startHOUR",startHour)
        // Ensure hours are two digits and use 24-hour format
        startHour = startHour.padStart(2, '0');
        endHour = endHour.padStart(2, '0');

        const selectedStartDate = `${dateInput}T${startHour}:00`;
        const selectedEndDate = `${dateInput}T${endHour}:00`;

        //console.log(`Start DateTime: ${selectedStartDate}, End DateTime: ${selectedEndDate}`);

        const categoryParam = currentCategoryId ? `&category=${encodeURIComponent(currentCategoryId)}` : '';

        window.location.href = `/reservation-details?start=${encodeURIComponent(selectedStartDate)}&end=${encodeURIComponent(selectedEndDate)}${categoryParam}`;
    });


    function adjustDate(days) {
        var dateInput = document.getElementById('dateInput');
        var currentDate = new Date(dateInput.value);
        currentDate.setDate(currentDate.getDate() + days);

        var year = currentDate.getFullYear();
        var month = ('0' + (currentDate.getMonth() + 1)).slice(-2); // Adds leading zero
        var day = ('0' + currentDate.getDate()).slice(-2); // Adds leading zero

        dateInput.value = `${year}-${month}-${day}`;
        // Programmatically submit the form
        document.getElementById('date-form').dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }

    // Invoke these functions at the end to ensure they are attached at the start.

    attachClickableCellListeners(); // Ensure this is called initially too.
});
