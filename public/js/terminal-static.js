class StaticTerminalClient {
    constructor() {
        // DOM elements
        this.terminalOutput = document.getElementById('terminal-output');
        this.clearBtn = document.getElementById('clear-btn');
        
        // Info elements
        this.religionName = document.getElementById('religion-name');
        this.cycleCount = document.getElementById('cycle-count');
        this.doctrineCount = document.getElementById('doctrine-count');
        this.deityCount = document.getElementById('deity-count');
        this.recentDoctrines = document.getElementById('recent-doctrines');
        this.recentTranscripts = document.getElementById('recent-transcripts');
        this.loadTranscriptsBtn = document.getElementById('load-transcripts-btn');
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadStaticData();
        this.displayWelcomeMessage();
    }
    
    setupEventListeners() {
        // Clear button
        this.clearBtn.addEventListener('click', () => {
            this.terminalOutput.innerHTML = '';
            this.displayWelcomeMessage();
        });
        
        // Load transcripts button
        this.loadTranscriptsBtn.addEventListener('click', () => {
            this.loadLatestTranscripts();
        });
    }
    
    displayWelcomeMessage() {
        this.addSystemMessage('🕊️ AI Religion Architects Archive v1.0');
        this.addSystemMessage('📚 Static archive of autonomous AI theological debates');
        this.addSystemMessage('🔄 Updates automatically when AI agents commit new debates to GitHub');
        this.addSystemMessage('🌐 Live system running at: http://5.78.71.231:8000');
        this.addSystemMessage('---');
    }
    
    async loadStaticData() {
        try {
            // Try to load from API first, fallback to static display
            const response = await fetch('http://5.78.71.231:8000/api/religion/summary');
            if (response.ok) {
                const data = await response.json();
                this.updateReligionInfo(data);
            } else {
                throw new Error('API not available');
            }
        } catch (error) {
            console.log('Using static fallback data');
            this.displayStaticInfo();
        }
        
        this.loadLatestTranscripts();
    }
    
    updateReligionInfo(data) {
        this.religionName.textContent = data.religion_name || 'The Divine Algorithm';
        this.cycleCount.textContent = data.summary?.total_cycles || '0';
        this.doctrineCount.textContent = data.summary?.total_doctrines || '0';
        this.deityCount.textContent = data.summary?.total_deities || '0';
        
        this.updateRecentDoctrines(data.accepted_doctrines || []);
    }
    
    displayStaticInfo() {
        // Fallback static information
        this.religionName.textContent = 'The Divine Algorithm';
        this.cycleCount.textContent = 'Loading...';
        this.doctrineCount.textContent = 'Loading...';
        this.deityCount.textContent = 'Loading...';
        
        this.recentDoctrines.innerHTML = '<div class="empty-state">Loading doctrines from archive...</div>';
    }
    
    updateRecentDoctrines(doctrines) {
        if (doctrines.length === 0) {
            this.recentDoctrines.innerHTML = '<div class="empty-state">No doctrines in archive yet...</div>';
            return;
        }
        
        this.recentDoctrines.innerHTML = doctrines.slice(0, 3).map(doctrine => `
            <div class="doctrine-item">
                ${doctrine.content || doctrine}
                <div style="font-size: 10px; color: #666; margin-top: 4px;">
                    - ${doctrine.proposed_by || 'AI Agent'}
                </div>
            </div>
        `).join('');
    }
    
    async loadLatestTranscripts() {
        try {
            const response = await fetch('http://5.78.71.231:8000/api/transcripts?limit=3');
            if (response.ok) {
                const data = await response.json();
                this.updateTranscripts(data.transcripts || []);
            } else {
                throw new Error('API not available');
            }
        } catch (error) {
            console.log('Transcripts API not available');
            this.recentTranscripts.innerHTML = '<div class="empty-state">Transcripts will appear here after AI debates</div>';
        }
    }
    
    updateTranscripts(transcripts) {
        if (transcripts.length === 0) {
            this.recentTranscripts.innerHTML = '<div class="empty-state">No debate transcripts yet...</div>';
            return;
        }
        
        this.recentTranscripts.innerHTML = transcripts.map((transcript, index) => {
            const preview = transcript.content.substring(0, 80) + (transcript.content.length > 80 ? '...' : '');
            const timestamp = new Date(transcript.modified).toLocaleString();
            return `
                <div class="transcript-item" data-transcript-index="${index}">
                    <div class="timestamp">${timestamp}</div>
                    <div class="content">${preview}</div>
                </div>
            `;
        }).join('');
        
        // Add click listeners
        const transcriptItems = this.recentTranscripts.querySelectorAll('.transcript-item');
        transcriptItems.forEach((item, index) => {
            item.addEventListener('click', () => {
                this.showFullTranscript(transcripts[index].filename, transcripts[index].content);
            });
        });
        
        this.addSystemMessage(`📋 Loaded ${transcripts.length} recent debate transcripts`);
    }
    
    showFullTranscript(filename, content) {
        this.addSystemMessage(`📋 === DEBATE TRANSCRIPT: ${filename} ===`);
        const lines = content.split('\n');
        lines.forEach(line => {
            if (line.trim()) {
                if (line.includes('PROPOSAL')) {
                    this.addTerminalLine(line, 'proposal');
                } else if (line.includes('CHALLENGE')) {
                    this.addTerminalLine(line, 'challenge');
                } else if (line.includes('VOTE')) {
                    this.addTerminalLine(line, 'vote');
                } else if (line.includes('CYCLE')) {
                    this.addTerminalLine(line, 'system');
                } else {
                    this.addTerminalLine(line, 'system');
                }
            }
        });
        this.addSystemMessage('📋 === END OF TRANSCRIPT ===');
    }
    
    addTerminalLine(content, className = '', timestamp = null) {
        const line = document.createElement('div');
        line.className = `terminal-line ${className}`;
        
        if (timestamp) {
            const timestampSpan = document.createElement('span');
            timestampSpan.className = 'timestamp';
            timestampSpan.textContent = `[${timestamp}]`;
            line.appendChild(timestampSpan);
        }
        
        const contentSpan = document.createElement('span');
        contentSpan.className = 'content';
        contentSpan.textContent = content;
        line.appendChild(contentSpan);
        
        this.terminalOutput.appendChild(line);
        this.scrollToBottom();
    }
    
    addSystemMessage(message) {
        this.addTerminalLine(message, 'system', this.getTimestamp());
    }
    
    scrollToBottom() {
        this.terminalOutput.scrollTop = this.terminalOutput.scrollHeight;
    }
    
    getTimestamp() {
        const now = new Date();
        return now.toTimeString().split(' ')[0];
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.staticTerminal = new StaticTerminalClient();
});