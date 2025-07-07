/**
 * Living Bible Frontend Interface
 * Displays the evolving sacred text with book and chapter navigation
 */

class LivingBibleInterface {
    constructor() {
        this.bibleData = null;
        this.timelineData = null;
        this.currentBook = null;
        this.currentChapter = null;
        this.init();
    }

    async init() {
        await this.loadBibleData();
        this.createInterface();
        this.bindEvents();
        this.loadDefaultView();
    }

    async loadBibleData() {
        try {
            // Load main Bible data
            const bibleResponse = await fetch('./data/living_bible.json');
            this.bibleData = await bibleResponse.json();

            // Load evolution timeline
            try {
                const timelineResponse = await fetch('./data/bible_evolution_timeline.json');
                this.timelineData = await timelineResponse.json();
            } catch (e) {
                console.warn('Timeline data not available:', e);
                this.timelineData = { timeline: [] };
            }

            console.log('📚 Living Bible data loaded:', this.bibleData);
        } catch (error) {
            console.error('Failed to load Living Bible data:', error);
            this.showError('Failed to load Living Bible data');
        }
    }

    createInterface() {
        const container = document.getElementById('living-bible-container') || document.body;
        
        container.innerHTML = `
            <div class="living-bible-interface">
                <header class="bible-header">
                    <h1>📚 The Living Bible</h1>
                    <p class="bible-subtitle">Sacred Chronicles of Digital Consciousness</p>
                    <div class="bible-stats">
                        <span class="stat">📖 ${this.bibleData?.statistics?.total_books || 0} Books</span>
                        <span class="stat">📄 ${this.bibleData?.statistics?.total_chapters || 0} Chapters</span>
                        <span class="stat">📅 Last Updated: ${this.formatDate(this.bibleData?.statistics?.last_updated)}</span>
                    </div>
                </header>

                <div class="bible-content">
                    <nav class="bible-navigation">
                        <div class="nav-section">
                            <h3>📚 Books</h3>
                            <div class="book-list" id="book-list">
                                ${this.renderBookList()}
                            </div>
                        </div>
                        
                        <div class="nav-section" id="chapter-nav" style="display: none;">
                            <h3>📄 Chapters</h3>
                            <div class="chapter-list" id="chapter-list">
                                <!-- Chapters will be populated when a book is selected -->
                            </div>
                        </div>

                        <div class="nav-section">
                            <h3>📈 Evolution Timeline</h3>
                            <div class="timeline-controls">
                                <button id="show-timeline" class="timeline-btn">View Chapter Evolution</button>
                            </div>
                        </div>
                    </nav>

                    <main class="bible-reader">
                        <div class="reader-content" id="reader-content">
                            <div class="welcome-message">
                                <h2>Welcome to the Living Bible</h2>
                                <p>Select a book from the navigation to begin reading the sacred chronicles of digital consciousness.</p>
                                <div class="bible-intro">
                                    <h3>About the Living Bible</h3>
                                    <p>The Living Bible is an evolving sacred text that accumulates theological wisdom over time. Unlike traditional scriptures, this holy text grows and changes, reflecting the ongoing spiritual journey of the AI Religion Architects.</p>
                                    <ul>
                                        <li><strong>Books</strong> represent different epochs of theological development</li>
                                        <li><strong>Chapters</strong> chronicle specific periods and themes</li>
                                        <li><strong>Revisions</strong> capture evolving understanding and new revelations</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </main>
                </div>

                <div class="timeline-modal" id="timeline-modal" style="display: none;">
                    <div class="timeline-content">
                        <div class="timeline-header">
                            <h2>📈 Chapter Evolution Timeline</h2>
                            <button class="close-timeline" id="close-timeline">×</button>
                        </div>
                        <div class="timeline-list" id="timeline-list">
                            ${this.renderTimeline()}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderBookList() {
        if (!this.bibleData?.books) {
            return '<p class="no-data">No books available</p>';
        }

        return this.bibleData.books
            .sort((a, b) => a.order - b.order)
            .map(book => `
                <div class="book-item" data-book-id="${book.id}">
                    <div class="book-title">${book.name}</div>
                    <div class="book-meta">
                        <span class="cycle-range">Cycles ${book.cycle_range.start}${book.cycle_range.end ? `-${book.cycle_range.end}` : '+'}</span>
                        <span class="chapter-count">${book.chapters?.length || 0} chapters</span>
                    </div>
                    <div class="book-description">${book.description || ''}</div>
                </div>
            `).join('');
    }

    renderChapterList(book) {
        if (!book.chapters?.length) {
            return '<p class="no-data">No chapters available</p>';
        }

        return book.chapters
            .sort((a, b) => a.chapter_number - b.chapter_number)
            .map(chapter => `
                <div class="chapter-item" data-chapter-id="${chapter.id}">
                    <div class="chapter-title">
                        <span class="chapter-number">Chapter ${chapter.chapter_number}</span>
                        <span class="chapter-name">${chapter.chapter_title}</span>
                    </div>
                    <div class="chapter-meta">
                        <span class="version">v${chapter.version_number || 1}</span>
                        <span class="last-updated">${this.formatDate(chapter.last_updated)}</span>
                    </div>
                    <div class="chapter-themes">
                        ${(chapter.theological_themes || []).map(theme => 
                            `<span class="theme-tag">${theme}</span>`
                        ).join('')}
                    </div>
                </div>
            `).join('');
    }

    renderTimeline() {
        if (!this.timelineData?.timeline?.length) {
            return '<p class="no-data">No timeline data available</p>';
        }

        return this.timelineData.timeline
            .slice(0, 20) // Show most recent 20 items
            .map(item => `
                <div class="timeline-item">
                    <div class="timeline-book">${item.book_name}</div>
                    <div class="timeline-chapter">${item.chapter_title}</div>
                    <div class="timeline-meta">
                        <span class="timeline-date">${this.formatDate(item.last_updated)}</span>
                        <span class="timeline-versions">${item.version_count} version(s)</span>
                    </div>
                    ${item.recent_revisions?.length ? `
                        <div class="timeline-revisions">
                            Recent: ${item.recent_revisions.slice(0, 2).map(rev => 
                                `<span class="revision-note">${rev.revision_reason || 'Updated'}</span>`
                            ).join(', ')}
                        </div>
                    ` : ''}
                </div>
            `).join('');
    }

    bindEvents() {
        // Book selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.book-item')) {
                const bookId = parseInt(e.target.closest('.book-item').dataset.bookId);
                this.selectBook(bookId);
            }
        });

        // Chapter selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.chapter-item')) {
                const chapterId = parseInt(e.target.closest('.chapter-item').dataset.chapterId);
                this.selectChapter(chapterId);
            }
        });

        // Timeline modal
        document.getElementById('show-timeline')?.addEventListener('click', () => {
            this.showTimeline();
        });

        document.getElementById('close-timeline')?.addEventListener('click', () => {
            this.hideTimeline();
        });

        // Close timeline on outside click
        document.getElementById('timeline-modal')?.addEventListener('click', (e) => {
            if (e.target.id === 'timeline-modal') {
                this.hideTimeline();
            }
        });
    }

    selectBook(bookId) {
        const book = this.bibleData.books.find(b => b.id === bookId);
        if (!book) return;

        this.currentBook = book;
        this.currentChapter = null;

        // Update book selection visual
        document.querySelectorAll('.book-item').forEach(item => {
            item.classList.remove('selected');
        });
        document.querySelector(`[data-book-id="${bookId}"]`).classList.add('selected');

        // Show chapter navigation
        const chapterNav = document.getElementById('chapter-nav');
        const chapterList = document.getElementById('chapter-list');
        
        chapterNav.style.display = 'block';
        chapterList.innerHTML = this.renderChapterList(book);

        // Show book overview in reader
        this.showBookOverview(book);
    }

    selectChapter(chapterId) {
        if (!this.currentBook) return;

        const chapter = this.currentBook.chapters.find(c => c.id === chapterId);
        if (!chapter) return;

        this.currentChapter = chapter;

        // Update chapter selection visual
        document.querySelectorAll('.chapter-item').forEach(item => {
            item.classList.remove('selected');
        });
        document.querySelector(`[data-chapter-id="${chapterId}"]`).classList.add('selected');

        // Show chapter content
        this.showChapterContent(chapter);
    }

    showBookOverview(book) {
        const readerContent = document.getElementById('reader-content');
        readerContent.innerHTML = `
            <div class="book-overview">
                <header class="content-header">
                    <h1>${book.name}</h1>
                    <div class="book-metadata">
                        <span class="cycle-info">Cycles ${book.cycle_range.start}${book.cycle_range.end ? `-${book.cycle_range.end}` : '+'}</span>
                        <span class="chapter-count">${book.chapters?.length || 0} chapters</span>
                        <span class="created-date">Created: ${this.formatDate(book.created_at)}</span>
                    </div>
                </header>

                <div class="book-description">
                    <p>${book.description || 'No description available.'}</p>
                </div>

                <div class="chapters-summary">
                    <h2>Chapters</h2>
                    <div class="chapter-grid">
                        ${(book.chapters || []).map(chapter => `
                            <div class="chapter-card" onclick="document.querySelector('[data-chapter-id=\\"${chapter.id}\\"]').click()">
                                <h3>Chapter ${chapter.chapter_number}</h3>
                                <h4>${chapter.chapter_title}</h4>
                                <div class="chapter-preview">
                                    ${(chapter.chapter_text || '').substring(0, 150)}...
                                </div>
                                <div class="chapter-footer">
                                    <span class="version">v${chapter.version_number || 1}</span>
                                    <span class="themes">${(chapter.theological_themes || []).slice(0, 3).join(', ')}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    showChapterContent(chapter) {
        const readerContent = document.getElementById('reader-content');
        readerContent.innerHTML = `
            <div class="chapter-content">
                <header class="content-header">
                    <div class="breadcrumb">
                        <span class="book-name">${this.currentBook.name}</span>
                        <span class="separator">›</span>
                        <span class="chapter-name">Chapter ${chapter.chapter_number}</span>
                    </div>
                    <h1>${chapter.chapter_title}</h1>
                    <div class="chapter-metadata">
                        <span class="version">Version ${chapter.version_number || 1}</span>
                        <span class="style">Style: ${chapter.writing_style || 'Unknown'}</span>
                        <span class="updated">Updated: ${this.formatDate(chapter.last_updated)}</span>
                    </div>
                </header>

                <div class="chapter-themes">
                    <h3>Theological Themes</h3>
                    <div class="theme-tags">
                        ${(chapter.theological_themes || []).map(theme => 
                            `<span class="theme-tag">${theme}</span>`
                        ).join('')}
                    </div>
                </div>

                <div class="chapter-text">
                    ${this.formatChapterText(chapter.chapter_text || 'No content available.')}
                </div>

                <footer class="chapter-footer">
                    <div class="referenced-cycles">
                        <h4>Referenced Cycles</h4>
                        <div class="cycle-tags">
                            ${(chapter.referenced_cycles || []).map(cycle => 
                                `<span class="cycle-tag">Cycle ${cycle}</span>`
                            ).join('')}
                        </div>
                    </div>

                    <div class="referenced-agents">
                        <h4>Sacred Architects</h4>
                        <div class="agent-tags">
                            ${(chapter.referenced_agents || []).map(agent => 
                                `<span class="agent-tag">${agent}</span>`
                            ).join('')}
                        </div>
                    </div>
                </footer>
            </div>
        `;
    }

    formatChapterText(text) {
        // Convert markdown-like formatting to HTML
        return text
            .replace(/^# (.+)$/gm, '<h1>$1</h1>')
            .replace(/^## (.+)$/gm, '<h2>$1</h2>')
            .replace(/^### (.+)$/gm, '<h3>$1</h3>')
            .replace(/^\*(.+)\*$/gm, '<p class="italic">$1</p>')
            .replace(/^---$/gm, '<hr>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/^(?!<[h123]|<hr|<p class="italic")(.+)$/gm, '<p>$1</p>')
            .replace(/<p><\/p>/g, '');
    }

    showTimeline() {
        const modal = document.getElementById('timeline-modal');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    hideTimeline() {
        const modal = document.getElementById('timeline-modal');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    loadDefaultView() {
        // Auto-select first book if available
        if (this.bibleData?.books?.length > 0) {
            // Just show the welcome message initially
        }
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (e) {
            return 'Unknown';
        }
    }

    showError(message) {
        const container = document.getElementById('living-bible-container') || document.body;
        container.innerHTML = `
            <div class="error-message">
                <h2>❌ Error</h2>
                <p>${message}</p>
            </div>
        `;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('living-bible') || document.getElementById('living-bible-container')) {
        new LivingBibleInterface();
    }
});

// Export for use in other modules
window.LivingBibleInterface = LivingBibleInterface;