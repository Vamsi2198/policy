# UI Enhancement Suggestions for Metadata and Audit Dashboard

## Overview
This document outlines UI changes to display:
1. **Atlan Metadata Table** - Policy changes and lineage stored in Atlan
2. **Audit Tables** - Policy execution audit logs stored in JSON files

---

## 1. New Dashboard Tabs/Sections

### Add Two New Navigation Tabs:

```html
<!-- Add to the header or create a navigation bar -->
<div class="dashboard-tabs">
    <button class="tab-button active" onclick="showTab('governance')">
        🎯 Governance Engine
    </button>
    <button class="tab-button" onclick="showTab('metadata')">
        📊 Atlan Metadata
    </button>
    <button class="tab-button" onclick="showTab('audit')">
        📋 Audit Logs
    </button>
</div>
```

---

## 2. Metadata Tab - Policy Changes & Lineage

### A. Policy Changes Table

Add this section to display policy changes stored in Atlan:

```html
<div id="metadataTab" class="tab-content" style="display: none;">
    <div class="metadata-section">
        <h2>📝 Policy Changes (Atlan Metadata)</h2>
        
        <!-- Filters -->
        <div class="filters-bar">
            <select id="policyFilter" onchange="loadPolicyChanges()">
                <option value="">All Policies</option>
                <option value="PII_MASKING_POLICY">PII Masking</option>
                <option value="FINANCIAL_DATA_POLICY">Financial Data</option>
            </select>
            
            <select id="changeTypeFilter" onchange="loadPolicyChanges()">
                <option value="">All Changes</option>
                <option value="CREATE">Create</option>
                <option value="UPDATE">Update</option>
                <option value="DELETE">Delete</option>
                <option value="APPLY">Apply</option>
            </select>
            
            <button onclick="loadPolicyChanges()">🔄 Refresh</button>
        </div>
        
        <!-- Policy Changes Table -->
        <div class="data-table-container">
            <table class="data-table" id="policyChangesTable">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Policy Name</th>
                        <th>Change Type</th>
                        <th>Affected Assets</th>
                        <th>User</th>
                        <th>Atlan GUID</th>
                        <th>Status</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody id="policyChangesBody">
                    <!-- Populated dynamically -->
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="metadata-section">
        <h2>🔗 Data Lineage (Atlan Metadata)</h2>
        
        <!-- Lineage Filters -->
        <div class="filters-bar">
            <input type="text" id="assetFilter" placeholder="Filter by asset...">
            <select id="lineageTypeFilter" onchange="loadLineageData()">
                <option value="">All Types</option>
                <option value="DATAFLOW">Data Flow</option>
                <option value="PROCESS">Process</option>
                <option value="POLICY">Policy</option>
            </select>
            <button onclick="loadLineageData()">🔄 Refresh</button>
        </div>
        
        <!-- Lineage Table -->
        <div class="data-table-container">
            <table class="data-table" id="lineageTable">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Source Asset</th>
                        <th>→</th>
                        <th>Target Asset</th>
                        <th>Transformation</th>
                        <th>Type</th>
                        <th>Process</th>
                        <th>Atlan GUID</th>
                    </tr>
                </thead>
                <tbody id="lineageBody">
                    <!-- Populated dynamically -->
                </tbody>
            </table>
        </div>
        
        <!-- Lineage Visualization (Optional) -->
        <div class="lineage-graph">
            <h3>Lineage Graph</h3>
            <div id="lineageViz" class="graph-container">
                <!-- Can be rendered using D3.js or similar -->
            </div>
        </div>
    </div>
    
    <!-- Metadata Statistics -->
    <div class="stats-grid">
        <div class="stat-card">
            <h3>Total Policy Changes</h3>
            <div class="stat-value" id="totalPolicyChanges">0</div>
        </div>
        <div class="stat-card">
            <h3>Total Lineage Entries</h3>
            <div class="stat-value" id="totalLineageEntries">0</div>
        </div>
        <div class="stat-card">
            <h3>Recent Changes (24h)</h3>
            <div class="stat-value" id="recentChanges24h">0</div>
        </div>
    </div>
</div>
```

---

## 3. Audit Tab - Policy Execution Logs

### A. Audit Dashboard

Add this section for audit logs:

