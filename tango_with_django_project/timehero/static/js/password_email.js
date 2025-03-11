 document.addEventListener('DOMContentLoaded', function() {
            const form = document.querySelector('form');
            const emailInput = form.querySelector('input[name="email"]');
            const toastEl = document.getElementById('liveToast');
            const toastBody = document.querySelector('.toast-body');

            function showToast(message) {
                toastBody.textContent = message;
                $(toastEl).toast('show');
            }

            form.addEventListener('submit', function(event) {
                event.preventDefault();
                const email = emailInput.value.trim();
                if (email === '') {
                    showToast('Please enter an email address.');
                    return;
                }

                // Check if the email exists in the database// Wait for the DOM to be fully loaded before executing the script
                document.addEventListener('DOMContentLoaded', function() {
                    // Get references to important DOM elements
                    const form = document.querySelector('form');
                    const emailInput = form.querySelector('input[name="email"]');
                    const toastEl = document.getElementById('liveToast');
                    const toastBody = document.querySelector('.toast-body');

                    /**
                     * Display a toast notification with the specified message
                     * @param {string} message - The message to display in the toast
                     */
                    function showToast(message) {
                        // Set the message text
                        toastBody.textContent = message;
                        // Show the toast using Bootstrap's toast API
                        $(toastEl).toast('show');
                    }

                    // Add event listener for form submission
                    form.addEventListener('submit', function(event) {
                        // Prevent the default form submission behavior
                        event.preventDefault();

                        // Get and trim the email value from the input field
                        const email = emailInput.value.trim();

                        // Basic validation: check if email is empty
                        if (email === '') {
                            showToast('Please enter an email address.');
                            return; // Stop execution if validation fails
                        }

                        // Make an AJAX request to check if the email exists in the database
                        fetch(`/api/ajax_check_email/?email=${email}`)
                            .then(response => response.json())
                            .then(data => {
                                if (data.exists) {
                                    // Email exists in database, proceed with form submission
                                    form.submit();
                                } else {
                                    // Email not found in database, show error message
                                    showToast('The email is not registered.');
                                }
                            })
                            .catch(error => {
                                // Handle any errors that occur during the fetch request
                                console.error('Error:', error);
                                showToast('An error occurred while checking the email.');
                            });
                    });
                });
                fetch(`/api/ajax_check_email/?email=${email}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.exists) {
                            form.submit();
                        } else {
                            showToast('The email is not registered.');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showToast('An error occurred while checking the email.');
                    });
            });
        });