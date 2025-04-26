/**
 * Notification Banner System
 * Handles cookie consent, pipeline information, onboarding guidance, and notification caching
 */

class NotificationSystem {
    constructor() {
        this.bannerContainer = null;
        this.currentNotification = null;
        this.notificationQueue = [];
        this.cachePrefix = 'synthara_notification_';
        this.initializeBanner();
        this.checkNotifications();
    }

    /**
     * Initialize the notification banner container
     */
    initializeBanner() {
        // Create banner container if it doesn't exist
        if (!document.querySelector('.notification-banner')) {
            const banner = document.createElement('div');
            banner.className = 'notification-banner';
            banner.innerHTML = `
                <div class="notification-content">
                    <div class="notification-message"></div>
                    <div class="notification-actions"></div>
                    <button class="notification-close">&times;</button>
                </div>
            `;
            document.body.appendChild(banner);

            // Add event listener for close button
            banner.querySelector('.notification-close').addEventListener('click', () => {
                this.dismissCurrentNotification();
            });
        }

        this.bannerContainer = document.querySelector('.notification-banner');
    }

    /**
     * Check which notifications need to be shown
     */
    checkNotifications() {
        // Check for cookie consent
        if (!this.isNotificationCached('cookie_consent')) {
            this.queueNotification({
                id: 'cookie_consent',
                message: 'This website uses cookies to enhance your experience. By continuing to use this site, you consent to our use of cookies.',
                actions: [
                    { text: 'Learn More', callback: () => this.showPrivacyPolicy() },
                    { text: 'Accept', primary: true, callback: () => this.acceptCookies() },
                    { text: 'Decline', callback: () => this.declineCookies() }
                ],
                persistent: true,
                priority: 10
            });
        }

        // Check for pipeline information (only show once per session)
        if (!sessionStorage.getItem(this.cachePrefix + 'pipeline_info') && this.isNotificationCached('cookie_consent')) {
            this.queueNotification({
                id: 'pipeline_info',
                message: 'You\'re using our API Key Orchestration Pipeline. This allows you to use premium models with your own API key.',
                actions: [
                    { text: 'Learn More', callback: () => window.location.href = '/api-key' },
                    { text: 'Got it', primary: true, callback: () => this.dismissCurrentNotification() }
                ],
                persistent: false,
                priority: 5,
                cacheInSession: true
            });
        }

        // Check for onboarding guidance (only for new users)
        if (!this.isNotificationCached('onboarding_complete') && this.isNotificationCached('cookie_consent')) {
            this.queueNotification({
                id: 'onboarding_welcome',
                message: 'Welcome to Synthara AI! Would you like a quick tour of our features?',
                actions: [
                    { text: 'Skip', callback: () => this.skipOnboarding() },
                    { text: 'Take Tour', primary: true, callback: () => this.startOnboarding() }
                ],
                persistent: false,
                priority: 7
            });
        }

        // Process the queue
        this.processNotificationQueue();
    }

    /**
     * Queue a notification to be shown
     * @param {Object} notification - The notification object
     */
    queueNotification(notification) {
        this.notificationQueue.push(notification);
        this.notificationQueue.sort((a, b) => b.priority - a.priority);
    }

    /**
     * Process the notification queue
     */
    processNotificationQueue() {
        if (this.notificationQueue.length > 0 && !this.currentNotification) {
            const notification = this.notificationQueue.shift();
            this.showNotification(notification);
        }
    }

    /**
     * Show a notification in the banner
     * @param {Object} notification - The notification object
     */
    showNotification(notification) {
        this.currentNotification = notification;

        // Set message
        this.bannerContainer.querySelector('.notification-message').textContent = notification.message;

        // Clear previous actions
        const actionsContainer = this.bannerContainer.querySelector('.notification-actions');
        actionsContainer.innerHTML = '';

        // Add action buttons
        notification.actions.forEach(action => {
            const button = document.createElement('button');
            button.className = `notification-btn${action.primary ? ' primary' : ''}`;
            button.textContent = action.text;
            button.addEventListener('click', action.callback);
            actionsContainer.appendChild(button);
        });

        // Show the banner
        this.bannerContainer.classList.add('show');

        // Cache in session if needed
        if (notification.cacheInSession) {
            sessionStorage.setItem(this.cachePrefix + notification.id, 'true');
        }
    }

