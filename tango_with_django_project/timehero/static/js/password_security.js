document.addEventListener('DOMContentLoaded', function() {
    // Initialize toast
    const toastEl = document.getElementById('liveToast');
    const toastBody = toastEl.querySelector('.toast-body');
    const toast = new bootstrap.Toast(toastEl, {
        animation: true,
        autohide: true,
        delay: 5000
    });



    // Handle form submission
    const form = document.getElementById('reset-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const securityAnswer = form.querySelector('input[name="security_answer"]').value;
        const newPassword = form.querySelector('input[name="new_password"]').value;
        const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;

        // Basic validation
        if (!securityAnswer || !newPassword) {
            toastBody.textContent = "Please fill in all fields";
            toast.show();
            return;
        }

        // Submit form via AJAX
        fetch('', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                security_answer: securityAnswer,
                new_password: newPassword
            })
        })
        .then(response => response.json())
        .then(data => {
            toastBody.textContent = data.message;
            toast.show();

            if (data.success) {
                // Redirect after successful password reset (after toast is shown)
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/login/';
                }, 2000);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            toastBody.textContent = "An error occurred. Please try again.";
            toast.show();
        });
    });
});