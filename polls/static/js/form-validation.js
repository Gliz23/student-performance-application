class FormValidator {
    constructor() {
        this.init();
    }

    init() {
        // Add event listeners for real-time validation
        document.addEventListener('DOMContentLoaded', () => {
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

        // Form submission handler
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmission(e));
        }
    }

    validateSubjectName(input) {
        const value = input.value.trim();
        
        // Clear previous errors
        this.clearFieldErrors(input);

        if (!value) {
            this.showFieldError(input, 'Subject name is required.');
            return false;
        }

        if (value.length < 2) {
            this.showFieldError(input, 'Subject name must be at least 2 characters long.');
            return false;
        }

        if (value.length > 100) {
            this.showFieldError(input, 'Subject name cannot exceed 100 characters.');
            return false;
        }

        // Check for existing subjects (client-side check using data attributes if available)
        const existingSubjects = this.getExistingSubjects();
        if (existingSubjects.includes(value.toLowerCase())) {
            this.showFieldError(input, `You already have a subject named '${value}'. Please choose a different name.`);
            return false;
        }

        // Show success state
        this.showFieldSuccess(input);
        return true;
    }

    getExistingSubjects() {
        // This could be populated from Django context or AJAX call
        // For now, we'll rely on server-side validation as the primary check
        const existingSubjectsElement = document.querySelector('#existing-subjects-data');
        if (existingSubjectsElement) {
            try {
                return JSON.parse(existingSubjectsElement.textContent).map(s => s.toLowerCase());
            } catch (e) {
                console.warn('Could not parse existing subjects data');
            }
        }
        return [];
    }

    validatePreviousScores(input) {
        const value = parseFloat(input.value);
        
        // Clear previous errors
        this.clearFieldErrors(input);

        if (isNaN(value)) {
            this.showFieldError(input, 'Please enter a valid number.');
            return false;
        }

        if (value < 0 || value > 100) {
            this.showFieldError(input, 'Previous scores must be between 0 and 100.');
            return false;
        }

        // Show success state
        this.showFieldSuccess(input);
        return true;
    }

    showFieldError(input, message) {
        input.classList.add('error');
        input.classList.remove('success');
        
        const errorContainer = this.getOrCreateErrorContainer(input);
        errorContainer.innerHTML = `<li>${message}</li>`;
        errorContainer.style.display = 'block';
    }

    showFieldSuccess(input) {
        input.classList.add('success');
        input.classList.remove('error');
        this.clearFieldErrors(input);
    }

    clearFieldErrors(input) {
        const errorContainer = this.getOrCreateErrorContainer(input);
        errorContainer.style.display = 'none';
        errorContainer.innerHTML = '';
    }

    clearValidationState(input) {
        input.classList.remove('error', 'success');
        this.clearFieldErrors(input);
    }

    getOrCreateErrorContainer(input) {
        const fieldContainer = input.closest('.form-field');
        let errorContainer = fieldContainer.querySelector('.errorlist');
        
        if (!errorContainer) {
            errorContainer = document.createElement('ul');
            errorContainer.className = 'errorlist';
            errorContainer.style.display = 'none';
            input.parentNode.insertBefore(errorContainer, input.nextSibling);
        }
        
        return errorContainer;
    }

    handleFormSubmission(event) {
        const currentStep = this.getCurrentStep();
        
        if (currentStep === 0) {
            // Validate Step 1 fields before allowing progression
            const subjectNameInput = document.querySelector('input[name="0-subject_name"]');
            const previousScoresInput = document.querySelector('input[name="0-previous_scores"]');
            
            let isValid = true;
            let errorMessages = [];
            
            if (subjectNameInput && !this.validateSubjectName(subjectNameInput)) {
                isValid = false;
                errorMessages.push('Please fix the subject name error.');
            }
            
            if (previousScoresInput && !this.validatePreviousScores(previousScoresInput)) {
                isValid = false;
                errorMessages.push('Please fix the previous scores error.');
            }
            
            // Check for any existing server-side errors
            const existingErrors = document.querySelectorAll('.errorlist li, .error-section');
            if (existingErrors.length > 0) {
                isValid = false;
                errorMessages.push('Please fix all validation errors before continuing.');
            }
            
            if (!isValid) {
                event.preventDefault();
                event.stopPropagation();
                
                const combinedMessage = errorMessages.length > 1 
                    ? 'Multiple errors found:\n• ' + errorMessages.join('\n• ')
                    : errorMessages[0] || 'Please fix the errors above before continuing.';
                    
                this.showFormError(combinedMessage);
                
                // Scroll to first error
                const firstError = document.querySelector('.error, .errorlist');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                
                return false;
            }
        }
        
        return true;
    }

    getCurrentStep() {
        const stepElement = document.querySelector('.form-step p');
        if (stepElement) {
            const stepText = stepElement.textContent;
            const match = stepText.match(/Step (\d+)/);
            return match ? parseInt(match[1]) - 1 : 0; // Convert to 0-indexed
        }
        return 0;
    }

    showFormError(message) {
        const formStep = document.querySelector('.form-step');
        let errorDiv = document.querySelector('.form-error-message');
        
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-section form-error-message';
            formStep.insertBefore(errorDiv, formStep.firstChild);
        }
        
        errorDiv.innerHTML = `<h4>Error:</h4><p>${message}</p>`;
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// Initialize the form validator
new FormValidator();
