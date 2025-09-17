class FormValidator {
    constructor() {
        this.mode = this.detectMode(); // Detect the mode
        this.init();
    }

    detectMode() {
        // Check if we're in new_prediction mode
        const wizardTitle = document.querySelector('.wizard-title');
        if (wizardTitle && wizardTitle.textContent.includes('New Prediction')) {
            return 'new_prediction';
        }
        
        // Check for hidden input or data attribute
        const modeInput = document.querySelector('input[name="mode"]');
        if (modeInput && modeInput.value === 'new_prediction') {
            return 'new_prediction';
        }
        
        // Check for data attribute on the form
        const form = document.querySelector('form');
        if (form && form.dataset.mode === 'new_prediction') {
            return 'new_prediction';
        }
        
        return 'not_editing'; // Default mode
    }

    init() {
        // Add event listeners for real-time validation
        document.addEventListener('DOMContentLoaded', () => {
            console.log('FormValidator initialized in mode:', this.mode);
            this.setupValidation();
        });
    }

    validateSubjectName(input) {
        const value = input.value.trim();
        
        // Clear previous errors
        this.clearFieldErrors(input);

        if (!value) {
            this.showFieldError(input, 'Subject name is required.');
            return false;
        }

        // In new_prediction mode, skip duplicate validation
        if (this.mode === 'new_prediction') {
            console.log('new_prediction mode - skipping duplicate validation');
            this.showFieldSuccess(input);
            return true;
        }

        if (value.length < 2) {
            this.showFieldError(input, 'Subject name must be at least 2 characters long.');
            return false;
        }

        if (value.length > 100) {
            this.showFieldError(input, 'Subject name cannot exceed 100 characters.');
            return false;
        }

        // Check for existing subjects (only in not_editing mode)
        const existingSubjects = this.getExistingSubjects();
        if (existingSubjects.includes(value.toLowerCase())) {
            this.showFieldError(input, `You already have a subject named '${value}'. Please choose a different name.`);
            return false;
        }

        // Show success state
        this.showFieldSuccess(input);
        return true;
    }

    // ... rest of your JavaScript code ...
}

// Initialize the form validator
new FormValidator();
