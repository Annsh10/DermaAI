// Navigation scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Mobile menu toggle
const mobileToggle = document.getElementById('mobile-toggle');
const navMenu = document.querySelector('.nav-menu');

mobileToggle?.addEventListener('click', () => {
    navMenu.classList.toggle('active');
    mobileToggle.classList.toggle('active');
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards for animation
document.querySelectorAll('.feature-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = 'all 0.6s ease';
    observer.observe(card);
});

// Add click handlers for CTA buttons
document.querySelectorAll('.cta-btn, .auth-btn').forEach(button => {
    button.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Add ripple effect
        const ripple = document.createElement('div');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(255, 255, 255, 0.3)';
        ripple.style.transform = 'scale(0)';
        ripple.style.animation = 'ripple 0.6s linear';
        ripple.style.pointerEvents = 'none';
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
        
        // Handle button actions
        if (button.textContent.includes('Watch Demo')) {
            console.log('Opening demo...');
            // Add your demo logic here
        }
    });
});

// Add CSS for ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .nav-menu.active {
        display: flex;
        position: absolute;
        top: 100%;
        left: 0;
        width: 100%;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        flex-direction: column;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    }
    
    .nav-menu.active .nav-list {
        flex-direction: column;
        gap: 16px;
    }
    
    .mobile-menu-toggle.active span:nth-child(1) {
        transform: rotate(45deg) translate(5px, 5px);
    }
    
    .mobile-menu-toggle.active span:nth-child(2) {
        opacity: 0;
    }
    
    .mobile-menu-toggle.active span:nth-child(3) {
        transform: rotate(-45deg) translate(7px, -6px);
    }
`;
document.head.appendChild(style);

// Parallax effect for hero section
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroCard = document.querySelector('.hero-card');
    const parallax = scrolled * 0.1;
    
    if (heroCard) {
        heroCard.style.transform = `rotate(-2deg) translateY(${parallax}px)`;
    }
});

// Add loading animation
window.addEventListener('load', () => {
    const heroTitle = document.querySelector('.hero-title');
    const heroDescription = document.querySelector('.hero-description');
    const heroActions = document.querySelector('.hero-actions');
    const heroCard = document.querySelector('.hero-card');
    
    // Animate hero elements
    [heroTitle, heroDescription, heroActions].forEach((element, index) => {
        if (element) {
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px)';
            element.style.transition = 'all 0.8s ease';
            
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 100 * (index + 1));
        }
    });
    
    // Animate hero card
    if (heroCard) {
        heroCard.style.opacity = '0';
        heroCard.style.transform = 'rotate(-2deg) translateY(50px) scale(0.9)';
        heroCard.style.transition = 'all 1s ease';
        
        setTimeout(() => {
            heroCard.style.opacity = '1';
            heroCard.style.transform = 'rotate(-2deg) translateY(0) scale(1)';
        }, 400);
    }
});

// Add hover sound effect simulation
document.querySelectorAll('button, .nav-link, .feature-card').forEach(element => {
    element.addEventListener('mouseenter', () => {
        // Subtle scale animation on hover
        if (element.classList.contains('feature-card')) {
            element.style.transform = 'translateY(-8px) scale(1.02)';
        }
    });
    
    element.addEventListener('mouseleave', () => {
        if (element.classList.contains('feature-card')) {
            element.style.transform = 'translateY(0) scale(1)';
        }
    });
});

// Preload critical images and fonts
const preloadResources = () => {
    // Preload fonts
    const fontLink = document.createElement('link');
    fontLink.rel = 'preload';
    fontLink.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap';
    fontLink.as = 'style';
    document.head.appendChild(fontLink);
};

preloadResources();