    /**
     * Dismiss the current notification
     */
    dismissCurrentNotification() {
        if (this.currentNotification) {
            this.bannerContainer.classList.remove('show');

            // Wait for animation to complete
            setTimeout(() => {
                this.currentNotification = null;
                this.processNotificationQueue();
            }, 300);
        }
    }

    /**
     * Check if a notification has been cached
     * @param {string} id - The notification ID
     * @returns {boolean} - Whether the notification is cached
     */
    isNotificationCached(id) {
        return localStorage.getItem(this.cachePrefix + id) === 'true';
    }

    /**
     * Cache a notification
     * @param {string} id - The notification ID
     */
    cacheNotification(id) {
        localStorage.setItem(this.cachePrefix + id, 'true');
    }

    /**
     * Show the privacy policy
     */
    showPrivacyPolicy() {
        window.open('/privacy-policy', '_blank');
    }

    /**
     * Contact email for privacy concerns
     * @returns {string} The contact email
     */
    getContactEmail() {
        return 'synthara.company@gmail.com';
    }

    /**
     * Accept cookies
     */
    acceptCookies() {
        this.cacheNotification('cookie_consent');
        this.dismissCurrentNotification();

        // Trigger any cookie-dependent features
        this.checkNotifications();
    }

    /**
     * Decline cookies
     */
    declineCookies() {
        // Still cache the decision but set a flag that cookies were declined
        this.cacheNotification('cookie_consent');
        localStorage.setItem(this.cachePrefix + 'cookies_declined', 'true');
        this.dismissCurrentNotification();

        // Show a follow-up notification about limited functionality
        this.queueNotification({
            id: 'cookies_declined_info',
            message: 'You\'ve declined cookies. Some features may be limited. You can change this decision in your settings.',
            actions: [
                { text: 'OK', primary: true, callback: () => this.dismissCurrentNotification() }
            ],
            persistent: false,
            priority: 8
        });

        this.processNotificationQueue();
    }

    /**
     * Skip the onboarding process
     */
    skipOnboarding() {
        this.cacheNotification('onboarding_complete');
        this.dismissCurrentNotification();
    }

    /**
     * Start the onboarding process
     */
    startOnboarding() {
        this.dismissCurrentNotification();

        // Queue onboarding steps
        this.queueNotification({
            id: 'onboarding_step1',
            message: 'Step 1: Choose a model from the dropdown menu to generate text or images.',
            actions: [
                { text: 'Next', primary: true, callback: () => this.showOnboardingStep2() }
            ],
            persistent: false,
            priority: 9
        });

        this.processNotificationQueue();
    }

    /**
     * Show onboarding step 2
     */
    showOnboardingStep2() {
        this.dismissCurrentNotification();

        this.queueNotification({
            id: 'onboarding_step2',
            message: 'Step 2: For premium models like Llama-4-Maverick, you\'ll need to provide your own API key.',
            actions: [
                { text: 'Next', primary: true, callback: () => this.showOnboardingStep3() }
            ],
            persistent: false,
            priority: 9
        });

        this.processNotificationQueue();
    }

    /**
     * Show onboarding step 3
     */
    showOnboardingStep3() {
        this.dismissCurrentNotification();

        this.queueNotification({
            id: 'onboarding_step3',
            message: 'Step 3: Explore our resources page to learn more about the models we offer.',
            actions: [
                { text: 'Finish', primary: true, callback: () => this.completeOnboarding() }
            ],
            persistent: false,
            priority: 9
        });

        this.processNotificationQueue();
    }

    /**
     * Complete the onboarding process
     */
    completeOnboarding() {
        this.cacheNotification('onboarding_complete');
        this.dismissCurrentNotification();

        // Show completion message
        this.queueNotification({
            id: 'onboarding_complete_message',
            message: 'You\'re all set! Enjoy using Synthara AI.',
            actions: [
                { text: 'Get Started', primary: true, callback: () => this.dismissCurrentNotification() }
            ],
            persistent: false,
            priority: 8
        });

        this.processNotificationQueue();
    }
}

// Initialize the notification system when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.notificationSystem = new NotificationSystem();
});
