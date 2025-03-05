// ⭐ Star Rating Hover Effect
document.addEventListener("DOMContentLoaded", () => {
    const stars = document.querySelectorAll(".star-rating label");

    stars.forEach((star) => {
        star.addEventListener("mouseover", () => {
            star.classList.add("hover");
            let previous = star.previousElementSibling;
            while (previous) {
                previous.classList.add("hover");
                previous = previous.previousElementSibling;
            }
        });

        star.addEventListener("mouseout", () => {
            stars.forEach(s => s.classList.remove("hover"));
        });
    });
});

// ⭐ Star Rating Hover Effect for Feedback
document.addEventListener("DOMContentLoaded", () => {
    const stars = document.querySelectorAll(".star-rating label");

    stars.forEach((star) => {
        star.addEventListener("mouseover", () => {
            star.classList.add("hover");
            let previous = star.previousElementSibling;
            while (previous) {
                previous.classList.add("hover");
                previous = previous.previousElementSibling;
            }
        });

        star.addEventListener("mouseout", () => {
            stars.forEach(s => s.classList.remove("hover"));
        });
    });
});


document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("addBookForm");
    const titleInput = document.getElementById("title");
    const authorInput = document.getElementById("author");
    const quantityInput = document.getElementById("quantity");
    const titleError = document.getElementById("titleError");
    const authorError = document.getElementById("authorError");
    const quantityError = document.getElementById("quantityError");
    const quantityFeedback = document.getElementById("quantity-feedback");
    const dropZone = document.getElementById("drop-zone");
    const coverInput = document.getElementById("cover");
    const coverPreview = document.getElementById("cover-preview");

    // ✅ Client-Side Validation
    form.addEventListener("submit", function (e) {
        let valid = true;

        if (!titleInput.value.trim()) {
            titleError.style.display = "block";
            titleInput.classList.add("error");
            valid = false;
        } else {
            titleError.style.display = "none";
            titleInput.classList.remove("error");
        }

        if (!authorInput.value.trim()) {
            authorError.style.display = "block";
            authorInput.classList.add("error");
            valid = false;
        } else {
            authorError.style.display = "none";
            authorInput.classList.remove("error");
        }

        if (!quantityInput.value || quantityInput.value < 1) {
            quantityError.style.display = "block";
            quantityInput.classList.add("error");
            valid = false;
        } else {
            quantityError.style.display = "none";
            quantityInput.classList.remove("error");
        }

        if (!valid) e.preventDefault();
    });

    // 📊 Real-Time Quantity Feedback
    quantityInput.addEventListener("input", () => {
        const quantity = quantityInput.value;
        if (quantity >= 1) {
            quantityFeedback.textContent = `📚 ${quantity} ${quantity > 1 ? 'copies' : 'copy'} will be added.`;
            quantityFeedback.style.color = "var(--primary-color)";
        } else {
            quantityFeedback.textContent = "";
        }
    });

    // 🖼️ Drag-and-Drop Cover Upload
    dropZone.addEventListener("click", () => coverInput.click());

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith("image/")) {
            coverInput.files = e.dataTransfer.files;
            showPreview(file);
        }
    });

    coverInput.addEventListener("change", () => {
        if (coverInput.files[0]) {
            showPreview(coverInput.files[0]);
        }
    });

    function showPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            coverPreview.src = e.target.result;
            coverPreview.style.display = "block";
            
            // Change the drop zone appearance
            const uploadIcon = dropZone.querySelector('.fa-cloud-upload-alt');
            const uploadText = dropZone.querySelector('p');
            
            if (uploadIcon) uploadIcon.style.display = 'none';
            if (uploadText) uploadText.textContent = 'Click to change image';
        };
        reader.readAsDataURL(file);
    }
});