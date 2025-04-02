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
            const data = await response.json();
            
            if (data.documents && data.documents.length > 0) {
                noDocumentsMessage.classList.add('d-none');
                documentList.innerHTML = '';
                
                data.documents.forEach(document => {
                    const item = document.create('a');
                    item.href = '#';
                    item.className = 'list-group-item list-group-item-action';
                    item.textContent = document;
                    documentList.appendChild(item);
                });
            } else {
                noDocumentsMessage.classList.remove('d-none');
                documentList.innerHTML = '';
            }
        } catch (error) {
            console.error('Failed to load documents:', error);
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
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
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
            showError('Network error: ' + error.message);
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
}); 