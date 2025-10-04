document.addEventListener('click', (e) => {
    if (e.target && e.target.id === 'passwordToggle') {
        const input = document.getElementById('password');
        if (input) {
            input.type = input.type === 'password' ? 'text' : 'password';
        }
    }
});

// Form validation and interaction handlers
class AuthHandler {
    constructor() {
        this.initializeEventListeners();
        this.initializeAnimations();
    }

    initializeEventListeners() {
        // Password toggle functionality
        const passwordToggles = document.querySelectorAll('.password-toggle');
        passwordToggles.forEach(toggle => {
            toggle.addEventListener('click', this.togglePasswordVisibility.bind(this));
        });

        // Forms: only do validation hints; let Flask handle submission/redirects
        const loginForm = document.getElementById('loginForm');
        const signupForm = document.getElementById('signupForm');

        if (loginForm) {
            this.setupLoginValidation();
        }

        if (signupForm) {
            this.setupSignupValidation();
        }

        // Real-time validation
        this.setupRealTimeValidation();
    }

    initializeAnimations() {
        // Animate form elements on load
        const formGroups = document.querySelectorAll('.form-group');
        formGroups.forEach((group, index) => {
            group.style.opacity = '0';
            group.style.transform = 'translateY(20px)';
            group.style.transition = 'all 0.6s ease';
            
            setTimeout(() => {
                group.style.opacity = '1';
                group.style.transform = 'translateY(0)';
            }, 100 * (index + 1));
        });

        // Animate visual card
        const visualCard = document.querySelector('.visual-card');
        if (visualCard) {
            visualCard.style.opacity = '0';
            visualCard.style.transform = 'translateY(30px) scale(0.95)';
            visualCard.style.transition = 'all 0.8s ease';
            
            setTimeout(() => {
                visualCard.style.opacity = '1';
                visualCard.style.transform = 'translateY(0) scale(1)';
            }, 300);
        }
    }

