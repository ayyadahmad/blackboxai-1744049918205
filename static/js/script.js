// Toast Notification System
class ToastNotification {
    constructor() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(this.container);
    }

    show(message, type = 'info') {
        const toast = document.createElement('div');
        const id = `toast-${Date.now()}`;
        toast.id = id;
        toast.className = `toast fade-in align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        this.container.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => toast.remove());
    }
}

// Initialize toast notification system
const toast = new ToastNotification();

// Form Validation
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
            
            let feedback = field.nextElementSibling;
            if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                field.parentNode.appendChild(feedback);
            }
            feedback.textContent = 'This field is required';
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// File Upload Preview
function handleFileUpload(input, previewContainer) {
    const file = input.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.createElement('div');
        preview.className = 'file-preview';

        if (file.type.startsWith('image/')) {
            preview.innerHTML = `
                <img src="${e.target.result}" class="img-fluid rounded" alt="Preview">
                <button type="button" class="btn btn-sm btn-danger remove-file">
                    <i class="fas fa-times"></i>
                </button>
            `;
        } else if (file.type.startsWith('video/')) {
            preview.innerHTML = `
                <video src="${e.target.result}" class="img-fluid rounded" controls></video>
                <button type="button" class="btn btn-sm btn-danger remove-file">
                    <i class="fas fa-times"></i>
                </button>
            `;
        }

        previewContainer.innerHTML = '';
        previewContainer.appendChild(preview);

        preview.querySelector('.remove-file').addEventListener('click', () => {
            input.value = '';
            previewContainer.innerHTML = '';
        });
    };

    reader.readAsDataURL(file);
}

// Initialize components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));

    // Initialize file upload previews
    document.querySelectorAll('.file-upload').forEach(input => {
        const previewContainer = document.querySelector(input.dataset.preview);
        if (previewContainer) {
            input.addEventListener('change', () => handleFileUpload(input, previewContainer));
        }
    });

    // Form validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                toast.show('Please fill in all required fields', 'warning');
            }
        });
    });

    // Character counter for textareas
    document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
        const counter = document.createElement('div');
        counter.className = 'text-muted small mt-1';
        textarea.parentNode.appendChild(counter);

        function updateCounter() {
            const remaining = parseInt(textarea.getAttribute('maxlength')) - textarea.value.length;
            counter.textContent = `${remaining} characters remaining`;
        }

        textarea.addEventListener('input', updateCounter);
        updateCounter();
    });
});