document.addEventListener("DOMContentLoaded", function () {


const responseType = document.getElementById("response_type");

if (responseType) {

    function updateResponseField() {
        const currentResponseField = document.getElementById("response");
        const type = responseType.value;

        if (!currentResponseField) {
            return;
        }

        currentResponseField.value = "";

        if (type === "BOOLEAN") {
            const select = document.createElement("select");
            select.className = "form-select";
            select.id = "response";
            select.name = "response";
            select.required = true;

            select.innerHTML = ` <option value="">Select response</option> <option value="Yes">Yes</option> <option value="No">No</option> `;

            currentResponseField.replaceWith(select);
            return;
        }

        if (type === "NUMBER") {
            const input = document.createElement("input");
            input.type = "number";
            input.className = "form-control";
            input.id = "response";
            input.name = "response";
            input.required = true;
            input.step = "any";

            currentResponseField.replaceWith(input);
            return;
        }

        if (type === "CHOICE") {
            const input = document.createElement("input");
            input.type = "text";
            input.className = "form-control";
            input.id = "response";
            input.name = "response";
            input.placeholder = "Enter the selected choice.";
            input.required = true;

            currentResponseField.replaceWith(input);
            return;
        }

        const textarea = document.createElement("textarea");
        textarea.className = "form-control";
        textarea.id = "response";
        textarea.name = "response";
        textarea.rows = 3;
        textarea.placeholder = "Enter the response.";
        textarea.required = true;

        currentResponseField.replaceWith(textarea);
    }

    responseType.addEventListener("change", updateResponseField);
}

const responseForm = document.querySelector(
    'form[method="post"]:has(#question_code)'
);

if (responseForm) {
    responseForm.addEventListener("submit", function (event) {
        const questionCode = document.getElementById("question_code");
        const question = document.getElementById("question");
        const response = document.getElementById("response");

        if (!questionCode || !question || !response) {
            return;
        }

        if (!questionCode.value.trim()) {
            event.preventDefault();
            questionCode.focus();
            alert("Question code is required.");
            return;
        }

        if (!question.value.trim()) {
            event.preventDefault();
            question.focus();
            alert("Question is required.");
            return;
        }

        if (!response.value.trim()) {
            event.preventDefault();
            response.focus();
            alert("Response is required.");
        }
    });
}

const completeForm = document.querySelector(
    'form[action*="/complete/"]'
);

if (completeForm) {
    completeForm.addEventListener("submit", function (event) {
        const confirmed = window.confirm(
            "Are you sure you want to complete this screening? No more responses can be added after completion."
        );

        if (!confirmed) {
            event.preventDefault();
        }
    });
}

const reviewForm = document.querySelector(
    'form[action*="/submit-review/"]'
);

if (reviewForm) {
    reviewForm.addEventListener("submit", function (event) {
        const confirmed = window.confirm(
            "Are you sure you want to submit this screening for review?"
        );

        if (!confirmed) {
            event.preventDefault();
        }
    });
}


});