```html
<div id="auditTab" class="tab-content" style="display: none;">
    <!-- Overview Cards -->
    <div class="audit-overview">
        <div class="overview-card">
            <div class="overview-icon">📊</div>
            <div class="overview-content">
                <h3 id="totalExecutions">0</h3>
                <p>Total Executions</p>
            </div>
        </div>
        
        <div class="overview-card success">
            <div class="overview-icon">✅</div>
            <div class="overview-content">
                <h3 id="successfulExecutions">0</h3>
                <p>Successful</p>
            </div>
        </div>
        
        <div class="overview-card failed">
            <div class="overview-icon">❌</div>
            <div class="overview-content">
                <h3 id="failedExecutions">0</h3>
                <p>Failed</p>
            </div>
        </div>
        
        <div class="overview-card rate">
            <div class="overview-icon">📈</div>
            <div class="overview-content">
                <h3 id="successRate">0%</h3>
                <p>Success Rate</p>
            </div>
        </div>
    </div>
    
    <!-- Top Policies Section -->
    <div class="audit-section">
        <h2>🏆 Top Policies by Execution Count</h2>
        <div class="data-table-container">
            <table class="data-table" id="topPoliciesTable">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Policy Name</th>
                        <th>Total Executions</th>
                        <th>Successful</th>
                        <th>Failed</th>
                        <th>Total Rows Affected</th>
                        <th>Tables Affected</th>
                        <th>Last Executed</th>
                    </tr>
                </thead>
                <tbody id="topPoliciesBody">
                    <!-- Populated dynamically -->
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- Top Tables Section -->
    <div class="audit-section">
        <h2>📋 Top Tables by Policy Execution</h2>
        <div class="data-table-container">
            <table class="data-table" id="topTablesTable">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Table Name</th>
                        <th>Execution Count</th>
                        <th>Rows Affected</th>
                        <th>Policies Applied</th>
                        <th>Policy Count</th>
                    </tr>
                </thead>
                <tbody id="topTablesBody">
                    <!-- Populated dynamically -->
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- Detailed Audit Log -->
    <div class="audit-section">
        <h2>📜 Detailed Audit Log</h2>
        
        <!-- Filters -->
        <div class="filters-bar">
            <input type="text" id="auditPolicyFilter" placeholder="Filter by policy...">
            <input type="text" id="auditTableFilter" placeholder="Filter by table...">
            <select id="auditStatusFilter" onchange="loadAuditLog()">
                <option value="">All Status</option>
                <option value="SUCCESS">Success</option>
                <option value="FAILED">Failed</option>
                <option value="PARTIAL">Partial</option>
            </select>
            <button onclick="loadAuditLog()">🔄 Refresh</button>
        </div>
        
        <!-- Audit Log Table -->
        <div class="data-table-container">
            <table class="data-table" id="auditLogTable">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Policy Name</th>
                        <th>Target Table</th>
                        <th>Columns</th>
                        <th>Status</th>
                        <th>Rows Affected</th>
                        <th>Execution Time</th>
                        <th>User</th>
                        <th>Error</th>
                    </tr>
                </thead>
                <tbody id="auditLogBody">
                    <!-- Populated dynamically -->
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- Recent Activity Timeline -->
    <div class="audit-section">
        <h2>⏱️ Recent Activity (Last 24 Hours)</h2>
        <div class="timeline-container" id="recentActivityTimeline">
            <!-- Populated dynamically -->
        </div>
    </div>
</div>
```

---

## 4. JavaScript Functions to Load Data

Add these functions to fetch and display data:

```javascript
// ============================================
// Metadata Tab Functions
// ============================================

async function loadPolicyChanges() {
    try {
        const policyName = document.getElementById('policyFilter').value;
        const changeType = document.getElementById('changeTypeFilter').value;
        
        const params = new URLSearchParams();
        if (policyName) params.append('policy_name', policyName);
        if (changeType) params.append('change_type', changeType);
        params.append('limit', '100');
        
        const response = await fetch(`/api/metadata/policy-changes?${params}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            displayPolicyChanges(data.changes);
        }
    } catch (error) {
        console.error('Error loading policy changes:', error);
    }
}

