document.addEventListener("DOMContentLoaded", function() {
    // This function runs when the DOM is ready, i.e., when the document has been parsed
    $('.clickable-row').click(function() {
        // Retrieve the data-token attribute of the clicked row
        var token = $(this).data('token');
        // Redirect to the reservation confirmation/cancellation page using the token
        window.location.href = `/verify_reservation/${token}`;
    });
});
