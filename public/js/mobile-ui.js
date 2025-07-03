/**
 * Mobile UI enhancements for AI Religion Architects
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeMobileUI();
});

function initializeMobileUI() {
    const mobileToggle = document.getElementById('mobile-toggle');
    const infoPanel = document.getElementById('info-panel');
    const overlay = document.getElementById('info-panel-overlay');
    
    if (!mobileToggle || !infoPanel || !overlay) {
        console.warn('Mobile UI elements not found');
        return;
    }
    
    // Mobile menu toggle
    mobileToggle.addEventListener('click', function() {
        toggleMobilePanel();
    });
    
    // Close panel when clicking overlay
    overlay.addEventListener('click', function() {
        closeMobilePanel();
    });
    
    // Close panel on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeMobilePanel();
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMobilePanel();
        }
    });
    
    // Touch handling for better mobile experience
    let touchStartX = 0;
    let touchStartY = 0;
    
    document.addEventListener('touchstart', function(e) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchmove', function(e) {
        if (!infoPanel.classList.contains('open')) return;
        
        const touchX = e.touches[0].clientX;
        const touchY = e.touches[0].clientY;
        const deltaX = touchX - touchStartX;
        const deltaY = Math.abs(touchY - touchStartY);
        
        // Swipe left to close panel
        if (deltaX < -50 && deltaY < 100) {
            closeMobilePanel();
        }
    });
    
    // Optimize scrolling for mobile
    if (isMobileDevice()) {
        optimizeMobileScrolling();
    }
}

function toggleMobilePanel() {
    const infoPanel = document.getElementById('info-panel');
    const overlay = document.getElementById('info-panel-overlay');
    const mobileToggle = document.getElementById('mobile-toggle');
    
    if (infoPanel.classList.contains('open')) {
        closeMobilePanel();
    } else {
        openMobilePanel();
    }
}

function openMobilePanel() {
    const infoPanel = document.getElementById('info-panel');
    const overlay = document.getElementById('info-panel-overlay');
    const mobileToggle = document.getElementById('mobile-toggle');
    
    infoPanel.classList.add('open');
    overlay.classList.add('open');
    mobileToggle.textContent = '✕ Close';
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
}

function closeMobilePanel() {
    const infoPanel = document.getElementById('info-panel');
    const overlay = document.getElementById('info-panel-overlay');
    const mobileToggle = document.getElementById('mobile-toggle');
    
    infoPanel.classList.remove('open');
    overlay.classList.remove('open');
    mobileToggle.textContent = '📋 Menu';
    
    // Restore body scroll
    document.body.style.overflow = '';
}

function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           window.innerWidth <= 768;
}

function optimizeMobileScrolling() {
    // Add momentum scrolling for iOS
    const scrollableElements = document.querySelectorAll('.terminal-output, .info-panel, .agent-memory-container');
    scrollableElements.forEach(element => {
        element.style.webkitOverflowScrolling = 'touch';
    });
    
    // Prevent zoom on input focus for iOS
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            if (isMobileDevice()) {
                const viewport = document.querySelector('meta[name=viewport]');
                if (viewport) {
                    viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
                }
            }
        });
        
        input.addEventListener('blur', function() {
            if (isMobileDevice()) {
                const viewport = document.querySelector('meta[name=viewport]');
                if (viewport) {
                    viewport.setAttribute('content', 'width=device-width, initial-scale=1.0');
                }
            }
        });
    });
}

// Performance optimizations for mobile
function optimizeForMobile() {
    if (!isMobileDevice()) return;
    
    // Reduce animation complexity on mobile
    const style = document.createElement('style');
    style.textContent = `
        @media (max-width: 768px) {
            * {
                animation-duration: 0.2s !important;
                transition-duration: 0.2s !important;
            }
            
            .cursor {
                animation: none !important;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Lazy load non-critical content on mobile
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('loaded');
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.memory-section').forEach(section => {
        observer.observe(section);
    });
}

// Initialize mobile optimizations
document.addEventListener('DOMContentLoaded', optimizeForMobile);

// Export functions for use in other scripts
window.MobileUI = {
    togglePanel: toggleMobilePanel,
    openPanel: openMobilePanel,
    closePanel: closeMobilePanel,
    isMobile: isMobileDevice
};