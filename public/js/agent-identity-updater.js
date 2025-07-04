/**
 * Agent Identity Display Updater
 * Updates the main interface to show chosen agent names instead of role names
 */

class AgentIdentityUpdater {
    constructor() {
        this.memoryData = null;
        this.identityMap = new Map(); // Maps role names to chosen names
        this.init();
    }

    async init() {
        await this.loadMemoryData();
        this.updateAgentDisplayNames();
        
        // Auto-refresh every 30 seconds
        setInterval(async () => {
            await this.loadMemoryData();
            this.updateAgentDisplayNames();
        }, 30000);
    }

    async loadMemoryData() {
        try {
            const response = await fetch('/data/agent_memories.json');
            if (response.ok) {
                this.memoryData = await response.json();
                this.buildIdentityMap();
            }
        } catch (error) {
            console.error('Failed to load agent memory data:', error);
        }
    }

    buildIdentityMap() {
        if (!this.memoryData || !this.memoryData.agents) return;

        // Build mapping from role names to chosen names
        this.identityMap.clear();
        
        for (const [roleName, agentData] of Object.entries(this.memoryData.agents)) {
            if (agentData.chosen_name) {
                this.identityMap.set(roleName, agentData.chosen_name);
            }
        }
    }

    updateAgentDisplayNames() {
        // Update agent names in the sidebar
        const agentItems = document.querySelectorAll('.agent-item');
        
        agentItems.forEach(item => {
            const agentNameElement = item.querySelector('.agent-name');
            if (agentNameElement) {
                const roleName = this.getRoleNameFromClasses(item);
                const chosenName = this.identityMap.get(roleName);
                
                if (chosenName) {
                    // Store original role name for data lookup
                    agentNameElement.setAttribute('data-role-name', roleName);
                    // Update display text to chosen name
                    agentNameElement.textContent = chosenName;
                    
                    // Update tooltip
                    const tooltip = `Click to view ${chosenName}'s memory profile (formerly ${roleName})`;
                    item.setAttribute('title', tooltip);
                }
            }
        });
    }

    getRoleNameFromClasses(element) {
        // Extract role name from CSS classes
        if (element.classList.contains('zealot')) return 'Zealot';
        if (element.classList.contains('skeptic')) return 'Skeptic';
        if (element.classList.contains('trickster')) return 'Trickster';
        return null;
    }

    // Method to get the role name for data lookup (used by other components)
    getRoleNameForLookup(displayElement) {
        return displayElement.getAttribute('data-role-name') || displayElement.textContent.trim();
    }

    // Method to get chosen name from role name
    getChosenName(roleName) {
        return this.identityMap.get(roleName) || roleName;
    }

    // Method to get role name from chosen name (reverse lookup)
    getRoleFromChosenName(chosenName) {
        for (const [role, chosen] of this.identityMap.entries()) {
            if (chosen === chosenName) return role;
        }
        return chosenName; // fallback to original name
    }
}

// Initialize the identity updater when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.agentIdentityUpdater = new AgentIdentityUpdater();
});

// Export for use by other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AgentIdentityUpdater;
}