function displayPolicyChanges(changes) {
    const tbody = document.getElementById('policyChangesBody');
    tbody.innerHTML = '';
    
    changes.forEach(change => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(change.timestamp).toLocaleString()}</td>
            <td><strong>${change.policy_name}</strong></td>
            <td><span class="badge ${change.change_type.toLowerCase()}">${change.change_type}</span></td>
            <td>${change.affected_assets.join(', ')}</td>
            <td>${change.user}</td>
            <td><code>${change.atlan_guid}</code></td>
            <td><span class="status-badge ${change.status.toLowerCase()}">${change.status}</span></td>
            <td><button onclick="showChangeDetails('${change.change_id}')">View</button></td>
        `;
        tbody.appendChild(row);
    });
}

async function loadLineageData() {
    try {
        const asset = document.getElementById('assetFilter').value;
        const lineageType = document.getElementById('lineageTypeFilter').value;
        
        const params = new URLSearchParams();
        if (asset) params.append('asset', asset);
        if (lineageType) params.append('lineage_type', lineageType);
        params.append('limit', '100');
        
        const response = await fetch(`/api/metadata/lineage?${params}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            displayLineageData(data.lineage_entries);
        }
    } catch (error) {
        console.error('Error loading lineage:', error);
    }
}

function displayLineageData(entries) {
    const tbody = document.getElementById('lineageBody');
    tbody.innerHTML = '';
    
    entries.forEach(entry => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(entry.timestamp).toLocaleString()}</td>
            <td><code>${entry.source_asset}</code></td>
            <td style="text-align: center;">→</td>
            <td><code>${entry.target_asset}</code></td>
            <td>${entry.transformation}</td>
            <td><span class="badge ${entry.lineage_type.toLowerCase()}">${entry.lineage_type}</span></td>
            <td>${entry.process_name}</td>
            <td><code>${entry.atlan_guid}</code></td>
        `;
        tbody.appendChild(row);
    });
}

async function loadMetadataStatistics() {
    try {
        const response = await fetch('/api/metadata/statistics');
        const data = await response.json();
        
        if (data.status === 'success') {
            const stats = data.statistics;
            document.getElementById('totalPolicyChanges').textContent = 
                stats.policy_changes.total || 0;
            document.getElementById('totalLineageEntries').textContent = 
                stats.lineage_entries.total || 0;
            document.getElementById('recentChanges24h').textContent = 
                stats.policy_changes.recent_24h || 0;
        }
    } catch (error) {
        console.error('Error loading metadata statistics:', error);
    }
}

// ============================================
// Audit Tab Functions
// ============================================

async function loadAuditDashboard() {
    try {
        const response = await fetch('/api/audit/dashboard');
        const data = await response.json();
        
        if (data.status === 'success') {
            const dashboard = data.dashboard;
            
            // Update overview cards
            document.getElementById('totalExecutions').textContent = 
                dashboard.overview.total_executions;
            document.getElementById('successfulExecutions').textContent = 
                dashboard.overview.successful_executions;
            document.getElementById('failedExecutions').textContent = 
                dashboard.overview.failed_executions;
            document.getElementById('successRate').textContent = 
                dashboard.overview.success_rate.toFixed(1) + '%';
            
            // Display top policies
            displayTopPolicies(dashboard.top_policies);
            
            // Display top tables
            displayTopTables(dashboard.top_tables);
            
            // Display recent executions
            displayRecentActivity(dashboard.recent_executions);
        }
    } catch (error) {
        console.error('Error loading audit dashboard:', error);
    }
}

function displayTopPolicies(policies) {
    const tbody = document.getElementById('topPoliciesBody');
    tbody.innerHTML = '';
    
    policies.forEach((policy, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${policy.policy_name}</strong></td>
            <td>${policy.total_executions}</td>
            <td class="success-text">${policy.successful_executions}</td>
            <td class="error-text">${policy.failed_executions}</td>
            <td>${policy.total_rows_affected.toLocaleString()}</td>
            <td>${Object.keys(policy.tables_affected || {}).length}</td>
            <td>${new Date(policy.last_executed).toLocaleString()}</td>
        `;
        tbody.appendChild(row);
    });
}

