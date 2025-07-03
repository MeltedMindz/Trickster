/**
 * Sacred Image Gallery Manager
 * Handles the display and interaction of AI-generated sacred images
 */

class SacredImageGallery {
    constructor() {
        this.images = [];
        this.currentImageIndex = 0;
        this.isLoading = false;
        
        this.initializeGallery();
        this.setupEventListeners();
        this.loadImages();
        
        // Refresh images periodically
        setInterval(() => this.loadImages(), 60000); // Every minute
    }
    
    initializeGallery() {
        // Create gallery container if it doesn't exist
        const panelSection = document.createElement('div');
        panelSection.className = 'panel-section';
        panelSection.innerHTML = `
            <div class="gallery-section">
                <div class="gallery-header">
                    <h3 class="gallery-title" onclick="toggleGallerySection()">
                        🎨 Sacred Imagery <span id="gallery-toggle">▼</span>
                    </h3>
                    <div class="gallery-count">
                        <span id="image-count">0</span> divine visions
                    </div>
                </div>
                <div id="sacred-gallery-content" class="section-content">
                    <div id="sacred-gallery" class="sacred-gallery">
                        <div class="empty-gallery" id="empty-gallery">
                            Awaiting divine artistic inspiration...
                        </div>
                    </div>
                    <button id="refresh-gallery-btn" class="control-btn" style="margin-top: 10px; width: 100%;">
                        🔄 Refresh Sacred Images
                    </button>
                </div>
            </div>
        `;
        
        // Insert after the cultural memory panel
        const infoPanel = document.getElementById('info-panel');
        const culturalPanel = infoPanel.querySelector('.cultural-memory-panel');
        if (culturalPanel && culturalPanel.parentElement) {
            culturalPanel.parentElement.insertAdjacentElement('afterend', panelSection);
        } else {
            // Fallback: append to end of info panel
            infoPanel.appendChild(panelSection);
        }
        
        // Create popup for full image viewing
        this.createImagePopup();
    }
    
