/**
 * Mobile-specific JavaScript for Synthara AI
 * Enhances the mobile experience with responsive interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add hamburger menu functionality
    setupMobileNavigation();

    // Add touch-friendly enhancements
    enhanceTouchInteractions();

    // Improve form handling on mobile
    improveMobileFormHandling();

    // Handle orientation changes
    handleOrientationChanges();

    // Add viewport height fix for mobile browsers
    fixMobileViewportHeight();
});

/**
 * Sets up the mobile navigation menu with hamburger toggle
 */
function setupMobileNavigation() {
    // Create hamburger menu button if it doesn't exist
    if (!document.querySelector('.hamburger-menu')) {
        const header = document.querySelector('header');
        const navLinks = document.querySelector('.nav-links');

        // Create hamburger button
        const hamburgerBtn = document.createElement('button');
        hamburgerBtn.className = 'hamburger-menu';
        hamburgerBtn.setAttribute('aria-label', 'Toggle navigation menu');
        hamburgerBtn.innerHTML = `
            <div class="hamburger-icon">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;

        // Insert hamburger button before nav links
        header.insertBefore(hamburgerBtn, navLinks);

        // Add click event to toggle menu
        hamburgerBtn.addEventListener('click', function() {
            this.classList.toggle('open');
            navLinks.classList.toggle('open');

            // Update aria-expanded attribute for accessibility
            const isExpanded = navLinks.classList.contains('open');
            this.setAttribute('aria-expanded', isExpanded);

            // Prevent body scrolling when menu is open
            document.body.style.overflow = isExpanded ? 'hidden' : '';
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!event.target.closest('.nav-links') &&
                !event.target.closest('.hamburger-menu') &&
                navLinks.classList.contains('open')) {
                hamburgerBtn.classList.remove('open');
                navLinks.classList.remove('open');
                document.body.style.overflow = '';
            }
        });

        // Close menu when clicking a nav link
        const links = navLinks.querySelectorAll('a');
        links.forEach(link => {
            link.addEventListener('click', function() {
                hamburgerBtn.classList.remove('open');
                navLinks.classList.remove('open');
                document.body.style.overflow = '';
            });
        });
    }
}

/**
 * Enhances touch interactions for mobile devices
 */
function enhanceTouchInteractions() {
    // Add active state for buttons on touch
    const buttons = document.querySelectorAll('button, .nav-link, .tab-btn');
    buttons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.classList.add('touch-active');
        }, { passive: true });

        button.addEventListener('touchend', function() {
            this.classList.remove('touch-active');
        }, { passive: true });

        button.addEventListener('touchcancel', function() {
            this.classList.remove('touch-active');
        }, { passive: true });
    });

    // Improve scrolling in output areas
    const outputAreas = document.querySelectorAll('.output-content');
    outputAreas.forEach(area => {
        area.addEventListener('touchstart', function(e) {
            // Allow scrolling within output areas without triggering parent scroll
            if (this.scrollHeight > this.clientHeight) {
                e.stopPropagation();
            }
        }, { passive: true });
    });

    // Add touch feedback for interactive elements
    const interactiveElements = document.querySelectorAll('.section, .form-group, select, textarea');
    interactiveElements.forEach(element => {
        // Add visual feedback on touch
        element.addEventListener('touchstart', function() {
            if (!this.classList.contains('touch-active-element')) {
                this.classList.add('touch-active-element');
                setTimeout(() => {
                    this.classList.remove('touch-active-element');
                }, 300);
            }
        }, { passive: true });
    });

    // Improve image handling on mobile
    const imageOutput = document.getElementById('image-output');
    if (imageOutput) {
        imageOutput.addEventListener('click', function(e) {
            if (e.target.tagName === 'IMG') {
                // Handle image click for fullscreen view or download
                const img = e.target;

                // Create a modal for fullscreen view if it doesn't exist
                if (!document.getElementById('fullscreen-image-modal')) {
                    const modal = document.createElement('div');
                    modal.id = 'fullscreen-image-modal';
                    modal.className = 'fullscreen-modal';
                    modal.innerHTML = `
                        <div class="modal-content">
                            <span class="close-modal">&times;</span>
                            <img id="fullscreen-image" src="" alt="Fullscreen view">
                            <div class="image-actions">
                                <button id="download-image" class="text-btn">Download</button>
                            </div>
                        </div>
                    `;
                    document.body.appendChild(modal);

                    // Add close functionality
                    document.querySelector('.close-modal').addEventListener('click', function() {
                        modal.style.display = 'none';
                    });

                    // Close when clicking outside the image
                    modal.addEventListener('click', function(e) {
                        if (e.target === modal) {
                            modal.style.display = 'none';
                        }
                    });

                    // Add download functionality
                    document.getElementById('download-image').addEventListener('click', function() {
                        const fullImg = document.getElementById('fullscreen-image');
                        const link = document.createElement('a');
                        link.href = fullImg.src;
                        link.download = 'synthara-ai-image.png';
                        link.click();
                    });
                }

                // Show the modal with the clicked image
                const modal = document.getElementById('fullscreen-image-modal');
                const fullImg = document.getElementById('fullscreen-image');
                fullImg.src = img.src;
                modal.style.display = 'flex';
            }
        });
    }
}

/**
 * Improves form handling for mobile devices
 */
function improveMobileFormHandling() {
    // Prevent zoom on focus for iOS devices
    const formInputs = document.querySelectorAll('input, textarea, select');
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            // Add a class to adjust font size when focused
            this.classList.add('mobile-focused');

            // Scroll element into view when focused
            setTimeout(() => {
                this.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
        });

        input.addEventListener('blur', function() {
            this.classList.remove('mobile-focused');
        });
    });

    // Improve textarea handling
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        // Auto-resize textareas based on content
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';

            // Limit height on mobile
            if (window.innerWidth <= 768 && this.scrollHeight > 200) {
                this.style.height = '200px';
            }
        });

        // Initialize height on page load
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';

        // Add character counter for mobile
        if (isMobileDevice()) {
            const formGroup = textarea.closest('.form-group');
            if (formGroup) {
                // Create character counter element
                const charCounter = document.createElement('div');
                charCounter.className = 'char-counter';
                charCounter.textContent = `${textarea.value.length} characters`;
                formGroup.appendChild(charCounter);

                // Update counter on input
                textarea.addEventListener('input', function() {
                    charCounter.textContent = `${this.value.length} characters`;
                });
            }
        }
    });

    // Improve select elements for mobile
    const selects = document.querySelectorAll('select');
    selects.forEach(select => {
        // Add larger touch area
        select.addEventListener('touchstart', function(e) {
            // Highlight the select on touch
            this.classList.add('touch-highlight');
        }, { passive: true });

        select.addEventListener('touchend', function() {
            this.classList.remove('touch-highlight');
        }, { passive: true });

        // Add custom styling for better mobile UX
        if (isMobileDevice()) {
            select.classList.add('mobile-select');
        }
    });

    // Add swipe to clear functionality for textareas
    if (isMobileDevice()) {
        textareas.forEach(textarea => {
            let touchStartX = 0;
            let touchEndX = 0;

            textarea.addEventListener('touchstart', function(e) {
                touchStartX = e.changedTouches[0].screenX;
            }, { passive: true });

            textarea.addEventListener('touchend', function(e) {
                touchEndX = e.changedTouches[0].screenX;
                handleSwipe(this);
            }, { passive: true });

            function handleSwipe(element) {
                const swipeThreshold = 100;
                if (touchStartX - touchEndX > swipeThreshold && element.value.trim() !== '') {
                    // Left swipe - show clear button
                    showClearButton(element);
                }
            }

            function showClearButton(element) {
                // Remove any existing clear buttons
                const existingBtn = element.parentNode.querySelector('.clear-text-btn');
                if (existingBtn) {
                    existingBtn.remove();
                }

                // Create clear button
                const clearBtn = document.createElement('button');
                clearBtn.className = 'clear-text-btn';
                clearBtn.innerHTML = 'Clear';
                clearBtn.addEventListener('click', function() {
                    element.value = '';
                    this.remove();
                    // Trigger input event to resize textarea
                    const event = new Event('input', { bubbles: true });
                    element.dispatchEvent(event);
                });

                // Add button after textarea
                element.parentNode.appendChild(clearBtn);

                // Auto-remove after 3 seconds
                setTimeout(() => {
                    if (clearBtn.parentNode) {
                        clearBtn.remove();
                    }
                }, 3000);
            }
        });
    }
}

/**
 * Handles orientation changes on mobile devices
 */
function handleOrientationChanges() {
    window.addEventListener('orientationchange', function() {
        // Recalculate layout after orientation change
        setTimeout(function() {
            // Fix viewport height
            fixMobileViewportHeight();

            // Resize any dynamic elements
            const textareas = document.querySelectorAll('textarea');
            textareas.forEach(textarea => {
                textarea.style.height = 'auto';
                textarea.style.height = (textarea.scrollHeight) + 'px';
            });
        }, 200);
    });
}

/**
 * Fixes the viewport height issue on mobile browsers
 * where 100vh is taller than the visible viewport
 */
function fixMobileViewportHeight() {
    // Set a CSS variable with the actual viewport height
    const setViewportHeight = () => {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);

        // Also set a variable for safe area insets for notched phones
        if (window.CSS && CSS.supports('padding-top: env(safe-area-inset-top)')) {
            document.body.classList.add('has-safe-area');
        }

        // Adjust content height for mobile browsers with dynamic toolbars
        adjustContentHeight();
    };

    // Adjust content height to account for mobile browser toolbars
    const adjustContentHeight = () => {
        const appContainer = document.querySelector('.app-container');
        if (appContainer) {
            // On mobile, set a max-height to prevent content from being hidden behind browser UI
            if (window.innerWidth <= 768) {
                appContainer.style.minHeight = `${window.innerHeight}px`;

                // Adjust output areas to ensure they're fully visible
                const outputAreas = document.querySelectorAll('.output-content');
                outputAreas.forEach(area => {
                    // Calculate maximum safe height based on position
                    const rect = area.getBoundingClientRect();
                    const maxHeight = window.innerHeight - rect.top - 60; // 60px buffer for bottom browser UI

                    if (maxHeight < parseInt(getComputedStyle(area).maxHeight)) {
                        area.style.maxHeight = `${maxHeight}px`;
                    }
                });
            } else {
                // Reset on desktop
                appContainer.style.minHeight = '';

                const outputAreas = document.querySelectorAll('.output-content');
                outputAreas.forEach(area => {
                    area.style.maxHeight = '';
                });
            }
        }
    };

    // Set on initial load
    setViewportHeight();

    // Update on resize and orientation change
    window.addEventListener('resize', setViewportHeight);
    window.addEventListener('orientationchange', () => {
        // Delay the height adjustment to ensure accurate measurements after orientation change
        setTimeout(setViewportHeight, 100);
    });

    // Also update on scroll for mobile browsers with dynamic toolbars
    if (isMobileDevice()) {
        let lastScrollPosition = window.scrollY;
        let scrollTimeout;

        window.addEventListener('scroll', () => {
            // Clear previous timeout
            clearTimeout(scrollTimeout);

            // Set a new timeout to avoid excessive calculations
            scrollTimeout = setTimeout(() => {
                // Only adjust if scroll position has changed significantly
                if (Math.abs(lastScrollPosition - window.scrollY) > 50) {
                    lastScrollPosition = window.scrollY;
                    adjustContentHeight();
                }
            }, 100);
        }, { passive: true });
    }
}

/**
 * Detects if the device is a mobile device
 * @returns {boolean} True if the device is mobile
 */
function isMobileDevice() {
    return (window.innerWidth <= 768) ||
           (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent));
}

// Add a class to the body if it's a mobile device
if (isMobileDevice()) {
    document.body.classList.add('mobile-device');
}
