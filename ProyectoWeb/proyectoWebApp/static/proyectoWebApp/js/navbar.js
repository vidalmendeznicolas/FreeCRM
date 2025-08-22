// Navbar functionality for hamburger menu
document.addEventListener('DOMContentLoaded', function() {
    
    // Get navbar elements
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    console.log('Navbar elements found:', {
        toggler: navbarToggler,
        collapse: navbarCollapse,
        links: navLinks.length
    });
    
    // Manual hamburger menu implementation (Bootstrap fallback)
    if (navbarToggler && navbarCollapse) {
        console.log('Setting up manual hamburger menu...');
        
        // Remove Bootstrap attributes to prevent conflicts
        navbarToggler.removeAttribute('data-bs-toggle');
        navbarToggler.removeAttribute('data-bs-target');
        
        // Add manual click event
        navbarToggler.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Manual hamburger button clicked!');
            
            // Toggle menu visibility
            const isExpanded = navbarCollapse.classList.contains('show');
            
            if (isExpanded) {
                // Close menu
                navbarCollapse.classList.remove('show');
                navbarToggler.setAttribute('aria-expanded', 'false');
                console.log('Menu closed');
            } else {
                // Open menu
                navbarCollapse.classList.add('show');
                navbarToggler.setAttribute('aria-expanded', 'true');
                console.log('Menu opened');
            }
            
            // Add visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    }
    
    // Close mobile menu when clicking on a link
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Check if we're on mobile and menu is open
            if (window.innerWidth <= 991.98 && navbarCollapse.classList.contains('show')) {
                // Close the menu manually
                navbarCollapse.classList.remove('show');
                navbarToggler.setAttribute('aria-expanded', 'false');
                console.log('Menu closed by link click');
            }
        });
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        const isClickInsideNavbar = event.target.closest('#mainNav');
        const isClickOnToggler = event.target.closest('.navbar-toggler');
        
        if (!isClickInsideNavbar && !isClickOnToggler && navbarCollapse.classList.contains('show')) {
            // Close the menu manually
            navbarCollapse.classList.remove('show');
            navbarToggler.setAttribute('aria-expanded', 'false');
            console.log('Menu closed by outside click');
        }
    });
    
    // Add active state to current page link
    const currentPath = window.location.pathname;
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath === currentPath || 
            (currentPath === '/' && linkPath === '/') ||
            (currentPath.startsWith('/blog/') && linkPath === '/blog/')) {
            link.classList.add('active');
            link.closest('.nav-item').classList.add('active');
        }
    });
    
    // Add loading animation to navbar
    const navbar = document.getElementById('mainNav');
    if (navbar) {
        setTimeout(() => {
            navbar.style.opacity = '1';
            navbar.style.transform = 'translateY(0)';
        }, 100);
    }
    
    // Add resize listener to handle responsive behavior
    window.addEventListener('resize', function() {
        if (window.innerWidth > 991.98 && navbarCollapse.classList.contains('show')) {
            // Auto-close menu when switching to desktop
            navbarCollapse.classList.remove('show');
            navbarToggler.setAttribute('aria-expanded', 'false');
            console.log('Menu closed by resize');
        }
    });
});

// Add CSS for navbar animations
const style = document.createElement('style');
style.textContent = `
    #mainNav {
        opacity: 0;
        transform: translateY(-20px);
        transition: all 0.3s ease;
    }
    
    .navbar-toggler-icon {
        transition: transform 0.3s ease;
    }
    
    /* Ensure mobile menu works properly */
    @media (max-width: 991.98px) {
        .navbar-toggler {
            display: block !important;
        }
        
        .navbar-collapse {
            display: none;
        }
        
        .navbar-collapse.show {
            display: block !important;
        }
    }
`;
document.head.appendChild(style); 