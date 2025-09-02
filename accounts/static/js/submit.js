document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".code-panel form");
    const languageSelect = document.getElementById("language");
    const codeEditor = document.querySelector(".code-editor");

    form.addEventListener("submit", (event) => {
        let errors = [];

        if (!languageSelect.value.trim()) {
            errors.push("Please select a programming language.");
        }

        if (!codeEditor.value.trim()) {
            errors.push("Please write your solution before submitting.");
        }

        if (errors.length > 0) {
            event.preventDefault();
            showError(errors.join(" "));
        }
    });

    function showError(message) {
        let errorContainer = document.querySelector(".submit-error");

        if (!errorContainer) {
            errorContainer = document.createElement("div");
            errorContainer.className = "submit-error";
            form.parentNode.insertBefore(errorContainer, form);
        }

        errorContainer.textContent = message;

        setTimeout(() => {
            errorContainer.style.display = "none";
        }, 4000);
    }
});

const textarea = document.getElementById("editor");
const lineNumbers = document.getElementById("lineNumbers");

function updateLineNumbers() {
  const lines = textarea.value.split('\n').length;
  let numbers = '';
  for (let i = 1; i <= lines; i++) {
    numbers += i + '\n';
  }
  lineNumbers.textContent = numbers;
}

// Initial
updateLineNumbers();

// Update on input
textarea.addEventListener('input', updateLineNumbers);

// Sync scroll
textarea.addEventListener('scroll', () => {
  lineNumbers.scrollTop = textarea.scrollTop;
});