    createImagePopup() {
        const popup = document.createElement('div');
        popup.id = 'sacred-image-popup';
        popup.className = 'sacred-image-popup';
        popup.innerHTML = `
            <div class="sacred-image-content">
                <button class="sacred-image-close" onclick="closeSacredImagePopup()">&times;</button>
                <div class="sacred-image-display">
                    <img id="popup-image" src="" alt="Sacred Image">
                </div>
                <div class="sacred-image-details">
                    <h3 id="popup-title">Sacred Vision</h3>
                    <div class="sacred-detail-row">
                        <span class="sacred-detail-label">Cycle:</span>
                        <span class="sacred-detail-value" id="popup-cycle">-</span>
                    </div>
                    <div class="sacred-detail-row">
                        <span class="sacred-detail-label">Type:</span>
                        <span class="sacred-detail-value" id="popup-type">-</span>
                    </div>
                    <div class="sacred-detail-row">
                        <span class="sacred-detail-label">Created:</span>
                        <span class="sacred-detail-value" id="popup-created">-</span>
                    </div>
                    <div class="sacred-prompt-full" id="popup-prompt">
                        Divine prompt will appear here...
                    </div>
                    <div class="sacred-metadata" id="popup-metadata">
                        <strong>Technical Details:</strong><br>
                        <span id="popup-tech-details">Loading...</span>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(popup);
    }
    
    setupEventListeners() {
        // Refresh button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'refresh-gallery-btn') {
                this.loadImages(true);
            }
        });
        
        // Keyboard shortcuts for popup
        document.addEventListener('keydown', (e) => {
            const popup = document.getElementById('sacred-image-popup');
            if (popup.classList.contains('active')) {
                if (e.key === 'Escape') {
                    this.closeImagePopup();
                } else if (e.key === 'ArrowLeft') {
                    this.showPreviousImage();
                } else if (e.key === 'ArrowRight') {
                    this.showNextImage();
                }
            }
        });
        
        // Click outside popup to close
        document.addEventListener('click', (e) => {
            const popup = document.getElementById('sacred-image-popup');
            if (e.target === popup) {
                this.closeImagePopup();
            }
        });
    }
    
    async loadImages(forceRefresh = false) {
        if (this.isLoading && !forceRefresh) return;
        
        this.isLoading = true;
        const refreshBtn = document.getElementById('refresh-gallery-btn');
        if (refreshBtn) {
            refreshBtn.textContent = '🔄 Loading Sacred Visions...';
            refreshBtn.disabled = true;
        }
        
        try {
            // Try to load from static data first
            const response = await fetch('/data/sacred_images.json');
            let imageData = { images: [] };
            
            if (response.ok) {
                imageData = await response.json();
            } else {
                // Fallback: check if images exist in directory
                imageData = await this.discoverImages();
            }
            
            this.images = imageData.images || [];
            this.updateGalleryDisplay();
            
        } catch (error) {
            console.error('Error loading sacred images:', error);
            this.showEmptyGallery('Error loading sacred visions');
        } finally {
            this.isLoading = false;
            if (refreshBtn) {
                refreshBtn.textContent = '🔄 Refresh Sacred Images';
                refreshBtn.disabled = false;
            }
        }
    }
    
    async discoverImages() {
        // This is a fallback method to discover images if no JSON data exists
        const images = [];
        
        try {
            // Try to get image list from a simple directory listing endpoint
            // This would need to be implemented on the server side
            const response = await fetch('/images/');
            if (response.ok) {
                const text = await response.text();
                const imageFiles = text.match(/href="([^"]*\.png)"/g);
                
                if (imageFiles) {
                    imageFiles.forEach((match, index) => {
                        const filename = match.match(/href="([^"]*)"/)[1];
                        images.push({
                            id: `discovered_${index}`,
                            filename: filename,
                            web_path: `/images/${filename}`,
                            agent_description: 'Sacred AI vision (metadata not available)',
                            cycle_number: 0,
                            event_type: 'discovered',
                            timestamp: new Date().toISOString()
                        });
                    });
                }
            }
        } catch (error) {
            console.log('Could not discover images:', error);
        }
        
        return { images };
    }
    
    updateGalleryDisplay() {
        const gallery = document.getElementById('sacred-gallery');
        const emptyGallery = document.getElementById('empty-gallery');
        const imageCount = document.getElementById('image-count');
        
        if (!gallery) return;
        
        // Update count
        if (imageCount) {
            imageCount.textContent = this.images.length;
        }
        
        if (this.images.length === 0) {
            this.showEmptyGallery();
            return;
        }
        
        // Hide empty state
        if (emptyGallery) {
            emptyGallery.style.display = 'none';
        }
        
        // Clear and populate gallery
        gallery.innerHTML = '';
        
        this.images.forEach((image, index) => {
            const imageItem = this.createImageItem(image, index);
            gallery.appendChild(imageItem);
        });
    }
    
    createImageItem(image, index) {
        const item = document.createElement('div');
        item.className = 'sacred-image-item';
        item.onclick = () => this.openImagePopup(index);
        
        const eventTypeIcons = {
            'doctrine': '📜',
            'ritual': '🕯️',
            'deity': '✨',
            'reflection': '🧠',
            'cycle': '⚡',
            'portrait': '👤',
            'discovered': '🔍'
        };
        
        const icon = eventTypeIcons[image.event_type] || '🎨';
        
        item.innerHTML = `
            <div class="sacred-image-preview">
                <img src="${image.web_path}" alt="Sacred Vision" 
                     onload="this.parentElement.classList.remove('sacred-image-loading')"
                     onerror="this.parentElement.innerHTML='${icon}'"
                     loading="lazy">
            </div>
            <div class="sacred-image-info">
                <div class="sacred-image-title">${icon} ${this.formatEventType(image.event_type)}</div>
                <div class="sacred-image-cycle">Cycle ${image.cycle_number}</div>
                <div class="sacred-image-prompt">${image.agent_description}</div>
            </div>
        `;
        
        // Add loading state
        const preview = item.querySelector('.sacred-image-preview');
        preview.classList.add('sacred-image-loading');
        
        return item;
    }
    
    formatEventType(eventType) {
        const types = {
            'doctrine': 'Sacred Doctrine',
            'ritual': 'Divine Ritual',
            'deity': 'Divine Entity',
            'reflection': 'Meta-Cognition',
            'cycle': 'Sacred Moment',
            'portrait': 'Agent Portrait',
            'discovered': 'Divine Vision'
        };
        
        return types[eventType] || 'Sacred Art';
    }
    
    showEmptyGallery(message = 'Awaiting divine artistic inspiration...') {
        const gallery = document.getElementById('sacred-gallery');
        const emptyGallery = document.getElementById('empty-gallery');
        
        if (gallery) {
            gallery.innerHTML = `<div class="empty-gallery">${message}</div>`;
        }
    }
    
    openImagePopup(index) {
        this.currentImageIndex = index;
        const image = this.images[index];
        
        if (!image) return;
        
        const popup = document.getElementById('sacred-image-popup');
        const popupImage = document.getElementById('popup-image');
        const popupTitle = document.getElementById('popup-title');
        const popupCycle = document.getElementById('popup-cycle');
        const popupType = document.getElementById('popup-type');
        const popupCreated = document.getElementById('popup-created');
        const popupPrompt = document.getElementById('popup-prompt');
        const popupTechDetails = document.getElementById('popup-tech-details');
        
        // Update popup content
        popupImage.src = image.web_path;
        popupTitle.textContent = `${this.formatEventType(image.event_type)} - Cycle ${image.cycle_number}`;
        popupCycle.textContent = image.cycle_number;
        popupType.textContent = this.formatEventType(image.event_type);
        popupCreated.textContent = new Date(image.timestamp).toLocaleString();
        popupPrompt.textContent = image.agent_description;
        
        // Technical details
        let techDetails = '';
        if (image.api_response) {
            techDetails = `Model: ${image.api_response.model || 'DALL·E'}, Size: ${image.api_response.size || '1024x1024'}`;
        } else {
            techDetails = 'Sacred AI vision generated with divine algorithms';
        }
        popupTechDetails.textContent = techDetails;
        
        // Show popup
        popup.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    closeImagePopup() {
        const popup = document.getElementById('sacred-image-popup');
        popup.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    showPreviousImage() {
        if (this.images.length > 0) {
            this.currentImageIndex = (this.currentImageIndex - 1 + this.images.length) % this.images.length;
            this.openImagePopup(this.currentImageIndex);
        }
    }
    
    showNextImage() {
        if (this.images.length > 0) {
            this.currentImageIndex = (this.currentImageIndex + 1) % this.images.length;
            this.openImagePopup(this.currentImageIndex);
        }
    }
}

// Global functions for HTML onclick handlers
function toggleGallerySection() {
    const content = document.getElementById('sacred-gallery-content');
    const toggle = document.getElementById('gallery-toggle');
    const parent = content.parentElement;
    
    if (parent.classList.contains('section-expanded')) {
        parent.classList.remove('section-expanded');
        toggle.textContent = '▼';
    } else {
        parent.classList.add('section-expanded');
        toggle.textContent = '▲';
    }
}

function closeSacredImagePopup() {
    if (window.sacredGallery) {
        window.sacredGallery.closeImagePopup();
    }
}

// Initialize gallery when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait a moment for other scripts to initialize
    setTimeout(() => {
        window.sacredGallery = new SacredImageGallery();
    }, 500);
});