class TerminalClient {
    constructor() {
        this.ws = null;
        this.reconnectInterval = 5000;
        this.shouldReconnect = true;
        this.isPaused = false;
        
        // DOM elements
        this.terminalOutput = document.getElementById('terminal-output');
        this.connectionStatus = document.getElementById('connection-status');
        this.pauseBtn = document.getElementById('pause-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.promptInput = document.getElementById('prompt-input');
        this.sendPromptBtn = document.getElementById('send-prompt');
        
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
        this.connect();
        this.setupEventListeners();
        this.startPingInterval();
        this.loadTranscripts();
    }
    
    connect() {
        const wsUrl = window.AI_RELIGION_CONFIG?.WS_URL || 'ws://localhost:8000/ws';
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.updateConnectionStatus(true);
                this.addSystemMessage('Connected to AI Religion Architects server');
            };
            
            this.ws.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };
            
            this.ws.onclose = () => {
                this.updateConnectionStatus(false);
                this.addSystemMessage('Disconnected from server');
                
                if (this.shouldReconnect) {
                    setTimeout(() => this.connect(), this.reconnectInterval);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.addSystemMessage('Connection error occurred', 'error');
            };
            
        } catch (error) {
            console.error('Failed to connect:', error);
            this.addSystemMessage('Failed to establish connection', 'error');
        }
    }
    
    handleMessage(message) {
        switch (message.type) {
            case 'initial_state':
                this.updateFullState(message.data);
                break;
                
            case 'new_debate':
                this.addDebateEntry(message.data);
                break;
                
            case 'state_update':
                this.updateFullState(message.data);
                break;
                
            case 'cycle_update':
                this.addCycleUpdate(message.data);
                break;
                
            case 'control':
                this.handleControlMessage(message);
                break;
                
            case 'external_prompt':
                this.addSystemMessage(`External prompt injected: ${message.content}`, 'prompt');
                break;
                
            default:
                console.log('Unknown message type:', message.type);
        }
    }
    
    updateFullState(state) {
        // Update religion info
        this.religionName.textContent = state.religion_name || 'Awaiting genesis...';
        this.cycleCount.textContent = state.statistics?.total_debates || '0';
        this.doctrineCount.textContent = state.statistics?.total_doctrines || '0';
        this.deityCount.textContent = state.deities?.length || '0';
        
        // Update recent doctrines
        this.updateRecentDoctrines(state.doctrines || []);
    }
    
    updateRecentDoctrines(doctrines) {
        if (doctrines.length === 0) {
            this.recentDoctrines.innerHTML = '<div class="empty-state">No doctrines yet...</div>';
            return;
        }
        
        this.recentDoctrines.innerHTML = doctrines.map(doctrine => `
            <div class="doctrine-item">
                ${doctrine.content}
                <div style="font-size: 10px; color: #666; margin-top: 4px;">
                    - ${doctrine.proposed_by}
                </div>
            </div>
        `).join('');
    }
    
    addDebateEntry(debate) {
        const timestamp = this.getTimestamp();
        
        // Add proposal
        this.addTerminalLine(
            `PROPOSAL by ${debate.proposer}: ${debate.proposal_content}`,
            'proposal',
            timestamp
        );
        
        // Add challenger response
        if (debate.challenger_response) {
            this.addTerminalLine(
                `CHALLENGE: ${debate.challenger_response}`,
                'challenge',
                timestamp
            );
        }
        
        // Add trickster response
        if (debate.trickster_response) {
            this.addTerminalLine(
                `🎲 TRICKSTER: ${debate.trickster_response}`,
                'chaos',
                timestamp
            );
        }
        
        // Add outcome
        const outcomeClass = debate.final_outcome === 'accept' ? 'accepted' : 'rejected';
        this.addTerminalLine(
            `OUTCOME: ${debate.final_outcome.toUpperCase()}`,
            outcomeClass,
            timestamp
        );
    }
    
    addCycleUpdate(data) {
        const timestamp = this.getTimestamp();
        this.addTerminalLine(
            `=== CYCLE ${data.cycle_number} ===`,
            'system',
            timestamp
        );
    }
    
    addTerminalLine(content, className = '', timestamp = null) {
        if (this.isPaused) return;
        
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
    
    addSystemMessage(message, type = 'system') {
        this.addTerminalLine(message, type, this.getTimestamp());
    }
    
    updateConnectionStatus(connected) {
        const statusDot = this.connectionStatus.querySelector('.status-dot');
        const statusText = this.connectionStatus.querySelector('.status-text');
        
        if (connected) {
            statusDot.classList.add('connected');
            statusText.textContent = 'Connected';
        } else {
            statusDot.classList.remove('connected');
            statusText.textContent = 'Disconnected';
        }
    }
    
    setupEventListeners() {
        // Pause/Resume button
        this.pauseBtn.addEventListener('click', () => {
            this.isPaused = !this.isPaused;
            this.pauseBtn.textContent = this.isPaused ? '▶ Resume' : '⏸ Pause';
            this.pauseBtn.classList.toggle('paused', this.isPaused);
            
            // Send pause/resume command to server
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                const apiUrl = window.AI_RELIGION_CONFIG?.API_URL || 'http://localhost:8000/api';
                fetch(`${apiUrl}/orchestrator/${this.isPaused ? 'pause' : 'resume'}`, {
                    method: 'POST'
                });
            }
        });
        
        // Clear button
        this.clearBtn.addEventListener('click', () => {
            this.terminalOutput.innerHTML = '';
            this.addSystemMessage('Terminal cleared');
        });
        
        // Prompt input
        const sendPrompt = () => {
            const prompt = this.promptInput.value.trim();
            if (prompt && this.ws && this.ws.readyState === WebSocket.OPEN) {
                const apiUrl = window.AI_RELIGION_CONFIG?.API_URL || 'http://localhost:8000/api';
                fetch(`${apiUrl}/prompt`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ content: prompt })
                });
                
                this.promptInput.value = '';
                this.addSystemMessage(`> ${prompt}`, 'prompt');
            }
        };
        
        this.sendPromptBtn.addEventListener('click', sendPrompt);
        this.promptInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendPrompt();
            }
        });
        
        // Load transcripts button
        this.loadTranscriptsBtn.addEventListener('click', () => {
            this.loadTranscripts();
        });
    }
    
    async loadTranscripts() {
        try {
            const apiUrl = window.AI_RELIGION_CONFIG?.API_URL || 'http://localhost:8000/api';
            const response = await fetch(`${apiUrl}/transcripts?limit=3`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.updateTranscripts(data.transcripts || []);
        } catch (error) {
            console.error('Failed to load transcripts:', error);
            this.recentTranscripts.innerHTML = '<div class="empty-state">Failed to load transcripts</div>';
        }
    }
    
    updateTranscripts(transcripts) {
        if (transcripts.length === 0) {
            this.recentTranscripts.innerHTML = '<div class="empty-state">No transcripts available</div>';
            return;
        }
        
        this.recentTranscripts.innerHTML = transcripts.map((transcript, index) => {
            const preview = transcript.content.substring(0, 80) + (transcript.content.length > 80 ? '...' : '');
            return `
                <div class="transcript-item" data-transcript-index="${index}">
                    <div class="timestamp">${transcript.timestamp}</div>
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
    }
    
    showFullTranscript(filename, content) {
        // Add full transcript to terminal
        this.addSystemMessage(`📋 Loading transcript: ${filename}`, 'system');
        const lines = content.split('\n');
        lines.forEach(line => {
            if (line.trim()) {
                this.addTerminalLine(line, 'system');
            }
        });
        this.addSystemMessage('📋 End of transcript', 'system');
    }
    
    startPingInterval() {
        setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send('ping');
            }
        }, 30000); // Ping every 30 seconds
    }
    
    scrollToBottom() {
        this.terminalOutput.scrollTop = this.terminalOutput.scrollHeight;
    }
    
    getTimestamp() {
        const now = new Date();
        return now.toTimeString().split(' ')[0];
    }
    
    handleControlMessage(message) {
        switch (message.action) {
            case 'paused':
                this.addSystemMessage('Orchestrator paused', 'system');
                break;
            case 'resumed':
                this.addSystemMessage('Orchestrator resumed', 'system');
                break;
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.terminalClient = new TerminalClient();
});