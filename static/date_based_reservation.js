document.addEventListener('DOMContentLoaded', function() {
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
                console.log('Before replace:', data.html); // Log the HTML before replace
                let htmlWithoutNewlines = data.html.replace(/\n/g, ''); // Remove newlines
                console.log('After replace:', htmlWithoutNewlines); // Log the HTML after replace
                document.getElementById('reservation-table').innerHTML = htmlWithoutNewlines;
            })
            .catch(error => console.error('Error loading the table:', error));
        });
    }
});
