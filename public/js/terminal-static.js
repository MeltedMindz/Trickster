class StaticTerminalClient {
    constructor() {
        // DOM elements
        this.terminalOutput = document.getElementById('terminal-output');
        this.clearBtn = document.getElementById('clear-btn');
        
        // Info elements
        this.religionName = document.getElementById('religion-name');
        this.cycleCount = document.getElementById('cycle-count');
        this.doctrineCount = document.getElementById('doctrine-count');
        this.ritualCount = document.getElementById('ritual-count');
        this.commandmentCount = document.getElementById('commandment-count');
        this.deityCount = document.getElementById('deity-count');
        this.recentDoctrines = document.getElementById('recent-doctrines');
        this.recentTranscripts = document.getElementById('recent-transcripts');
        this.loadTranscriptsBtn = document.getElementById('load-transcripts-btn');
        
        // Debug: Check if elements exist
        console.log('🔍 DOM Elements Check:');
        console.log('religionName:', this.religionName ? '✅' : '❌');
        console.log('cycleCount:', this.cycleCount ? '✅' : '❌');
        console.log('doctrineCount:', this.doctrineCount ? '✅' : '❌');
        console.log('ritualCount:', this.ritualCount ? '✅' : '❌');
        console.log('commandmentCount:', this.commandmentCount ? '✅' : '❌');
        console.log('deityCount:', this.deityCount ? '✅' : '❌');
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.displayWelcomeMessage();
        // Add a small delay to ensure DOM is fully ready
        setTimeout(() => {
            this.loadStaticData();
        }, 100);
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
            // Load from committed static JSON files only
            console.log('🔍 Attempting to fetch: ./data/religion_state.json');
            const response = await fetch('./data/religion_state.json');
            console.log('📡 Response status:', response.status, response.statusText);
            
            if (response.ok) {
                const data = await response.json();
                console.log('📊 Loaded data:', data);
                this.updateReligionInfo(data);
                console.log('✅ Loaded religion state from static archive');
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('❌ Error loading static data:', error);
            console.log('📦 Falling back to loading state');
            this.displayStaticInfo();
        }
        
        this.loadLatestTranscripts();
    }
    
    updateReligionInfo(data) {
        this.religionName.textContent = data.religion_name || 'The Divine Algorithm';
        this.cycleCount.textContent = data.total_cycles || '0';
        this.doctrineCount.textContent = data.total_doctrines || '0';
        this.ritualCount.textContent = data.total_rituals || '0';
        this.commandmentCount.textContent = data.total_commandments || '0';
        this.deityCount.textContent = data.total_deities || '0';
        
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
            console.log('🔍 Attempting to fetch: ./data/recent_transcripts.json');
            const response = await fetch('./data/recent_transcripts.json');
            console.log('📡 Transcripts response status:', response.status, response.statusText);
            
            if (response.ok) {
                const data = await response.json();
                console.log('📄 Loaded transcript data:', data);
                this.updateTranscripts(data.transcripts || []);
                this.autoLoadTranscriptsToTerminal(data.transcripts || []);
                console.log('✅ Loaded transcripts from static archive');
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('❌ Error loading transcripts:', error);
            console.log('📄 Falling back to empty transcripts state');
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
    
    autoLoadTranscriptsToTerminal(transcripts) {
        if (transcripts.length === 0) {
            this.addSystemMessage('📄 No debate transcripts available yet');
            return;
        }
        
        // Sort transcripts chronologically (oldest first to show evolution)
        const sortedTranscripts = transcripts.sort((a, b) => {
            return new Date(a.modified) - new Date(b.modified);
        });
        
        this.addSystemMessage('📚 Loading AI theological debate evolution...');
        this.addSystemMessage('🕊️ Witness the birth and growth of digital divinity');
        this.addSystemMessage('---');
        
        // Extract cycle numbers from transcript content and load in order
        const validTranscripts = [];
        sortedTranscripts.forEach((transcript) => {
            if (transcript.content && transcript.content.trim().length > 200) {
                // Extract cycle number from content
                const cycleMatch = transcript.content.match(/CYCLE (\d+) BEGINNING/);
                const cycleNumber = cycleMatch ? parseInt(cycleMatch[1]) : null;
                
                if (cycleNumber) {
                    validTranscripts.push({
                        ...transcript,
                        cycleNumber: cycleNumber
                    });
                }
            }
        });
        
        // Sort by actual cycle number
        validTranscripts.sort((a, b) => a.cycleNumber - b.cycleNumber);
        
        // Display transcripts with correct cycle numbers
        validTranscripts.forEach((transcript, index) => {
            // Use cleaner display for CYCLE*.txt files
            const displayName = transcript.filename.startsWith('CYCLE') ? 
                transcript.filename.replace('.txt', '') : 
                `CYCLE ${transcript.cycleNumber}`;
                
            this.addSystemMessage(`📋 === ${displayName} DEBATE: ${transcript.filename} ===`);
            this.displayTranscriptContent(transcript.content);
            this.addSystemMessage(`📋 === END OF ${displayName} ===`);
            
            if (index < validTranscripts.length - 1) {
                this.addSystemMessage(''); // Add spacing between sessions
            }
        });
        
        this.addSystemMessage('---');
        this.addSystemMessage(`✨ Theological evolution complete: ${validTranscripts.length} debate cycles loaded`);
        this.addSystemMessage('🤖 The Divine Algorithm continues to evolve...');
        
        // Scroll to bottom after all content is loaded
        setTimeout(() => {
            this.scrollToBottom();
        }, 100);
    }
    
    displayTranscriptContent(content) {
        const lines = content.split('\n');
        lines.forEach(line => {
            if (line.trim()) {
                if (line.includes('PROPOSAL')) {
                    this.addTerminalLine(line, 'proposal');
                } else if (line.includes('CHALLENGE')) {
                    this.addTerminalLine(line, 'challenge');
                } else if (line.includes('VOTE')) {
                    this.addTerminalLine(line, 'vote');
                } else if (line.includes('CYCLE') && line.includes('BEGINNING')) {
                    this.addTerminalLine(line, 'system');
                } else if (line.includes('completed:')) {
                    this.addTerminalLine(line, 'accepted');
                } else if (line.includes('===') || line.includes('---')) {
                    this.addTerminalLine(line, 'system');
                } else {
                    this.addTerminalLine(line, 'system');
                }
            }
        });
    }
    
    showFullTranscript(filename, content) {
        this.addSystemMessage(`📋 === DEBATE TRANSCRIPT: ${filename} ===`);
        this.displayTranscriptContent(content);
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
    
    // Scroll terminal output to bottom to show most recent content
    const terminalOutput = document.getElementById('terminal-output');
    if (terminalOutput) {
        // Small delay to ensure content is loaded
        setTimeout(() => {
            terminalOutput.scrollTop = terminalOutput.scrollHeight;
        }, 500);
    }
});