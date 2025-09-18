class FormValidator {
    constructor() {
        this.mode = this.detectMode();
        this.init();
    }

    detectMode() {
        // Check if subject name field is read-only (indicates new_prediction mode)
        const subjectNameInput = document.querySelector('input[name="0-subject_name"]');
        if (subjectNameInput && subjectNameInput.readOnly) {
            return 'new_prediction';
        }
        
        // Check wizard title
        const wizardTitle = document.querySelector('.wizard-title');
        if (wizardTitle && wizardTitle.textContent.includes('New Prediction')) {
            return 'new_prediction';
        }
        
        return 'not_editing';
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            console.log('FormValidator initialized in mode:', this.mode);
            this.setupValidation();
        });
    }

    setupValidation() {
        const subjectNameInput = document.querySelector('input[name="0-subject_name"]');
        const previousScoresInput = document.querySelector('input[name="0-previous_scores"]');

        if (subjectNameInput) {
            subjectNameInput.addEventListener('blur', (e) => this.validateSubjectName(e.target));
            subjectNameInput.addEventListener('input', (e) => this.clearValidationState(e.target));
        }

        if (previousScoresInput) {
            previousScoresInput.addEventListener('blur', (e) => this.validatePreviousScores(e.target));
            previousScoresInput.addEventListener('input', (e) => this.clearValidationState(e.target));
        }

        // REMOVE the form submission handler - let Django handle it
        // const form = document.querySelector('form');
        // if (form) {
        //     form.addEventListener('submit', (e) => this.handleFormSubmission(e));
        // }
    }

    validateSubjectName(input) {
        const value = input.value.trim();
        
        // Clear previous errors
        this.clearFieldErrors(input);

        if (!value) {
            this.showFieldError(input, 'Subject name is required.');
            return false;
        }

        // Skip duplicate validation in new_prediction mode
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

        this.showFieldSuccess(input);
        return true;
    }

    // ... keep the rest of your methods but REMOVE handleFormSubmission ...
}

// Initialize the form validator
new FormValidator();