function displayTopTables(tables) {
    const tbody = document.getElementById('topTablesBody');
    tbody.innerHTML = '';
    
    tables.forEach((table, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${table.table_name}</strong></td>
            <td>${table.execution_count}</td>
            <td>${table.rows_affected.toLocaleString()}</td>
            <td>${table.policies.join(', ')}</td>
            <td>${table.policy_count}</td>
        `;
        tbody.appendChild(row);
    });
}

async function loadAuditLog() {
    try {
        const policyName = document.getElementById('auditPolicyFilter').value;
        const tableName = document.getElementById('auditTableFilter').value;
        const status = document.getElementById('auditStatusFilter').value;
        
        const params = new URLSearchParams();
        if (policyName) params.append('policy_name', policyName);
        if (tableName) params.append('target_table', tableName);
        if (status) params.append('status', status);
        params.append('limit', '100');
        
        const response = await fetch(`/api/audit/log?${params}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            displayAuditLog(data.audit_entries);
        }
    } catch (error) {
        console.error('Error loading audit log:', error);
    }
}

function displayAuditLog(entries) {
    const tbody = document.getElementById('auditLogBody');
    tbody.innerHTML = '';
    
    entries.forEach(entry => {
        const row = document.createElement('tr');
        const statusClass = entry.execution_status === 'SUCCESS' ? 'success' : 'error';
        
        row.innerHTML = `
            <td>${new Date(entry.timestamp).toLocaleString()}</td>
            <td><strong>${entry.policy_name}</strong></td>
            <td>${entry.target_table}</td>
            <td>${entry.target_columns.join(', ')}</td>
            <td><span class="status-badge ${statusClass}">${entry.execution_status}</span></td>
            <td>${entry.rows_affected.toLocaleString()}</td>
            <td>${entry.execution_time.toFixed(2)}s</td>
            <td>${entry.user}</td>
            <td>${entry.error_message || '-'}</td>
        `;
        tbody.appendChild(row);
    });
}

function displayRecentActivity(executions) {
    const timeline = document.getElementById('recentActivityTimeline');
    timeline.innerHTML = '';
    
    executions.forEach(exec => {
        const item = document.createElement('div');
        item.className = `timeline-item ${exec.execution_status.toLowerCase()}`;
        item.innerHTML = `
            <div class="timeline-time">${new Date(exec.timestamp).toLocaleTimeString()}</div>
            <div class="timeline-content">
                <strong>${exec.policy_name}</strong> on <code>${exec.target_table}</code>
                <br>
                <span class="status-badge ${exec.execution_status.toLowerCase()}">${exec.execution_status}</span>
                ${exec.rows_affected} rows • ${exec.execution_time.toFixed(2)}s
            </div>
        `;
        timeline.appendChild(item);
    });
}

// ============================================
// Tab Management
// ============================================

function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    if (tabName === 'metadata') {
        document.getElementById('metadataTab').style.display = 'block';
        loadPolicyChanges();
        loadLineageData();
        loadMetadataStatistics();
    } else if (tabName === 'audit') {
        document.getElementById('auditTab').style.display = 'block';
        loadAuditDashboard();
        loadAuditLog();
    } else {
        // Show governance tab (default)
        document.getElementById('governanceTab').style.display = 'block';
    }
    
    // Set active button
    event.target.classList.add('active');
}

// ============================================
// Auto-refresh
// ============================================

// Refresh data every 30 seconds
setInterval(() => {
    const activeTab = document.querySelector('.tab-content[style*="display: block"]');
    if (activeTab && activeTab.id === 'metadataTab') {
        loadMetadataStatistics();
    } else if (activeTab && activeTab.id === 'auditTab') {
        loadAuditDashboard();
    }
}, 30000);
```

---

## 5. Additional CSS Styles

Add these styles for the new components:

```css
/* Tabs */
.dashboard-tabs {
    display: flex;
    gap: 10px;
    padding: 20px;
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    border-bottom: 3px solid #3498db;
}

.tab-button {
    background: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    border: 2px solid transparent;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 600;
}

.tab-button:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: #3498db;
}

.tab-button.active {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    border-color: #3498db;
}

/* Data Tables */
.data-table-container {
    overflow-x: auto;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin: 20px 0;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}

.data-table thead {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    color: #ffffff;
}

.data-table th {
    padding: 15px;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid #3498db;
}

.data-table td {
    padding: 12px 15px;
    border-bottom: 1px solid #ecf0f1;
}

.data-table tbody tr:hover {
    background: #f8f9fa;
}

/* Filters Bar */
.filters-bar {
    display: flex;
    gap: 15px;
    margin: 20px 0;
    padding: 15px;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 10px;
}

.filters-bar input,
.filters-bar select {
    padding: 10px 15px;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    font-size: 0.9rem;
}

.filters-bar button {
    padding: 10px 20px;
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
}

/* Badges */
.badge {
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
}

