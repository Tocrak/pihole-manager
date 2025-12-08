class ThemeManager {
    static TOGGLE_ID = 'theme-toggle';
    static TEXT_ID = 'toggle-text';

    constructor() {
        this._root = document.documentElement;
        this._toggleButton = document.getElementById(ThemeManager.TOGGLE_ID);
        this._toggleText = document.getElementById(ThemeManager.TEXT_ID);
        this.init();
    }

    _updateDisplay(theme) {
        if (this._toggleText) {
            this._toggleText.textContent = (theme === 'dark') ? 'Light Mode' : 'Dark Mode';
        }
    }

    _toggleTheme() {
        const currentTheme = this._root.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        this._root.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        this._updateDisplay(newTheme);
    }

    init() {
        const initialTheme = localStorage.getItem('theme') || 
                             (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

        this._root.setAttribute('data-theme', initialTheme);
        this._updateDisplay(initialTheme);

        if (this._toggleButton) {
            this._toggleButton.addEventListener('click', this._toggleTheme.bind(this));
        } else {
            console.warn(`Theme toggle button (ID: ${ThemeManager.TOGGLE_ID}) not found.`);
        }
    }
}

class ClientTableManager {
    static TABLE_BODY_SELECTOR = 'tbody';
    static REFRESH_INTERVAL = 5000;
    static ENDPOINTS = {
        CLIENTS: "/clients",
        GROUP_IDS: "/group-ids",
        EDIT_CLIENT: "/editclient"
    };

    constructor() {
        this._tableBody = document.querySelector(ClientTableManager.TABLE_BODY_SELECTOR);
        this._ADBLOCK_GROUP_ID = null;
        this._NON_ADBLOCK_GROUP_ID = null;
        this._intervalId = null;

        if (this._tableBody) {
            this._tableBody.addEventListener('click', this._handleTableClick.bind(this));
        } else {
            console.error(`Table body element (${ClientTableManager.TABLE_BODY_SELECTOR}) not found. Auto-refresh aborted.`);
        }
    }

    async _fetch(url) {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status} for ${url}`);
        }
        return url.endsWith('/clients') ? response.text() : response.json();
    }

    async _fetchClientData() {
        try {
            const contents = await this._fetch(ClientTableManager.ENDPOINTS.CLIENTS);
            return JSON.parse(contents);
        } catch (e) {
            console.error('Error fetching client data: ', e);
            return [];
        }
    }

    async _fetchGroupIds() {
        try {
            const data = await this._fetch(ClientTableManager.ENDPOINTS.GROUP_IDS);
            this._ADBLOCK_GROUP_ID = data.adblock_group_id;
            this._NON_ADBLOCK_GROUP_ID = data.non_adblock_group_id;
        } catch (e) {
            console.error('Error fetching group IDs, client functionality will use defaults: ', e);
            this._ADBLOCK_GROUP_ID = 0; 
            this._NON_ADBLOCK_GROUP_ID = 1;
        }
    }

    async _editClient(client, comment, group) {
        const payload = { client, comment, group };
        try {
            const response = await fetch(ClientTableManager.ENDPOINTS.EDIT_CLIENT, {
                method: "POST",
                headers: { 'content-type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`Failed to update client status: ${response.status}`);
            }
            this.refreshTable();
        } catch (error) {
            console.error("Error updating client status:", error);
        }
    }

    _handleTableClick(event) {
        const button = event.target.closest('.status-button');
        if (!button) {
            return;
        }

        const { client, comment, newGroup } = button.dataset;
        this._editClient(client, comment, parseInt(newGroup));
    }

    _createTableFromJSON(clientList) {
        if (!this._tableBody) {
            return;
        }
        
        const fragment = document.createDocumentFragment();
        this._tableBody.innerHTML = ""; 

        clientList.forEach(clientData => {
            const groups = clientData.groups || [];
            const isEnabled = groups.includes(this._ADBLOCK_GROUP_ID);
            const newGroup = isEnabled ? this._NON_ADBLOCK_GROUP_ID : this._ADBLOCK_GROUP_ID;
            
            const row = document.createElement("tr");

            ['client', 'comment'].forEach(key => {
                const cell = document.createElement("td");
                cell.textContent = clientData[key];
                row.appendChild(cell);
            });

            const statusCell = document.createElement("td");
            statusCell.classList.add("center-content");

            const statusText = isEnabled ? 'Enabled' : 'Disabled';
            const statusClass = isEnabled ? 'enabled' : 'disabled';
            const icon = isEnabled ? '✓' : '✖';
            
            const button = document.createElement("button");
            button.innerHTML = `<span class="icon">${icon}</span> ${statusText}`;
            button.classList.add('status-button', statusClass);
            
            button.dataset.client = clientData.client;
            button.dataset.comment = clientData.comment;
            button.dataset.newGroup = newGroup;

            statusCell.appendChild(button);
            row.appendChild(statusCell);
            fragment.appendChild(row);
        });

        this._tableBody.appendChild(fragment);
    }

    async refreshTable() {
        const clientList = await this._fetchClientData();
        this._createTableFromJSON(clientList);
    }

    async init() {
        await this._fetchGroupIds(); 
        this.refreshTable(); 
        
        if (this._tableBody) {
            this._intervalId = setInterval(() => this.refreshTable(), ClientTableManager.REFRESH_INTERVAL);
            console.log(`Client table auto-refresh started every ${ClientTableManager.REFRESH_INTERVAL}ms.`);
        }
    }
}

class DashboardApp {
    constructor() {
        this.themeManager = new ThemeManager();
        this.clientManager = new ClientTableManager();
    }
    
    async init() {
        await this.clientManager.init();
        console.log("Dashboard Application Initialized.");
    }
}

window.onload = () => {
    const app = new DashboardApp();
    app.init();
};