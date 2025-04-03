/**
 * Medical AI Assistant Settings Manager
 * Handles saving and loading user settings using localStorage
 */

class SettingsManager {
    constructor() {
        this.settings = {};
        this.loadSettings();
        this.setupEventListeners();
    }

    /**
     * Load settings from localStorage
     */
    loadSettings() {
        const savedSettings = localStorage.getItem('medicalAISettings');
        if (savedSettings) {
            try {
                this.settings = JSON.parse(savedSettings);
                this.applySettings();
            } catch (error) {
                console.error('Error parsing saved settings:', error);
                // Reset settings if there's an error
                localStorage.removeItem('medicalAISettings');
                this.settings = this.getDefaultSettings();
            }
        } else {
            this.settings = this.getDefaultSettings();
        }
    }

    /**
     * Get default settings
     */
    getDefaultSettings() {
        return {
            general: {
                userName: '',
                emailAddress: '',
                timeFormat: '12h',
                dateFormat: 'MM/DD/YYYY',
                timezone: 'UTC'
            },
            ai: {
                modelProvider: 'openai',
                apiKey: '',
                modelName: 'gpt-3.5-turbo',
                temperature: 0.7
            },
            notifications: {
                emailMedicationReminders: true,
                emailWeeklyReports: true,
                emailMedicationChanges: false,
                appMedicationReminders: true,
                appHealthTips: true,
                appNewFeatures: true,
                reminderTime: 30
            },
            health: {
                height: '',
                weight: '',
                bloodType: '',
                dateOfBirth: '',
                allergies: '',
                chronicConditions: '',
                medications: '',
                shareHealthData: false,
                allowAnonymizedData: false
            },
            language: {
                interfaceLanguage: 'en',
                medicalLanguage: 'en',
                simplifiedLanguage: false,
                includeTranslations: true
            },
            appearance: {
                theme: 'light',
                fontSize: 'medium',
                colorScheme: 'blue',
                highContrast: false,
                reduceMotion: false,
                useScreenReader: false
            },
            dataManagement: {
                chatRetention: 30
            }
        };
    }

    /**
     * Apply settings to form elements
     */
    applySettings() {
        // General settings
        this.setFormValue('#userName', this.settings.general.userName);
        this.setFormValue('#emailAddress', this.settings.general.emailAddress);
        this.setRadioValue('timeFormat', this.settings.general.timeFormat);
        this.setFormValue('#dateFormat', this.settings.general.dateFormat);
        this.setFormValue('#timezone', this.settings.general.timezone);

        // AI Model settings
        this.setFormValue('#modelProvider', this.settings.ai.modelProvider);
        this.setFormValue('#apiKey', this.settings.ai.apiKey);
        this.setFormValue('#modelName', this.settings.ai.modelName);
        this.setFormValue('#temperature', this.settings.ai.temperature);

        // Notification settings
        this.setCheckboxValue('#emailMedicationReminders', this.settings.notifications.emailMedicationReminders);
        this.setCheckboxValue('#emailWeeklyReports', this.settings.notifications.emailWeeklyReports);
        this.setCheckboxValue('#emailMedicationChanges', this.settings.notifications.emailMedicationChanges);
        this.setCheckboxValue('#appMedicationReminders', this.settings.notifications.appMedicationReminders);
        this.setCheckboxValue('#appHealthTips', this.settings.notifications.appHealthTips);
        this.setCheckboxValue('#appNewFeatures', this.settings.notifications.appNewFeatures);
        this.setFormValue('#reminderTime', this.settings.notifications.reminderTime);

        // Health Data settings
        this.setFormValue('#height', this.settings.health.height);
        this.setFormValue('#weight', this.settings.health.weight);
        this.setFormValue('#bloodType', this.settings.health.bloodType);
        this.setFormValue('#dateOfBirth', this.settings.health.dateOfBirth);
        this.setFormValue('#allergies', this.settings.health.allergies);
        this.setFormValue('#chronicConditions', this.settings.health.chronicConditions);
        this.setFormValue('#medications', this.settings.health.medications);
        this.setCheckboxValue('#shareHealthData', this.settings.health.shareHealthData);
        this.setCheckboxValue('#allowAnonymizedData', this.settings.health.allowAnonymizedData);

        // Language settings
        this.setFormValue('#interfaceLanguage', this.settings.language.interfaceLanguage);
        this.setFormValue('#medicalLanguage', this.settings.language.medicalLanguage);
        this.setCheckboxValue('#simplifiedLanguage', this.settings.language.simplifiedLanguage);
        this.setCheckboxValue('#includeTranslations', this.settings.language.includeTranslations);

        // Appearance settings
        this.setRadioValue('theme', this.settings.appearance.theme);
        this.setFormValue('#fontSize', this.settings.appearance.fontSize);
        this.setFormValue('#colorScheme', this.settings.appearance.colorScheme);
        this.setCheckboxValue('#highContrast', this.settings.appearance.highContrast);
        this.setCheckboxValue('#reduceMotion', this.settings.appearance.reduceMotion);
        this.setCheckboxValue('#useScreenReader', this.settings.appearance.useScreenReader);

        // Data Management settings
        this.setFormValue('#chatRetention', this.settings.dataManagement.chatRetention);

        // Apply theme immediately
        this.applyTheme();
    }

