// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Sample scenarios
const SAMPLE_SCENARIOS = {
    cet1: {
        question: "How should this Common Equity Tier 1 capital be reported?",
        scenario: "The bank has issued ordinary shares worth £500 million with full voting rights. These shares are perpetual, fully paid up, and meet all CRR Article 28 criteria for CET1 classification. The bank also has retained earnings of £200 million that have been verified by external auditors. Additionally, there are accumulated other comprehensive income reserves of £50 million."
    },
    at1: {
        question: "How should this Additional Tier 1 instrument be reported?",
        scenario: "The bank issued £100 million of perpetual subordinated bonds that include a mandatory conversion to ordinary shares if the CET1 ratio falls below 7%. The instruments are callable after 5 years with regulatory approval. They pay a non-cumulative discretionary coupon. The instruments meet all AT1 criteria under CRR."
    },
    deduction: {
        question: "What deductions should be applied to CET1 capital?",
        scenario: "The bank has goodwill and other intangible assets totaling £75 million on its balance sheet. There are also deferred tax assets of £30 million that rely on future profitability. The bank holds £10 million of its own CET1 instruments acquired through a share buyback program."
    }
};

// DOM Elements
const queryForm = document.getElementById('queryForm');
const questionInput = document.getElementById('question');
const scenarioInput = document.getElementById('scenario');
const templateSelect = document.getElementById('template');
const submitBtn = document.getElementById('submitBtn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoader = submitBtn.querySelector('.btn-loader');
const statusBadge = document.getElementById('statusBadge');
const resultsSection = document.getElementById('resultsSection');
const populatedFields = document.getElementById('populatedFields');
const auditTrail = document.getElementById('auditTrail');
const validationFlags = document.getElementById('validationFlags');
const validationCard = document.getElementById('validationCard');
const retrievedContext = document.getElementById('retrievedContext');

// Event Listeners
queryForm.addEventListener('submit', handleSubmit);

// Sample scenario buttons
document.querySelectorAll('.scenario-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const scenarioKey = btn.dataset.scenario;
        const scenario = SAMPLE_SCENARIOS[scenarioKey];
        if (scenario) {
            questionInput.value = scenario.question;
            scenarioInput.value = scenario.scenario;
            // Smooth scroll to form
            queryForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// Form submission handler
async function handleSubmit(e) {
    e.preventDefault();

    // Update UI to loading state
    setLoadingState(true);
    updateStatus('Processing...', 'warning');

    // Get form data
    const formData = {
        question: questionInput.value,
        scenario: scenarioInput.value,
        template_code: templateSelect.value
    };

    try {
        // Call API
        const response = await fetch(`${API_BASE_URL}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API request failed');
        }

        const result = await response.json();

        // Display results
        displayResults(result);
        updateStatus('Complete', 'success');

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (error) {
        console.error('Error:', error);
        updateStatus('Error', 'error');
        alert(`Error: ${error.message}\n\nPlease ensure:\n1. Backend server is running (python -m uvicorn backend.main:app --reload)\n2. Documents are ingested (python backend/ingest_documents.py)\n3. OpenAI API key is configured in .env file`);
    } finally {
        setLoadingState(false);
    }
}

// Set loading state
function setLoadingState(isLoading) {
    submitBtn.disabled = isLoading;
    btnText.style.display = isLoading ? 'none' : 'inline';
    btnLoader.style.display = isLoading ? 'flex' : 'none';
}

// Update status badge
function updateStatus(text, type) {
    const statusText = statusBadge.querySelector('span:last-child');
    const statusDot = statusBadge.querySelector('.status-dot');

    statusText.textContent = text;

    // Update colors based on type
    const colors = {
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444'
    };

    const color = colors[type] || colors.success;
    statusDot.style.background = color;
    statusBadge.style.borderColor = `${color}33`;
    statusBadge.style.background = `${color}1a`;
    statusBadge.style.color = color;
}

// Display results
function displayResults(result) {
    // Show results section
    resultsSection.style.display = 'block';

    // Display populated fields
    displayPopulatedFields(result.fields);

    // Display audit trail
    displayAuditTrail(result.audit_log);

    // Display validation flags
    if (result.validation_flags && result.validation_flags.length > 0) {
        displayValidationFlags(result.validation_flags);
        validationCard.style.display = 'block';
    } else {
        validationCard.style.display = 'none';
    }

    // Display retrieved context
    if (result.retrieved_context) {
        displayRetrievedContext(result.retrieved_context);
    }
}

// Display populated fields
function displayPopulatedFields(fields) {
    if (!fields || fields.length === 0) {
        populatedFields.innerHTML = '<p style="color: var(--text-muted);">No fields populated</p>';
        return;
    }

    populatedFields.innerHTML = fields.map(field => `
        <div class="field-item">
            <div class="field-header">
                <span class="field-code">${escapeHtml(field.field_code)}</span>
                <span class="field-value">${escapeHtml(field.value)}</span>
            </div>
            <div class="field-name">${escapeHtml(field.field_name || 'N/A')}</div>
            ${field.justification ? `
                <div class="field-justification">
                    <strong>Justification:</strong> ${escapeHtml(field.justification)}
                </div>
            ` : ''}
            ${field.source_rule ? `
                <div class="field-source">
                    <strong>Source:</strong> ${escapeHtml(field.source_rule)}
                </div>
            ` : ''}
        </div>
    `).join('');
}

// Display audit trail
function displayAuditTrail(auditLog) {
    if (!auditLog || auditLog.length === 0) {
        auditTrail.innerHTML = '<p style="color: var(--text-muted);">No audit trail available</p>';
        return;
    }

    auditTrail.innerHTML = auditLog.map((entry, index) => `
        <div class="audit-item">
            ${index + 1}. ${escapeHtml(entry)}
        </div>
    `).join('');
}

// Display validation flags
function displayValidationFlags(flags) {
    validationFlags.innerHTML = flags.map(flag => `
        <div class="validation-item">
            ⚠️ ${escapeHtml(flag)}
        </div>
    `).join('');
}

// Display retrieved context
function displayRetrievedContext(contexts) {
    if (!contexts || contexts.length === 0) {
        retrievedContext.innerHTML = '<p style="color: var(--text-muted);">No context retrieved</p>';
        return;
    }

    retrievedContext.innerHTML = contexts.map(ctx => `
        <div class="context-item">
            <span class="context-source">${escapeHtml(ctx.source)}</span>
            <div class="context-content">${escapeHtml(ctx.content)}</div>
        </div>
    `).join('');
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Check backend health on load
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (response.ok) {
            const data = await response.json();
            updateStatus(`Ready (${data.documents_loaded} docs loaded)`, 'success');
        } else {
            updateStatus('Backend not responding', 'error');
        }
    } catch (error) {
        updateStatus('Backend offline', 'error');
        console.warn('Backend health check failed:', error.message);
    }
}

// Initialize
checkBackendHealth();
