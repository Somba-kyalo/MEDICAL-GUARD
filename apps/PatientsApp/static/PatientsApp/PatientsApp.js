document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('.patients-form');

    forms.forEach((form) => {
        form.addEventListener('submit', () => {
            const submitButton = form.querySelector('button[type="submit"]');

            if (!submitButton) {
                return;
            }

            submitButton.disabled = true;
            submitButton.textContent = 'Saving...';
        });
    });

    const phoneInputs = document.querySelectorAll(
        'input[type="tel"]'
    );

    phoneInputs.forEach((input) => {
        input.addEventListener('input', () => {
            input.value = input.value.replace(/[^\d+\-\s()]/g, '');
        });
    });

    const timelineItems = document.querySelectorAll(
        '.patients-timeline-item'
    );

    timelineItems.forEach((item) => {
        item.addEventListener('click', () => {
            item.classList.toggle('patients-timeline-item-active');
        });
    });
});