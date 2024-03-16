document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('date-form');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();  // Prevent the form from submitting normally
            var selectedDate = this.elements['selected_date'].value;  // Get the selected date

            fetch(`/your-endpoint?selected_date=${selectedDate}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest', // Important for Django to recognize AJAX
                }
            })
                .then(response => response.text())
                .then(html => {
                    document.getElementById('reservation-table').innerHTML = html;  // Update the table content
                })
                .catch(error => console.error('Error loading the table:', error));
        });
    }
});