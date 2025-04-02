document.addEventListener('DOMContentLoaded', function() {
    // Model selection elements
    const providerSelect = document.getElementById('providerSelect');
    const modelSelect = document.getElementById('modelSelect');
    const modelSelectionForm = document.getElementById('modelSelectionForm');
    
    // Form elements
    const diagnoseForm = document.getElementById('diagnoseForm');
    const treatmentForm = document.getElementById('treatmentForm');
    const researchForm = document.getElementById('researchForm');
    const uploadForm = document.getElementById('uploadForm');
    const resultContainer = document.getElementById('resultContainer');
    
    // Visualization elements
    const visualizationContainer = document.getElementById('visualizationContainer');
    const chartContainer = document.getElementById('chartContainer');
    const saveVisualizationBtn = document.getElementById('saveVisualizationBtn');
    const visualizationsGallery = document.getElementById('visualizationsGallery');
    const noVisualizationsMessage = document.getElementById('noVisualizationsMessage');
    
    // Document elements
    const documentList = document.getElementById('documentList');
    const noDocumentsMessage = document.getElementById('noDocumentsMessage');
    
    // Other UI elements
    const copyResponseBtn = document.querySelector('.copy-response-btn');
    
    // Storage for current visualization data
    let currentVisualization = null;
    
    // Initialize
    loadProviders();
    loadDocuments();
    loadSavedVisualizations();

    // Function to load providers and models
    async function loadProviders() {
        try {
            const response = await fetch('/api/providers');
            const providers = await response.json();
            
            // Add event listener for provider change
            providerSelect.addEventListener('change', function() {
                updateModelOptions(providers);
            });
            
            // Initial population of models
            updateModelOptions(providers);
        } catch (error) {
            console.error('Failed to load providers:', error);
        }
    }
    
    // Function to update model options based on selected provider
    function updateModelOptions(providers) {
        const selectedProvider = providerSelect.value;
        const providerData = providers[selectedProvider];
        
        // Clear existing options
        modelSelect.innerHTML = '';
        
        if (providerData && providerData.available_models) {
            providerData.available_models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                if (model === providerData.default_model) {
                    option.selected = true;
                }
                modelSelect.appendChild(option);
            });
        }
    }
    
    // Function to handle model selection form submission
    modelSelectionForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const provider = providerSelect.value;
        const model = modelSelect.value;
        
        callAPI('/api/change_provider', { provider, model });
    });

    // Function to load documents from the server
    async function loadDocuments() {
        try {
            const response = await fetch('/api/documents');
            
            // Check if the response is JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                console.error('Documents response is not JSON');
                return;
            }
            
            const data = await response.json();
            
            if (data.documents && data.documents.length > 0) {
                noDocumentsMessage.classList.add('d-none');
                documentList.innerHTML = '';
                
                data.documents.forEach(docName => {
                    const item = document.createElement('a');
                    item.href = '#';
                    item.className = 'list-group-item list-group-item-action';
                    item.textContent = docName;
                    documentList.appendChild(item);
                });
            } else {
                noDocumentsMessage.classList.remove('d-none');
                documentList.innerHTML = '';
            }
        } catch (error) {
            console.error('Failed to load documents:', error);
            noDocumentsMessage.textContent = 'Failed to load documents. Please try again later.';
            noDocumentsMessage.classList.remove('d-none');
            documentList.innerHTML = '';
        }
    }
    
    // Function to load saved visualizations from localStorage
    function loadSavedVisualizations() {
        const savedVisualizations = JSON.parse(localStorage.getItem('medicalAI_visualizations') || '[]');
        
        if (savedVisualizations.length > 0) {
            noVisualizationsMessage.classList.add('d-none');
            visualizationsGallery.innerHTML = '';
            
            savedVisualizations.forEach((viz, index) => {
                const vizCard = document.createElement('div');
                vizCard.className = 'col-md-6 col-lg-4 mb-4';
                
                let vizContent = '';
                if (viz.type === 'bar') {
                    vizContent = `<img src="data:image/png;base64,${viz.data}" class="img-fluid" alt="Visualization">`;
                } else {
                    vizContent = `<div id="savedViz${index}" class="viz-container"></div>`;
                    // Will be rendered after adding to DOM
                }
                
                vizCard.innerHTML = `
                    <div class="card h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="mb-0">${viz.title}</h6>
                            <button class="btn btn-sm btn-outline-danger delete-viz-btn" data-index="${index}">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                        <div class="card-body text-center">
                            ${vizContent}
                        </div>
                        <div class="card-footer text-muted small">
                            ${new Date(viz.date).toLocaleString()}
                        </div>
                    </div>
                `;
                
                visualizationsGallery.appendChild(vizCard);
                
                // Render Plotly charts after adding to DOM
                if (viz.type === 'line' || viz.type === 'pie') {
                    const plotlyData = JSON.parse(viz.data);
                    Plotly.newPlot(`savedViz${index}`, plotlyData.data, plotlyData.layout);
                }
            });
            
            // Add event listeners for delete buttons
            document.querySelectorAll('.delete-viz-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const index = parseInt(this.dataset.index);
                    deleteVisualization(index);
                });
            });
        } else {
            noVisualizationsMessage.classList.remove('d-none');
            visualizationsGallery.innerHTML = '';
        }
    }
    
    // Function to save current visualization
    saveVisualizationBtn.addEventListener('click', function() {
        if (!currentVisualization) return;
        
        const savedVisualizations = JSON.parse(localStorage.getItem('medicalAI_visualizations') || '[]');
        
        // Add timestamp to visualization data
        currentVisualization.date = new Date().toISOString();
        
        savedVisualizations.push(currentVisualization);
        localStorage.setItem('medicalAI_visualizations', JSON.stringify(savedVisualizations));
        
        // Show success message briefly
        this.textContent = 'Saved!';
        this.classList.replace('btn-outline-dark', 'btn-success');
        
        setTimeout(() => {
            this.innerHTML = '<i class="bi bi-bookmark-plus"></i> Save Visualization';
            this.classList.replace('btn-success', 'btn-outline-dark');
        }, 2000);
        
        // Reload visualizations gallery if it's visible
        if (!document.getElementById('visualizations').classList.contains('d-none')) {
            loadSavedVisualizations();
        }
    });
    
    // Function to delete a saved visualization
    function deleteVisualization(index) {
        const savedVisualizations = JSON.parse(localStorage.getItem('medicalAI_visualizations') || '[]');
        
        if (index >= 0 && index < savedVisualizations.length) {
            savedVisualizations.splice(index, 1);
            localStorage.setItem('medicalAI_visualizations', JSON.stringify(savedVisualizations));
            loadSavedVisualizations();
        }
    }
    
    // Function to handle document upload
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('documentFile');
        
        if (!fileInput.files || fileInput.files.length === 0) {
            showError('Please select a file to upload');
            return;
        }
        
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);
        
        showLoading();
        
        fetch('/api/upload_document', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.success) {
                fileInput.value = '';
                displayResult(`Document uploaded: ${data.message}`);
                loadDocuments();
            } else {
                showError(data.error || 'Error uploading document');
            }
        })
        .catch(error => {
            hideLoading();
            showError('Network error: ' + error.message);
        });
    });

    // Function for copying response to clipboard
    copyResponseBtn.addEventListener('click', function() {
        const text = resultContainer.textContent;
        
        navigator.clipboard.writeText(text)
            .then(() => {
                // Show success message briefly
                this.innerHTML = '<i class="bi bi-check-lg"></i> Copied';
                this.classList.replace('btn-outline-light', 'btn-success');
                
                setTimeout(() => {
                    this.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
                    this.classList.replace('btn-success', 'btn-outline-light');
                }, 2000);
            })
            .catch(err => {
                console.error('Error copying text: ', err);
            });
    });

    // Function to display loading state
    function showLoading() {
        resultContainer.innerHTML = '';
        resultContainer.classList.add('loading');
        
        // Hide visualization while loading
        visualizationContainer.classList.add('d-none');
        currentVisualization = null;
    }

    // Function to hide loading state
    function hideLoading() {
        resultContainer.classList.remove('loading');
    }

    // Function to display results
    function displayResult(result) {
        hideLoading();
        resultContainer.textContent = result;
    }

    // Function to display errors
    function showError(error) {
        hideLoading();
        resultContainer.innerHTML = `<div class="alert alert-danger">${error}</div>`;
        
        // Hide visualization on error
        visualizationContainer.classList.add('d-none');
        currentVisualization = null;
    }
    
    // Function to display visualization
    function displayVisualization(visualization) {
        if (!visualization) {
            visualizationContainer.classList.add('d-none');
            currentVisualization = null;
            return;
        }
        
        visualizationContainer.classList.remove('d-none');
        chartContainer.innerHTML = '';
        
        // Store visualization for saving
        currentVisualization = {
            type: visualization.type,
            data: visualization.type === 'bar' ? visualization.image : visualization.data,
            title: 'Medical Visualization'
        };
        
        if (visualization.type === 'bar') {
            // For bar charts (matplotlib - static image)
            chartContainer.innerHTML = `<img src="data:image/png;base64,${visualization.image}" class="img-fluid" alt="Bar Chart">`;
        } else if (visualization.type === 'pie' || visualization.type === 'line') {
            // For interactive Plotly charts
            const plotlyData = JSON.parse(visualization.data);
            Plotly.newPlot(chartContainer, plotlyData.data, plotlyData.layout);
        }
    }

    // Helper function for API calls
    async function callAPI(endpoint, data) {
        try {
            showLoading();
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin', // Include credentials for session cookies
                body: JSON.stringify(data)
            });

            // Check if the response is JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Response is not JSON. You may need to log in again.');
            }

            const result = await response.json();
            hideLoading();
            
            if (response.ok) {
                displayResult(result.result);
                
                // Handle visualization if present
                if (result.visualization) {
                    displayVisualization(result.visualization);
                } else {
                    visualizationContainer.classList.add('d-none');
                    currentVisualization = null;
                }
            } else {
                showError(result.error || 'An unexpected error occurred');
            }
        } catch (error) {
            hideLoading();
            if (error.message.includes('JSON')) {
                // This is likely a login issue
                showError('Authentication error: Please log in to continue');
                // Redirect to login after a delay
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                showError('Network error: ' + error.message);
            }
        }
    }

    // Diagnose form submission
    diagnoseForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const symptoms = document.getElementById('symptoms').value.trim();
        const includeVisualization = document.getElementById('includeVisualizationSymptoms').checked;
        
        if (!symptoms) {
            showError('Please enter your symptoms');
            return;
        }
        
        callAPI('/api/diagnose', { 
            symptoms,
            include_visualization: includeVisualization
        });
    });

    // Treatment form submission
    treatmentForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const condition = document.getElementById('condition').value.trim();
        const includeVisualization = document.getElementById('includeVisualizationTreatment').checked;
        
        if (!condition) {
            showError('Please enter a medical condition');
            return;
        }
        
        callAPI('/api/treatment', { 
            condition,
            include_visualization: includeVisualization
        });
    });

    // Research form submission
    researchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const disease = document.getElementById('disease').value.trim();
        const includeVisualization = document.getElementById('includeVisualizationResearch').checked;
        
        if (!disease) {
            showError('Please enter a disease name');
            return;
        }
        
        callAPI('/api/research', { 
            disease,
            include_visualization: includeVisualization
        });
    });

    // Analytics Dashboard Functions
    async function loadAnalyticsDashboard() {
        try {
            // Load adherence data
            const adherenceResponse = await fetch('/api/analytics/adherence');
            if (adherenceResponse.ok) {
                const adherenceData = await adherenceResponse.json();
                if (adherenceData.success) {
                    updateAdherenceChart(adherenceData.statistics);
                }
            }
            
            // Load health metrics
            const metricsResponse = await fetch('/api/analytics/health_metrics');
            if (metricsResponse.ok) {
                const metricsData = await metricsResponse.json();
                if (metricsData.success) {
                    updateHealthMetricsChart(metricsData.metrics);
                }
            }
            
            // Load health activities
            const activitiesResponse = await fetch('/api/analytics/health_activities');
            if (activitiesResponse.ok) {
                const activitiesData = await activitiesResponse.json();
                if (activitiesData.success) {
                    updateHealthActivitiesList(activitiesData.activities);
                }
            }
        } catch (error) {
            console.error('Failed to load analytics data:', error);
        }
    }

    function updateAdherenceChart(statistics) {
        const adherenceChart = Chart.getChart('adherenceChart');
        if (adherenceChart) {
            adherenceChart.data.datasets[0].data = [
                statistics.taken || 0,
                statistics.missed || 0,
                statistics.upcoming || 0
            ];
            adherenceChart.update();
        }
    }

    function updateHealthMetricsChart(metrics) {
        const healthMetricsChart = Chart.getChart('healthMetricsChart');
        if (healthMetricsChart && metrics) {
            // Extract blood pressure data
            if (metrics.blood_pressure) {
                const bpData = metrics.blood_pressure.map(item => item.value);
                const labels = metrics.blood_pressure.map(item => {
                    const date = new Date(item.date);
                    return date.toLocaleString('default', { month: 'short' });
                });
                
                healthMetricsChart.data.labels = labels;
                healthMetricsChart.data.datasets[0].data = bpData;
                
                // Extract blood glucose data if it exists
                if (metrics.blood_glucose) {
                    const bgData = metrics.blood_glucose.map(item => item.value);
                    healthMetricsChart.data.datasets[1].data = bgData;
                }
                
                healthMetricsChart.update();
            }
        }
    }

    function updateHealthActivitiesList(activities) {
        const healthActivityList = document.getElementById('healthActivityList');
        if (healthActivityList && activities && activities.length > 0) {
            // Clear existing list
            healthActivityList.innerHTML = '';
            
            // Add new activities
            activities.forEach(activity => {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';
                
                // Set item text
                li.textContent = activity.title;
                
                // Add badge based on status
                const badge = document.createElement('span');
                
                if (activity.status === 'due_today') {
                    badge.className = 'badge bg-success rounded-pill';
                    badge.textContent = 'Today';
                } else if (activity.status === 'upcoming') {
                    badge.className = 'badge bg-warning rounded-pill';
                    
                    // Calculate days until due
                    const dueDate = new Date(activity.due_date);
                    const today = new Date();
                    const diffTime = Math.abs(dueDate - today);
                    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                    
                    badge.textContent = diffDays === 1 ? 'Tomorrow' : `${diffDays} days`;
                } else if (activity.status === 'overdue') {
                    badge.className = 'badge bg-danger rounded-pill';
                    badge.textContent = 'Overdue';
                }
                
                li.appendChild(badge);
                healthActivityList.appendChild(li);
            });
        }
    }

    // Additional event listener for analytics dashboard
    const analyticsDashboardCollapse = document.getElementById('analyticsDashboardCollapse');
    if (analyticsDashboardCollapse) {
        // Initialize analytics when the dashboard is opened
        analyticsDashboardCollapse.addEventListener('shown.bs.collapse', function() {
            loadAnalyticsDashboard();
        });
    }
}); 