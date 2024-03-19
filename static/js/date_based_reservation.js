document.addEventListener('DOMContentLoaded', (event) => {
    const date = new Date();
    const today = new Date(date.getTime() - (date.getTimezoneOffset() * 60000))
        .toISOString()
        .split("T")[0];
    document.getElementById('dateInput').value = today;
}); //this puts today's date as defaut value


// loads the schedule
document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('date-form');
    console.log("Form found:", form); // Confirm the form is found
    
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); 
            var selectedDate = this.elements['selected_date'].value;
            console.log("Selected date:", selectedDate); // Log the selected date

            fetch('?selected_date=${selectedDate}', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json()) // Parse the JSON response
            .then(data => {
                //console.log('Before replace:', data.html); // Log the HTML before replace
                let htmlWithoutNewlines = data.html.replace(/\n/g, ''); // Remove newlines
                //console.log('After replace:', htmlWithoutNewlines); // Log the HTML after replace
                document.getElementById('reservation-table').innerHTML = htmlWithoutNewlines;
            })
            .catch(error => console.error('Error loading the table:', error));
        });
    }
});

//row click action does not cover button click action 
//btn-reservation-form

document.addEventListener('DOMContentLoaded', function () {
    //row click action does not cover button click action 
    //btn-reservation-calendar
    document.querySelectorAll('.table .btn-reservation-calendar').forEach(function (button) {
        button.addEventListener('click', function (event) {
            // Stop the event from bubbling up
            event.stopPropagation();

            // Retrieve data attributes
            var offerId = this.getAttribute('data-offer-id');
            var categoryId = this.getAttribute('data-category-id');

            // Construct the URL for the new reservation calendar
            var url = `/new_reservation_timetable/${offerId}/${categoryId}`;

            // Navigate to the URL
            console.log("btn res calendar")
            window.location.href = url;
            
        });
    });
});
document.addEventListener('DOMContentLoaded', function () {
    // Add click event listener for the first button leading to the reservation form
    document.querySelectorAll('.table .btn-reservation-form').forEach(function (button) {
        button.addEventListener('click', function (event) {
            // Stop the event from bubbling up
            event.stopPropagation();

            // Retrieve data attributes
            var offerId = this.getAttribute('data-offer-id');
            var categoryId = this.getAttribute('data-category-id');

            // Construct the URL for the reservation form
            var url = `/new_reservation/${offerId}/${categoryId}`;

            // Navigate to the URL
            console.log("btn res form")
            window.location.href = url;
            
        });
    });
});    
