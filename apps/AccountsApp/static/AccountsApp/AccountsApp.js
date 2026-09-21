document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.accounts-form');
    const password = document.querySelector('#password');
    const confirmPassword = document.querySelector('#confirm_password');

    if (!form || !password || !confirmPassword) {
        return;
    }

    form.addEventListener('submit', (event) => {
        if (password.value !== confirmPassword.value) {
            event.preventDefault();
            confirmPassword.setCustomValidity('Passwords do not match.');
            confirmPassword.reportValidity();
            return;
        }

        confirmPassword.setCustomValidity('');
    });

    confirmPassword.addEventListener('input', () => {
        if (password.value === confirmPassword.value) {
            confirmPassword.setCustomValidity('');
        } else {
            confirmPassword.setCustomValidity('Passwords do not match.');
        }
    });
});