    togglePasswordVisibility(event) {
        const toggle = event.currentTarget;
        const passwordInput = toggle.parentElement.querySelector('input');
        const eyeIcon = toggle.querySelector('.eye-icon');

        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            eyeIcon.textContent = '🙈';
        } else {
            passwordInput.type = 'password';
            eyeIcon.textContent = '👁️';
        }
    }

    setupLoginValidation() {
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');

        if (emailInput) {
            emailInput.addEventListener('blur', () => this.validateEmail(emailInput));
            emailInput.addEventListener('input', () => this.clearError('emailError'));
        }

        if (passwordInput) {
            passwordInput.addEventListener('blur', () => this.validatePassword(passwordInput, 'login'));
            passwordInput.addEventListener('input', () => this.clearError('passwordError'));
        }
    }

    setupSignupValidation() {
        const firstNameInput = document.getElementById('firstName');
        const lastNameInput = document.getElementById('lastName');
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirmPassword');
        const termsCheckbox = document.getElementById('terms');

        if (firstNameInput) {
            firstNameInput.addEventListener('blur', () => this.validateName(firstNameInput, 'firstNameError'));
            firstNameInput.addEventListener('input', () => this.clearError('firstNameError'));
        }

        if (lastNameInput) {
            lastNameInput.addEventListener('blur', () => this.validateName(lastNameInput, 'lastNameError'));
            lastNameInput.addEventListener('input', () => this.clearError('lastNameError'));
        }

        if (emailInput) {
            emailInput.addEventListener('blur', () => this.validateEmail(emailInput));
            emailInput.addEventListener('input', () => this.clearError('emailError'));
        }

        if (passwordInput) {
            passwordInput.addEventListener('input', () => {
                this.updatePasswordStrength(passwordInput);
                this.clearError('passwordError');
            });
            passwordInput.addEventListener('blur', () => this.validatePassword(passwordInput, 'signup'));
        }

        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('blur', () => this.validatePasswordConfirmation());
            confirmPasswordInput.addEventListener('input', () => this.clearError('confirmPasswordError'));
        }

        if (termsCheckbox) {
            termsCheckbox.addEventListener('change', () => this.clearError('termsError'));
        }
    }

    setupRealTimeValidation() {
        // Add input focus effects
        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('focus', (e) => {
                e.target.parentElement.classList.add('focused');
            });

            input.addEventListener('blur', (e) => {
                e.target.parentElement.classList.remove('focused');
            });
        });
    }

    validateName(input, errorId) {
        const value = input.value.trim();
        if (value.length < 2) {
            this.showError(errorId, 'Name must be at least 2 characters long');
            input.classList.add('error');
            return false;
        }
        input.classList.remove('error');
        return true;
    }

    validateEmail(input) {
        const email = input.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!email) {
            this.showError('emailError', 'Email is required');
            input.classList.add('error');
            return false;
        }
        
        if (!emailRegex.test(email)) {
            this.showError('emailError', 'Please enter a valid email address');
            input.classList.add('error');
            return false;
        }
        
        input.classList.remove('error');
        return true;
    }

    validatePassword(input, type) {
        const password = input.value;
        const minLength = type === 'signup' ? 8 : 1;
        
        if (password.length < minLength) {
            const message = type === 'signup' 
                ? 'Password must be at least 8 characters long'
                : 'Password is required';
            this.showError('passwordError', message);
            input.classList.add('error');
            return false;
        }
        
        if (type === 'signup') {
            const hasUpperCase = /[A-Z]/.test(password);
            const hasLowerCase = /[a-z]/.test(password);
            const hasNumbers = /\d/.test(password);
            const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
            
            if (!hasUpperCase || !hasLowerCase || !hasNumbers) {
                this.showError('passwordError', 'Password must contain uppercase, lowercase, and numbers');
                input.classList.add('error');
                return false;
            }
        }
        
        input.classList.remove('error');
        return true;
    }

    validatePasswordConfirmation() {
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        if (password !== confirmPassword) {
            this.showError('confirmPasswordError', 'Passwords do not match');
            document.getElementById('confirmPassword').classList.add('error');
            return false;
        }
        
        document.getElementById('confirmPassword').classList.remove('error');
        return true;
    }

    updatePasswordStrength(input) {
        const password = input.value;
        const strengthFill = document.querySelector('.strength-fill');
        const strengthText = document.querySelector('.strength-text');
        
        if (!strengthFill || !strengthText) return;

        let strength = 0;
        let strengthLabel = 'Weak';
        
        if (password.length >= 8) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/\d/.test(password)) strength++;
        if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;
        
        strengthFill.className = 'strength-fill';
        
        if (strength === 0) {
            strengthLabel = 'Too weak';
        } else if (strength <= 2) {
            strengthFill.classList.add('weak');
            strengthLabel = 'Weak';
        } else if (strength === 3) {
            strengthFill.classList.add('fair');
            strengthLabel = 'Fair';
        } else if (strength === 4) {
            strengthFill.classList.add('good');
            strengthLabel = 'Good';
        } else {
            strengthFill.classList.add('strong');
            strengthLabel = 'Strong';
        }
        
        strengthText.textContent = `Password strength: ${strengthLabel}`;
    }

    showError(errorId, message) {
        const errorElement = document.getElementById(errorId);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add('show');
        }
    }

    clearError(errorId) {
        const errorElement = document.getElementById(errorId);
        if (errorElement) {
            errorElement.classList.remove('show');
        }
    }

    async handleLogin(event) {}

    async handleSignup(event) {}

    simulateApiCall() {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                // Simulate random success/failure for demo
                Math.random() > 0.1 ? resolve() : reject(new Error('API Error'));
            }, 2000);
        });
    }

    showSuccessMessage(message) {
        // Create and show success notification
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #30D158;
            color: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(48, 209, 88, 0.3);
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Google Sign-In simulation
document.addEventListener('DOMContentLoaded', () => {
    new AuthHandler();
    
    // Handle Google sign-in buttons
    const googleBtns = document.querySelectorAll('.google-btn');
    googleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            btn.style.transform = 'scale(0.98)';
            setTimeout(() => {
                btn.style.transform = 'scale(1)';
                alert('Google Sign-In would be implemented here with actual OAuth integration');
            }, 150);
        });
    });
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.auth-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('div');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.className = 'ripple-effect';
            ripple.style.cssText += `
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
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
    
    .form-group.focused input {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 122, 255, 0.15);
    }
`;
document.head.appendChild(style);