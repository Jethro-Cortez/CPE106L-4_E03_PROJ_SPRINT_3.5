// Theme Toggle Functionality
document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.querySelector(".theme-toggle")
  const htmlElement = document.documentElement
  const themeIcon = themeToggle.querySelector("i")

  // Check for saved theme preference or use system preference
  const savedTheme = localStorage.getItem("theme")
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches

  // Set initial theme
  if (savedTheme === "dark" || (savedTheme === null && prefersDark)) {
    htmlElement.setAttribute("data-theme", "dark")
    themeIcon.classList.remove("fa-moon")
    themeIcon.classList.add("fa-sun")
    themeToggle.setAttribute("aria-pressed", "true")
  } else {
    htmlElement.setAttribute("data-theme", "light")
    themeIcon.classList.remove("fa-sun")
    themeIcon.classList.add("fa-moon")
    themeToggle.setAttribute("aria-pressed", "false")
  }

  // Toggle theme on button click with smooth transition
  themeToggle.addEventListener("click", () => {
    const currentTheme = htmlElement.getAttribute("data-theme")
    const newTheme = currentTheme === "light" ? "dark" : "light"

    // Add transition class for smooth color changes
    htmlElement.classList.add("theme-transition")
    
    // Set the new theme
    htmlElement.setAttribute("data-theme", newTheme)
    localStorage.setItem("theme", newTheme)

    // Update icon an  newTheme)
    localStorage.setItem("theme", newTheme)

    // Update icon and aria-pressed
    if (newTheme === "dark") {
      themeIcon.classList.remove("fa-moon")
      themeIcon.classList.add("fa-sun")
      themeToggle.setAttribute("aria-pressed", "true")
    } else {
      themeIcon.classList.remove("fa-sun")
      themeIcon.classList.add("fa-moon")
      themeToggle.setAttribute("aria-pressed", "false")
    }
    
    // Remove transition class after animation completes
    setTimeout(() => {
      htmlElement.classList.remove("theme-transition")
    }, 500)
  })

  // Mobile navigation toggle with animation
  const navbarToggler = document.querySelector(".navbar-toggler")
  const navLinks = document.querySelector(".nav-links")

  if (navbarToggler) {
    navbarToggler.addEventListener("click", () => {
      navLinks.classList.toggle("active")
      const expanded = navbarToggler.getAttribute("aria-expanded") === "true" || false
      navbarToggler.setAttribute("aria-expanded", !expanded)
      
      // Add animation to nav items
      const navItems = navLinks.querySelectorAll("li")
      navItems.forEach((item, index) => {
        // Reset animation
        item.style.animation = "none"
        item.offsetHeight // Trigger reflow
        
        if (navLinks.classList.contains("active")) {
          item.style.animation = `slideDown 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) forwards ${index * 0.1}s`
        } else {
          item.style.animation = ""
        }
      })
    })
  }

  // Close flash messages with animation
  const closeButtons = document.querySelectorAll(".flash-close")
  closeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const flashMessage = this.closest(".flash")
      flashMessage.style.animation = "slideRight 0.5s cubic-bezier(0.25, 0.8, 0.25, 1) forwards"
      setTimeout(() => {
        flashMessage.style.display = "none"
      }, 500)
    })
  })

  // Auto-hide flash messages after 5 seconds with animation
  const flashMessages = document.querySelectorAll(".flash")
  flashMessages.forEach((message) => {
    setTimeout(() => {
      message.style.animation = "slideRight 0.5s cubic-bezier(0.25, 0.8, 0.25, 1) forwards"
      setTimeout(() => {
        message.style.display = "none"
      }, 500)
    }, 5000)
  })
  
  // Add animation to section cards on scroll
  const animateOnScroll = () => {
    const elements = document.querySelectorAll('.section-card, .feature-card, .testimonial-card, .book-card')
    
    elements.forEach(element => {
      const elementTop = element.getBoundingClientRect().top
      const elementVisible = 150
      
      if (elementTop < window.innerHeight - elementVisible) {
        element.classList.add('animate-fade-in')
      }
    })
  }
  
  // Run on initial load
  animateOnScroll()
  
  // Add event listener for scroll
  window.addEventListener('scroll', animateOnScroll)
})