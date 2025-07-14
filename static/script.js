// DOM elements
const manualCheckBtn = document.getElementById('manual-check-btn');
const lowStockBtn = document.getElementById('low-stock-btn');
const salesAnalyticsBtn = document.getElementById('sales-analytics-btn');

const loadingElement = document.getElementById('loading');
const resultsContainer = document.getElementById('results-container');
const errorContainer = document.getElementById('error-container');
const welcomeMessage = document.getElementById('welcome-message');

const classificationBadge = document.getElementById('classification-badge');
const classificationText = document.getElementById('classification-text');
const priorityBadge = document.getElementById('priority-badge');
const priorityText = document.getElementById('priority-text');
const messagesContainer = document.getElementById('messages-container');
const errorMessage = document.getElementById('error-message');

// Utility functions
function showLoading() {
    hideAllPanels();
    loadingElement.classList.remove('hidden');
    disableButtons();
}

function hideLoading() {
    loadingElement.classList.add('hidden');
    enableButtons();
}

function showResults(data) {
    hideAllPanels();
    updateResultsDisplay(data);
    resultsContainer.classList.remove('hidden');
}

function showError(error) {
    hideAllPanels();
    errorMessage.textContent = error;
    errorContainer.classList.remove('hidden');
}

function hideAllPanels() {
    loadingElement.classList.add('hidden');
    resultsContainer.classList.add('hidden');
    errorContainer.classList.add('hidden');
    welcomeMessage.classList.add('hidden');
}

function disableButtons() {
    manualCheckBtn.disabled = true;
    lowStockBtn.disabled = true;
    salesAnalyticsBtn.disabled = true;
}

function enableButtons() {
    manualCheckBtn.disabled = false;
    lowStockBtn.disabled = false;
    salesAnalyticsBtn.disabled = false;
}

// Update results display
function updateResultsDisplay(data) {
    // Update classification badge
    classificationText.textContent = data.classification.replace('_', ' ').toUpperCase();
    
    // Update classification badge icon based on classification
    const classificationIcon = classificationBadge.querySelector('i');
    switch(data.classification) {
        case 'monitor':
            classificationIcon.className = 'fas fa-eye';
            break;
        case 'alert':
            classificationIcon.className = 'fas fa-exclamation-triangle';
            break;
        case 'action_required':
            classificationIcon.className = 'fas fa-exclamation-circle';
            break;
        default:
            classificationIcon.className = 'fas fa-info-circle';
    }
    
    // Update priority badge
    priorityText.textContent = data.priority.toUpperCase() + ' PRIORITY';
    priorityBadge.className = `priority-badge ${data.priority}`;
    
    // Clear and populate messages
    messagesContainer.innerHTML = '';
    
    if (data.messages && data.messages.length > 0) {
        data.messages.forEach(message => {
            const messageElement = createMessageElement(message);
            messagesContainer.appendChild(messageElement);
        });
    } else {
        const noMessagesElement = document.createElement('div');
        noMessagesElement.className = 'message';
        noMessagesElement.innerHTML = `
            <div class="message-role">System</div>
            <div class="message-content">No detailed messages available.</div>
        `;
        messagesContainer.appendChild(noMessagesElement);
    }
}

function createMessageElement(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message';
    
    // Format the content to be more readable
    let formattedContent = message.content;
    
    // Add some basic formatting for common patterns
    formattedContent = formattedContent
        .replace(/(\$[\d,]+\.?\d*)/g, '<strong>$1</strong>') // Highlight dollar amounts
        .replace(/(\d+%)/g, '<strong>$1</strong>') // Highlight percentages
        .replace(/(LOW STOCK|HIGH PRIORITY|CRITICAL|WARNING)/gi, '<strong style="color: #e53e3e;">$1</strong>') // Highlight alerts
        .replace(/(COMPLETED|SUCCESS|APPROVED)/gi, '<strong style="color: #38a169;">$1</strong>'); // Highlight success
    
    messageElement.innerHTML = `
        <div class="message-role">${formatRole(message.role)}</div>
        <div class="message-content">${formattedContent}</div>
    `;
    
    return messageElement;
}

function formatRole(role) {
    const roleMap = {
        'user': 'Request',
        'assistant': 'Agent Response',
        'system': 'System',
        'tool': 'Tool Result'
    };
    
    return roleMap[role] || role.charAt(0).toUpperCase() + role.slice(1);
}

// API calls
async function callSalesMonitorAPI(requestData) {
    try {
        const response = await fetch('/api/sales-monitor', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Event handlers
async function runManualCheck() {
    showLoading();
    
    try {
        const result = await callSalesMonitorAPI({
            type: 'manual_check'
        });
        
        showResults(result);
    } catch (error) {
        showError(`Failed to run manual check: ${error.message}`);
    }
}

async function runLowStockAlert() {
    showLoading();
    
    try {
        const itemName = document.getElementById('item-name').value.trim();
        const currentStock = parseInt(document.getElementById('current-stock').value);
        const reorderLevel = parseInt(document.getElementById('reorder-level').value);
        
        if (!itemName) {
            throw new Error('Please enter an item name');
        }
        
        if (isNaN(currentStock) || currentStock < 0) {
            throw new Error('Please enter a valid current stock amount');
        }
        
        if (isNaN(reorderLevel) || reorderLevel < 0) {
            throw new Error('Please enter a valid reorder level');
        }
        
        const result = await callSalesMonitorAPI({
            type: 'low_stock',
            item_name: itemName,
            current_stock: currentStock,
            reorder_level: reorderLevel
        });
        
        showResults(result);
    } catch (error) {
        showError(`Failed to run low stock alert: ${error.message}`);
    }
}

async function runSalesAnalytics() {
    showLoading();
    
    try {
        const period = document.getElementById('period').value;
        const totalSales = parseFloat(document.getElementById('total-sales').value);
        const totalOrders = parseInt(document.getElementById('total-orders').value);
        
        if (isNaN(totalSales) || totalSales < 0) {
            throw new Error('Please enter a valid total sales amount');
        }
        
        if (isNaN(totalOrders) || totalOrders < 0) {
            throw new Error('Please enter a valid total orders count');
        }
        
        const result = await callSalesMonitorAPI({
            type: 'sales_analytics',
            period: period,
            total_sales: totalSales,
            total_orders: totalOrders
        });
        
        showResults(result);
    } catch (error) {
        showError(`Failed to generate sales analytics: ${error.message}`);
    }
}

// Add event listeners
document.addEventListener('DOMContentLoaded', function() {
    manualCheckBtn.addEventListener('click', runManualCheck);
    lowStockBtn.addEventListener('click', runLowStockAlert);
    salesAnalyticsBtn.addEventListener('click', runSalesAnalytics);
    
    // Add input validation and formatting
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });
    
    // Add enter key support for form submission
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                // Find the button in the same monitor section and click it
                const section = this.closest('.monitor-section');
                const button = section.querySelector('.btn');
                if (button && !button.disabled) {
                    button.click();
                }
            }
        });
    });
    
    console.log('Sales Monitor Agent Dashboard initialized');
}); 