.badge.create { background: #27ae60; color: #ffffff; }
.badge.update { background: #f39c12; color: #ffffff; }
.badge.delete { background: #e74c3c; color: #ffffff; }
.badge.apply { background: #3498db; color: #ffffff; }
.badge.dataflow { background: #9b59b6; color: #ffffff; }
.badge.process { background: #16a085; color: #ffffff; }
.badge.policy { background: #e67e22; color: #ffffff; }

.status-badge.success { background: #d5f4e6; color: #27ae60; }
.status-badge.failed, .status-badge.error { background: #fadbd8; color: #e74c3c; }
.status-badge.completed { background: #d5f4e6; color: #27ae60; }

/* Overview Cards */
.audit-overview {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.overview-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    gap: 20px;
    border-left: 5px solid #3498db;
}

.overview-card.success { border-left-color: #27ae60; }
.overview-card.failed { border-left-color: #e74c3c; }
.overview-card.rate { border-left-color: #f39c12; }

.overview-icon {
    font-size: 2.5rem;
}

.overview-content h3 {
    font-size: 2rem;
    margin: 0;
    color: #2c3e50;
}

.overview-content p {
    margin: 5px 0 0 0;
    color: #7f8c8d;
}

/* Timeline */
.timeline-container {
    max-height: 500px;
    overflow-y: auto;
    padding: 20px;
}

.timeline-item {
    display: flex;
    gap: 20px;
    padding: 15px;
    margin: 10px 0;
    background: #ffffff;
    border-radius: 8px;
    border-left: 4px solid #3498db;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.timeline-item.success { border-left-color: #27ae60; }
.timeline-item.failed { border-left-color: #e74c3c; }

.timeline-time {
    color: #7f8c8d;
    font-weight: 600;
    min-width: 100px;
}

.timeline-content {
    flex: 1;
}

/* Statistics Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin: 30px 0;
}

.stat-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    border-top: 4px solid #3498db;
}

.stat-card h3 {
    color: #7f8c8d;
    font-size: 0.9rem;
    margin: 0 0 10px 0;
}

.stat-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #2c3e50;
}

/* Section Headers */
.audit-section, .metadata-section {
    margin: 30px 0;
    padding: 20px;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 15px;
}

.audit-section h2, .metadata-section h2 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 1.5rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
```

---

## 6. Quick Commands to Test

Add these quick command buttons to the main dashboard:

```html
<span class="quick-cmd" onclick="showTab('metadata')">
    📊 View Metadata
</span>
<span class="quick-cmd" onclick="showTab('audit')">
    📋 View Audit Logs
</span>
```

---

## 7. Summary of Changes

### Files Created:
1. ✅ `atlan_metadata_store.py` - Stores policy changes and lineage in JSON
2. ✅ `policy_audit_tracker.py` - Tracks policy execution audit logs in JSON
3. ✅ Both modules store data in organized folder structure (`atlan_metadata/`, `policy_audits/`)

### API Endpoints Added:
1. `/api/metadata/policy-changes` - Get policy changes
2. `/api/metadata/lineage` - Get lineage entries
3. `/api/metadata/statistics` - Get metadata statistics
4. `/api/audit/log` - Get audit log
5. `/api/audit/statistics` - Get audit statistics
6. `/api/audit/dashboard` - Get dashboard summary
7. `/api/audit/table-summary/<table>` - Get table-specific audit
8. `/api/audit/top-policies` - Get top policies
9. `/api/audit/top-tables` - Get top tables

### UI Components:
1. **Metadata Tab** - Displays policy changes and lineage from Atlan
2. **Audit Tab** - Displays policy execution logs and statistics
3. **Interactive Tables** - Sortable, filterable data tables
4. **Statistics Cards** - Overview metrics
5. **Timeline View** - Recent activity visualization

---

## 8. Implementation Steps

1. **Backend**: API endpoints already added to `atlan_api_server.py`
2. **Frontend**: Add the HTML sections to the dashboard template
3. **JavaScript**: Add the data loading functions
4. **CSS**: Add the styling for new components
5. **Testing**: Test with sample data using the demo scripts

---

## 9. Sample Data Generation

To populate with test data, run:

```python
# Generate sample metadata
python atlan_metadata_store.py

# Generate sample audit logs
python policy_audit_tracker.py
```

This will create JSON files with sample data that can be viewed in the UI!