    /**
     * Apply the current theme
     */
    applyTheme() {
        document.body.setAttribute('data-theme', this.settings.appearance.theme);
        
        if (this.settings.appearance.highContrast) {
            document.body.classList.add('high-contrast');
        } else {
            document.body.classList.remove('high-contrast');
        }
        
        document.body.setAttribute('data-color-scheme', this.settings.appearance.colorScheme);
        document.body.setAttribute('data-font-size', this.settings.appearance.fontSize);
        
        if (this.settings.appearance.reduceMotion) {
            document.body.classList.add('reduce-motion');
        } else {
            document.body.classList.remove('reduce-motion');
        }
    }

    /**
     * Set up event listeners for settings forms
     */
    setupEventListeners() {
        // Listen for form submissions
        document.getElementById('generalSettingsForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveGeneralSettings();
        });

        document.getElementById('llmSettingsForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveAISettings();
        });

        document.getElementById('notificationSettingsForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveNotificationSettings();
        });

        document.getElementById('healthDataSettingsForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveHealthSettings();
        });

        document.getElementById('languageSettingsForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveLanguageSettings();
        });

        document.getElementById('appearanceSettingsForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveAppearanceSettings();
        });

        document.getElementById('dataRetentionForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveDataManagementSettings();
        });

        // Listen for theme changes to apply immediately
        const themeRadios = document.querySelectorAll('input[name="theme"]');
        themeRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                this.settings.appearance.theme = radio.value;
                this.applyTheme();
                this.saveSettings();
            });
        });

        // High contrast toggle
        document.getElementById('highContrast')?.addEventListener('change', (e) => {
            this.settings.appearance.highContrast = e.target.checked;
            this.applyTheme();
            this.saveSettings();
        });

        // Color scheme change
        document.getElementById('colorScheme')?.addEventListener('change', (e) => {
            this.settings.appearance.colorScheme = e.target.value;
            this.applyTheme();
            this.saveSettings();
        });

        // Font size change
        document.getElementById('fontSize')?.addEventListener('change', (e) => {
            this.settings.appearance.fontSize = e.target.value;
            this.applyTheme();
            this.saveSettings();
        });
    }

    /**
     * Save General Settings
     */
    saveGeneralSettings() {
        this.settings.general = {
            userName: this.getFormValue('#userName'),
            emailAddress: this.getFormValue('#emailAddress'),
            timeFormat: this.getRadioValue('timeFormat'),
            dateFormat: this.getFormValue('#dateFormat'),
            timezone: this.getFormValue('#timezone')
        };
        this.saveSettings();
        this.showSuccessMessage('#generalSettingsForm');
    }

    /**
     * Save AI Settings
     */
    saveAISettings() {
        this.settings.ai = {
            modelProvider: this.getFormValue('#modelProvider'),
            apiKey: this.getFormValue('#apiKey'),
            modelName: this.getFormValue('#modelName'),
            temperature: this.getFormValue('#temperature')
        };
        this.saveSettings();
        this.showSuccessMessage('#llmSettingsForm');
    }

    /**
     * Save Notification Settings
     */
    saveNotificationSettings() {
        this.settings.notifications = {
            emailMedicationReminders: this.getCheckboxValue('#emailMedicationReminders'),
            emailWeeklyReports: this.getCheckboxValue('#emailWeeklyReports'),
            emailMedicationChanges: this.getCheckboxValue('#emailMedicationChanges'),
            appMedicationReminders: this.getCheckboxValue('#appMedicationReminders'),
            appHealthTips: this.getCheckboxValue('#appHealthTips'),
            appNewFeatures: this.getCheckboxValue('#appNewFeatures'),
            reminderTime: this.getFormValue('#reminderTime')
        };
        this.saveSettings();
        this.showSuccessMessage('#notificationSettingsForm');
    }

    /**
     * Save Health Settings
     */
    saveHealthSettings() {
        this.settings.health = {
            height: this.getFormValue('#height'),
            weight: this.getFormValue('#weight'),
            bloodType: this.getFormValue('#bloodType'),
            dateOfBirth: this.getFormValue('#dateOfBirth'),
            allergies: this.getFormValue('#allergies'),
            chronicConditions: this.getFormValue('#chronicConditions'),
            medications: this.getFormValue('#medications'),
            shareHealthData: this.getCheckboxValue('#shareHealthData'),
            allowAnonymizedData: this.getCheckboxValue('#allowAnonymizedData')
        };
        this.saveSettings();
        this.showSuccessMessage('#healthDataSettingsForm');
    }

    /**
     * Save Language Settings
     */
    saveLanguageSettings() {
        this.settings.language = {
            interfaceLanguage: this.getFormValue('#interfaceLanguage'),
            medicalLanguage: this.getFormValue('#medicalLanguage'),
            simplifiedLanguage: this.getCheckboxValue('#simplifiedLanguage'),
            includeTranslations: this.getCheckboxValue('#includeTranslations')
        };
        this.saveSettings();
        this.showSuccessMessage('#languageSettingsForm');
    }

    /**
     * Save Appearance Settings
     */
    saveAppearanceSettings() {
        this.settings.appearance = {
            theme: this.getRadioValue('theme'),
            fontSize: this.getFormValue('#fontSize'),
            colorScheme: this.getFormValue('#colorScheme'),
            highContrast: this.getCheckboxValue('#highContrast'),
            reduceMotion: this.getCheckboxValue('#reduceMotion'),
            useScreenReader: this.getCheckboxValue('#useScreenReader')
        };
        this.applyTheme();
        this.saveSettings();
        this.showSuccessMessage('#appearanceSettingsForm');
    }

    /**
     * Save Data Management Settings
     */
    saveDataManagementSettings() {
        this.settings.dataManagement = {
            chatRetention: this.getFormValue('#chatRetention')
        };
        this.saveSettings();
        this.showSuccessMessage('#dataRetentionForm');
    }

    /**
     * Save settings to localStorage
     */
    saveSettings() {
        localStorage.setItem('medicalAISettings', JSON.stringify(this.settings));
    }

    /**
     * Helper to show success message
     */
    showSuccessMessage(formSelector) {
        const form = document.querySelector(formSelector);
        if (!form) return;

        // Check if there's already a success message
        let alert = form.querySelector('.alert-success');
        if (alert) {
            // Reset the timeout
            setTimeout(() => {
                alert.remove();
            }, 3000);
            return;
        }

        // Create a new alert
        alert = document.createElement('div');
        alert.className = 'alert alert-success mt-3 alert-dismissible fade show';
        alert.innerHTML = `
            <strong>Settings saved!</strong> Your preferences have been updated.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        form.appendChild(alert);

        // Remove the alert after 3 seconds
        setTimeout(() => {
            alert.remove();
        }, 3000);
    }

    /**
     * Helper to set form value
     */
    setFormValue(selector, value) {
        const element = document.querySelector(selector);
        if (element) {
            element.value = value;
        }
    }

    /**
     * Helper to get form value
     */
    getFormValue(selector) {
        const element = document.querySelector(selector);
        return element ? element.value : '';
    }

    /**
     * Helper to set radio button value
     */
    setRadioValue(name, value) {
        const radio = document.querySelector(`input[name="${name}"][value="${value}"]`);
        if (radio) {
            radio.checked = true;
        }
    }

    /**
     * Helper to get radio button value
     */
    getRadioValue(name) {
        const radio = document.querySelector(`input[name="${name}"]:checked`);
        return radio ? radio.value : '';
    }

    /**
     * Helper to set checkbox value
     */
    setCheckboxValue(selector, value) {
        const checkbox = document.querySelector(selector);
        if (checkbox) {
            checkbox.checked = value;
        }
    }

    /**
     * Helper to get checkbox value
     */
    getCheckboxValue(selector) {
        const checkbox = document.querySelector(selector);
        return checkbox ? checkbox.checked : false;
    }

    /**
     * Clear specific storage
     */
    clearStorage(storageType) {
        switch (storageType) {
            case 'chat':
                localStorage.removeItem('medicalAIChatHistory');
                return true;
            case 'medications':
                localStorage.removeItem('medicalAIMedications');
                return true;
            case 'health':
                // Clear health-related settings but keep other settings
                this.settings.health = this.getDefaultSettings().health;
                this.saveSettings();
                return true;
            case 'all':
                localStorage.clear();
                return true;
            default:
                return false;
        }
    }
}

// Initialize settings when document is ready
document.addEventListener('DOMContentLoaded', function() {
    window.settingsManager = new SettingsManager();
    
    // Set up clear data button listeners
    const clearButtons = document.querySelectorAll('.btn-outline-danger');
    clearButtons.forEach((button, index) => {
        button.addEventListener('click', function() {
            let storageType;
            
            // Determine what data to clear based on button index
            switch (index) {
                case 0: // Chat History
                    storageType = 'chat';
                    break;
                case 1: // Medication History
                    storageType = 'medications';
                    break;
                case 2: // Health Data
                    storageType = 'health';
                    break;
                default:
                    return;
            }
            
            if (window.settingsManager.clearStorage(storageType)) {
                const alert = document.createElement('div');
                alert.className = 'alert alert-success mt-3';
                alert.innerHTML = `<strong>Success!</strong> Data has been cleared.`;
                
                const parent = button.closest('.mb-4');
                parent.appendChild(alert);
                
                setTimeout(() => {
                    alert.remove();
                }, 3000);
            }
        });
    });
    
    // Set up delete all data button
    document.getElementById('confirmDeleteBtn')?.addEventListener('click', function() {
        if (window.settingsManager.clearStorage('all')) {
            // Show success message
            const modal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
            modal.hide();
            
            // Show success alert
            const alert = document.createElement('div');
            alert.className = 'alert alert-success';
            alert.innerHTML = `<strong>Success!</strong> All data has been deleted. Refreshing page...`;
            
            document.querySelector('.tab-content').prepend(alert);
            
            // Reload the page after a brief delay
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        }
    });
}); 