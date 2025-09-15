
class SidebarManager {
    constructor() {
        this.sidebar = null;
        this.toggleButton = null;
        this.overlay = null;
        this.isVisible = false;
        this.isMobile = window.innerWidth <= 768;
        
        this.init();
    }

    /**
     * Initialize the sidebar manager
     */
    init() {
        this.sidebar = document.getElementById('sidebar');
        this.toggleButton = document.getElementById('toggleSidebar');
        
        if (!this.sidebar || !this.toggleButton) {
            console.warn('Sidebar elements not found');
            return;
        }

        this.createOverlay();
        this.setupToggleButton();
        this.loadSidebarState();
        this.addEventListeners();
        this.handleResize();
        
        console.log('Sidebar initialized');
    }

    /**
     * Create mobile overlay for better UX
     */
    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'sidebar-overlay';
        this.overlay.setAttribute('aria-hidden', 'true');
        document.body.appendChild(this.overlay);
    }


    setupToggleButton() {
        this.toggleButton.innerHTML = `
            <svg class="sidebar-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="9" y1="9" x2="15" y2="9"></line>
                <line x1="9" y1="12" x2="15" y2="12"></line>
                <line x1="9" y1="15" x2="15" y2="15"></line>
            </svg>
        `;
        
        this.toggleButton.setAttribute('aria-label', 'Toggle navigation sidebar');
        this.toggleButton.setAttribute('title', 'Toggle Sidebar');
    }

    /**
     * Load sidebar state from localStorage with intelligent defaults
     */
    loadSidebarState() {
        const savedState = localStorage.getItem('sidebarVisible');
        
        // Smart defaults: visible on desktop, hidden on mobile
        if (savedState === null) {
            this.isVisible = !this.isMobile;
        } else {
            this.isVisible = savedState === 'true';
        }
        
        this.updateSidebarState(false); // Don't animate on initial load
    }

    toggleSidebar() {
        this.isVisible = !this.isVisible;
        this.updateSidebarState(true);
        this.saveSidebarState();
        
        // Track usage analytics (optional)
        this.trackSidebarUsage();
    }


    updateSidebarState(animate = true) {
        const { sidebar, toggleButton, overlay } = this;
        
        if (!animate) {
            sidebar.style.transition = 'none';
            setTimeout(() => {
                sidebar.style.transition = '';
            }, 50);
        }

        if (this.isVisible) {
            sidebar.classList.add('visible');
            sidebar.classList.remove('hidden');
            sidebar.setAttribute('aria-hidden', 'false');
            
            if (this.isMobile) {
                overlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
            
            this.updateToggleIcon('close');
        } else {
            sidebar.classList.remove('visible');
            sidebar.classList.add('hidden');
            sidebar.setAttribute('aria-hidden', 'true');
            
            overlay.classList.remove('active');
            document.body.style.overflow = '';
            
            this.updateToggleIcon('open');
        }

        // Update toggle button state
        toggleButton.setAttribute('aria-expanded', this.isVisible);
        toggleButton.classList.toggle('active', this.isVisible);
    }

    /**
     * Update toggle icon based on state
     */
    updateToggleIcon(state) {
        const icon = this.toggleButton.querySelector('.sidebar-icon');
        
        if (state === 'close') {
            icon.innerHTML = `
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            `;
            icon.setAttribute('aria-label', 'Close sidebar');
        } else {
            icon.innerHTML = `
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="9" y1="9" x2="15" y2="9"></line>
                <line x1="9" y1="12" x2="15" y2="12"></line>
                <line x1="9" y1="15" x2="15" y2="15"></line>
            `;
            icon.setAttribute('aria-label', 'Open sidebar');
        }
    }

    /**
     * Save sidebar state to localStorage
     */
    saveSidebarState() {
        localStorage.setItem('sidebarVisible', this.isVisible.toString());
    }

    /**
     * Handle window resize events
     */
    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;
        
        // If switching between mobile/desktop, update defaults
        if (wasMobile !== this.isMobile) {
            if (this.isMobile && this.isVisible) {
                // On mobile, ensure overlay is handled properly
                this.updateSidebarState(false);
            } else if (!this.isMobile) {
                // On desktop, remove overlay effects
                document.body.style.overflow = '';
                this.overlay.classList.remove('active');
            }
        }
    }

    /**
     * Add all event listeners
     */
    addEventListeners() {
        // Toggle button click
        this.toggleButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleSidebar();
        });

        // Overlay click (mobile)
        this.overlay.addEventListener('click', () => {
            if (this.isMobile && this.isVisible) {
                this.toggleSidebar();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + B to toggle sidebar
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                this.toggleSidebar();
            }
            
            // Escape to close sidebar on mobile
            if (e.key === 'Escape' && this.isMobile && this.isVisible) {
                this.toggleSidebar();
            }
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });

        // Theme change listener
        window.addEventListener('themeChange', (e) => {
            this.handleThemeChange(e.detail.theme);
        });
    }

    /**
     * Handle theme changes for better integration
     */
    handleThemeChange(theme) {
        console.log(`🎨 Sidebar adapting to ${theme} theme`);
        // Additional theme-specific adjustments can be added here
    }

    /**
     * Track sidebar usage for analytics (optional)
     */
    trackSidebarUsage() {
        const event = {
            action: 'sidebar_toggle',
            state: this.isVisible ? 'opened' : 'closed',
            device: this.isMobile ? 'mobile' : 'desktop',
            timestamp: new Date().toISOString()
        };
        
        console.log('📊 Sidebar usage:', event);
        // You can send this to your analytics service
    }

    /**
     * Public method to programmatically show sidebar
     */
    show() {
        if (!this.isVisible) {
            this.toggleSidebar();
        }
    }

    /**
     * Public method to programmatically hide sidebar
     */
    hide() {
        if (this.isVisible) {
            this.toggleSidebar();
        }
    }

    /**
     * Get current sidebar state
     */
    getState() {
        return {
            visible: this.isVisible,
            mobile: this.isMobile,
            element: this.sidebar
        };
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.sidebarManager = new SidebarManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SidebarManager;
}