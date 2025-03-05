document.addEventListener("DOMContentLoaded", () => {
  // Form validation for login form
  const loginForm = document.getElementById("login-form")
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      const username = document.getElementById("username").value.trim()
      const password = document.getElementById("password").value.trim()
      let isValid = true

      if (!username) {
        showError("username", "Username is required")
        isValid = false
      } else {
        clearError("username")
      }

      if (!password) {
        showError("password", "Password is required")
        isValid = false
      } else {
        clearError("password")
      }

      if (!isValid) {
        e.preventDefault()
      }
    })
  }

  // Form validation for registration form
  const registerForm = document.getElementById("register-form")
  if (registerForm) {
    registerForm.addEventListener("submit", (e) => {
      const username = document.getElementById("username").value.trim()
      const email = document.getElementById("email").value.trim()
      const password = document.getElementById("password").value.trim()
      const confirmPassword = document.getElementById("confirm_password").value.trim()
      let isValid = true

      if (!username) {
        showError("username", "Username is required")
        isValid = false
      } else if (username.length < 3) {
        showError("username", "Username must be at least 3 characters")
        isValid = false
      } else {
        clearError("username")
      }

      if (!email) {
        showError("email", "Email is required")
        isValid = false
      } else if (!isValidEmail(email)) {
        showError("email", "Please enter a valid email address")
        isValid = false
      } else {
        clearError("email")
      }

      if (!password) {
        showError("password", "Password is required")
        isValid = false
      } else if (password.length < 6) {
        showError("password", "Password must be at least 6 characters")
        isValid = false
      } else {
        clearError("password")
      }

      if (password !== confirmPassword) {
        showError("confirm_password", "Passwords do not match")
        isValid = false
      } else {
        clearError("confirm_password")
      }

      if (!isValid) {
        e.preventDefault()
      }
    })
  }

  // Helper functions
  function showError(fieldId, message) {
    const field = document.getElementById(fieldId)
    const errorElement = field.nextElementSibling?.classList.contains("error-message")
      ? field.nextElementSibling
      : document.createElement("div")

    if (!errorElement.classList.contains("error-message")) {
      errorElement.classList.add("error-message")
      errorElement.style.color = "#ef4444"
      errorElement.style.fontSize = "0.875rem"
      errorElement.style.marginTop = "0.5rem"
      field.parentNode.insertBefore(errorElement, field.nextSibling)
    }

    errorElement.textContent = message
    field.style.borderColor = "#ef4444"
  }

  function clearError(fieldId) {
    const field = document.getElementById(fieldId)
    const errorElement = field.nextElementSibling

    if (errorElement && errorElement.classList.contains("error-message")) {
      errorElement.textContent = ""
    }

    field.style.borderColor = ""
  }

  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }
})

document.addEventListener('DOMContentLoaded', function() {
  const stars = document.querySelectorAll('.star-rating label');
  
  stars.forEach(star => {
      star.addEventListener('mouseover', function() {
          // Add hover class to current and previous stars
          let currentStar = this;
          while(currentStar) {
              currentStar.classList.add('hover');
              currentStar = currentStar.previousElementSibling?.previousElementSibling;
          }
      });
      
      star.addEventListener('mouseout', function() {
          // Remove hover class from all stars
          document.querySelectorAll('.star-rating label').forEach(s => {
              s.classList.remove('hover');
          });
      });
  });
  
  // Form validation feedback
  const form = document.getElementById('feedback-form');
  if (form) {
      form.addEventListener('submit', function(event) {
          const rating = form.querySelector('input[name="rating"]:checked');
          const message = form.querySelector('#message');
          
          if (!rating && form.querySelector('input[name="rating"][required]')) {
              event.preventDefault();
              alert('Please select a rating before submitting.');
          }
          
          if (message.required && message.value.trim() === '') {
              event.preventDefault();
              message.classList.add('error');
              alert('Please provide feedback before submitting.');
          }
      });
  }
});

const stars = document.querySelectorAll('.star-input');
stars.forEach(star => {
    star.addEventListener('change', () => {
        const ratingValue = star.value;
        stars.forEach(s => {
            const label = document.querySelector(`label[for="${s.id}"]`);
            label.style.color = s.value <= ratingValue ? '#ffc107' : '#ccc'; // Change color based on selection
        });
    });
});