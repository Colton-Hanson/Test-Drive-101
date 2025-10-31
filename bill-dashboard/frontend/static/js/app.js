// API Base URL
const API_BASE = '/api';

// Load dashboard data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});

// Load all dashboard data
async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE}/dashboard/summary`);
        const data = await response.json();

        // Update summary cards
        document.getElementById('totalBalance').textContent = formatCurrency(data.total_balance);
        document.getElementById('totalDue').textContent = formatCurrency(data.total_due);
        document.getElementById('urgentBills').textContent = data.urgent_bills;

        // Load accounts
        displayAccounts(data.accounts);

        // Load bills
        displayBills(data.bills);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showNotification('Failed to load dashboard data', 'error');
    }
}

// Display bank accounts
function displayAccounts(accounts) {
    const container = document.getElementById('accountsContainer');

    if (!accounts || accounts.length === 0) {
        container.innerHTML = '<p class="empty-state">No accounts connected yet. Click "Connect Account" to get started.</p>';
        return;
    }

    container.innerHTML = accounts.map(account => `
        <div class="account-card">
            <h3>${account.account_name}</h3>
            <p class="bank-name">${account.institution_name}</p>
            <p class="balance">${formatCurrency(account.current_balance)}</p>
            <p class="balance-label">Current Balance</p>
            ${account.available_balance ? `<p class="balance-label">Available: ${formatCurrency(account.available_balance)}</p>` : ''}
        </div>
    `).join('');
}

// Display bills
function displayBills(bills) {
    const container = document.getElementById('billsContainer');

    if (!bills || bills.length === 0) {
        container.innerHTML = '<p class="empty-state">No bills added yet. Click "Add Bill" to get started.</p>';
        return;
    }

    container.innerHTML = bills.map(bill => {
        const urgencyClass = getUrgencyClass(bill.days_until_due);
        const urgencyBadge = getUrgencyBadge(bill.days_until_due);

        return `
            <div class="bill-item ${bill.paid ? 'paid' : urgencyClass}">
                <div class="bill-info">
                    <h3>${bill.company_name}</h3>
                    <div class="bill-meta">
                        <span>💵 ${formatCurrency(bill.amount)}</span>
                        <span>📅 Due: ${formatDate(bill.due_date)}</span>
                        <span>${urgencyBadge}</span>
                        ${bill.category ? `<span>🏷️ ${bill.category}</span>` : ''}
                    </div>
                    ${bill.notes ? `<p style="margin-top: 8px; color: #666; font-size: 0.9rem;">${bill.notes}</p>` : ''}
                </div>
                <div class="bill-actions">
                    ${!bill.paid ? `
                        ${bill.payment_url ?
                            `<button class="btn btn-success btn-small" onclick="payBill(${bill.id}, '${bill.payment_url}')">Pay Bill</button>` :
                            `<button class="btn btn-success btn-small" onclick="markAsPaid(${bill.id})">Mark Paid</button>`
                        }
                    ` : ''}
                    <button class="btn btn-secondary btn-small" onclick="editBill(${bill.id})">Edit</button>
                    <button class="btn btn-danger btn-small" onclick="deleteBill(${bill.id})">Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

// Get urgency class based on days until due
function getUrgencyClass(days) {
    if (days < 0) return 'urgent';
    if (days <= 7) return 'urgent';
    return '';
}

// Get urgency badge
function getUrgencyBadge(days) {
    if (days < 0) {
        return `<span class="badge urgent">OVERDUE by ${Math.abs(days)} days</span>`;
    } else if (days === 0) {
        return '<span class="badge urgent">DUE TODAY</span>';
    } else if (days <= 7) {
        return `<span class="badge urgent">${days} days left</span>`;
    } else if (days <= 14) {
        return `<span class="badge soon">${days} days left</span>`;
    } else {
        return `<span class="badge ok">${days} days left</span>`;
    }
}

// Show add bill modal
function showAddBillModal() {
    document.getElementById('addBillModal').classList.add('show');
}

// Close add bill modal
function closeAddBillModal() {
    document.getElementById('addBillModal').classList.remove('show');
    document.getElementById('addBillForm').reset();
}

// Add a new bill
async function addBill(event) {
    event.preventDefault();

    const formData = {
        company_name: document.getElementById('companyName').value,
        amount: parseFloat(document.getElementById('amount').value),
        due_date: document.getElementById('dueDate').value,
        category: document.getElementById('category').value,
        payment_url: document.getElementById('paymentUrl').value,
        notes: document.getElementById('notes').value
    };

    try {
        const response = await fetch(`${API_BASE}/bills`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            showNotification('Bill added successfully!', 'success');
            closeAddBillModal();
            loadDashboard();
        } else {
            const error = await response.json();
            showNotification('Failed to add bill: ' + error.error, 'error');
        }
    } catch (error) {
        console.error('Error adding bill:', error);
        showNotification('Failed to add bill', 'error');
    }
}

// Pay a bill
function payBill(billId, paymentUrl) {
    // Open payment URL in new tab
    window.open(paymentUrl, '_blank');

    // Ask user if they completed the payment
    setTimeout(() => {
        if (confirm('Did you complete the payment?')) {
            markAsPaid(billId);
        }
    }, 1000);
}

// Mark bill as paid
async function markAsPaid(billId) {
    try {
        const response = await fetch(`${API_BASE}/bills/${billId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ paid: true })
        });

        if (response.ok) {
            showNotification('Bill marked as paid!', 'success');
            loadDashboard();
        } else {
            showNotification('Failed to update bill', 'error');
        }
    } catch (error) {
        console.error('Error updating bill:', error);
        showNotification('Failed to update bill', 'error');
    }
}

// Delete a bill
async function deleteBill(billId) {
    if (!confirm('Are you sure you want to delete this bill?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/bills/${billId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showNotification('Bill deleted successfully!', 'success');
            loadDashboard();
        } else {
            showNotification('Failed to delete bill', 'error');
        }
    } catch (error) {
        console.error('Error deleting bill:', error);
        showNotification('Failed to delete bill', 'error');
    }
}

// Edit bill (TODO: Implement edit modal)
function editBill(billId) {
    showNotification('Edit functionality coming soon!', 'info');
}

// Connect Plaid account
function connectPlaid() {
    showNotification('Plaid integration coming soon! You will be able to connect your bank accounts securely.', 'info');
}

// Utility: Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount || 0);
}

// Utility: Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

// Show notification
function showNotification(message, type = 'info') {
    // Simple alert for now, can be replaced with a toast notification
    alert(message);
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('addBillModal');
    if (event.target === modal) {
        closeAddBillModal();
    }
}
