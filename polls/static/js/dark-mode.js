// Dark mode toggle functionality
class DarkModeToggle {
    constructor() {
        this.init();
    }

    init() {
        // Check for saved theme preference or default to light mode
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        
        // Create dark mode toggle if it doesn't exist
        this.createToggle();
        
        // Add event listeners
        this.addEventListeners();
    }

    createToggle() {
        // Check if toggle already exists
        if (document.querySelector('.dark-mode-toggle-container')) {
            return;
        }

        // Find the header or create one
        let header = document.querySelector('.main-header');
        if (!header) {
            header = document.querySelector('header');
        }
        
        if (!header) {
            // Create a header if none exists
            header = document.createElement('div');
            header.className = 'goaltweaks-header';
            document.body.insertBefore(header, document.body.firstChild);
        }

        // Create the toggle container
        const toggleContainer = document.createElement('div');
        toggleContainer.className = 'dark-mode-toggle-container';
        
        // Create the label
        const label = document.createElement('span');
        label.className = 'dark-mode-label';
        label.textContent = 'Dark Mode';
        
        // Create the toggle button
        const toggle = document.createElement('button');
        toggle.className = 'dark-mode-toggle';
        toggle.setAttribute('aria-label', 'Toggle dark mode');
        toggle.type = 'button';
        
        // Assemble the toggle
        toggleContainer.appendChild(label);
        toggleContainer.appendChild(toggle);
        
        // Find the right place to insert the toggle
        const authButtons = header.querySelector('.auth-buttons');
        if (authButtons) {
            authButtons.appendChild(toggleContainer);
        } else {
            // Create a header right section if it doesn't exist
            let headerRight = header.querySelector('.header-right');
            if (!headerRight) {
                headerRight = document.createElement('div');
                headerRight.className = 'header-right';
                header.appendChild(headerRight);
            }
            headerRight.appendChild(toggleContainer);
        }
    }

    addEventListeners() {
        const toggle = document.querySelector('.dark-mode-toggle');
        if (toggle) {
            toggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

        // Listen for system theme changes
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addListener((e) => {
                if (!localStorage.getItem('theme')) {
                    this.setTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update the toggle state
        const toggle = document.querySelector('.dark-mode-toggle');
        if (toggle) {
            toggle.setAttribute('aria-pressed', theme === 'dark');
        }
        
        // Update meta theme color for mobile browsers
        this.updateMetaThemeColor(theme);
        
        // Dispatch custom event for other components to listen to
        window.dispatchEvent(new CustomEvent('themeChange', { detail: { theme } }));
    }

    updateMetaThemeColor(theme) {
        let metaTheme = document.querySelector('meta[name="theme-color"]');
        if (!metaTheme) {
            metaTheme = document.createElement('meta');
            metaTheme.name = 'theme-color';
            document.head.appendChild(metaTheme);
        }
        
        // Set theme color based on current theme
        metaTheme.content = theme === 'dark' ? '#1a202c' : '#ffffff';
    }

    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    }
}

// Initialize dark mode toggle when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DarkModeToggle();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DarkModeToggle;
}
