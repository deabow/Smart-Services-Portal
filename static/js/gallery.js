// Gallery JavaScript for About Page
document.addEventListener('DOMContentLoaded', function() {
    
    // Create modal for image gallery
    createImageModal();
    
    // Add click events to gallery items
    addGalleryClickEvents();
    
    // Add click events to achievement gallery items
    addAchievementGalleryClickEvents();
});

function createImageModal() {
    // Create modal HTML
    const modalHTML = `
        <div id="imageModal" class="modal fade" tabindex="-1" role="dialog" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="imageModalTitle">معرض الصور</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img id="modalImage" src="" alt="" class="img-fluid rounded">
                        <div id="modalDescription" class="mt-3"></div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                        <button type="button" class="btn btn-primary" id="downloadBtn" style="display: none;">
                            <i class="fas fa-download"></i> تحميل الصورة
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function addGalleryClickEvents() {
    // Sidebar gallery items
    const galleryItems = document.querySelectorAll('.gallery-item-small');
    
    galleryItems.forEach((item, index) => {
        item.addEventListener('click', function() {
            const img = this.querySelector('.gallery-img');
            const src = img.src;
            const alt = img.alt;
            
            showImageModal(src, alt, `صورة ${index + 1}`);
        });
    });
}

function addAchievementGalleryClickEvents() {
    // Achievement gallery items
    const achievementItems = document.querySelectorAll('.achievement-gallery-item');
    
    achievementItems.forEach((item, index) => {
        item.addEventListener('click', function() {
            const img = this.querySelector('.achievement-gallery-img');
            const src = img.src;
            const alt = img.alt;
            
            // Get title and description from overlay content
            const overlayContent = this.querySelector('.overlay-content');
            const title = overlayContent ? overlayContent.querySelector('h5').textContent : `إنجاز ${index + 1}`;
            const description = overlayContent ? overlayContent.querySelector('p').textContent : '';
            
            showImageModal(src, alt, title, description);
        });
    });
}

function showImageModal(src, alt, title, description = '') {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalTitle = document.getElementById('imageModalTitle');
    const modalDescription = document.getElementById('modalDescription');
    const downloadBtn = document.getElementById('downloadBtn');
    
    // Set image source and alt
    modalImage.src = src;
    modalImage.alt = alt;
    
    // Set title
    modalTitle.textContent = title;
    
    // Set description
    if (description) {
        modalDescription.innerHTML = `<p class="text-muted">${description}</p>`;
        modalDescription.style.display = 'block';
    } else {
        modalDescription.style.display = 'none';
    }
    
    // Set download button
    downloadBtn.onclick = function() {
        downloadImage(src, alt);
    };
    downloadBtn.style.display = 'inline-block';
    
    // Show modal using Bootstrap
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

function downloadImage(src, alt) {
    // Create a temporary link element
    const link = document.createElement('a');
    link.href = src;
    link.download = alt || 'image';
    link.target = '_blank';
    
    // Trigger download
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Add keyboard navigation
document.addEventListener('keydown', function(e) {
    const modal = document.getElementById('imageModal');
    if (modal && modal.classList.contains('show')) {
        if (e.key === 'Escape') {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    }
});

// Add touch/swipe support for mobile
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', function(e) {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', function(e) {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    const modal = document.getElementById('imageModal');
    if (modal && modal.classList.contains('show')) {
        const swipeThreshold = 50;
        const swipeDistance = touchEndX - touchStartX;
        
        if (Math.abs(swipeDistance) > swipeThreshold) {
            if (swipeDistance > 0) {
                // Swipe right - close modal
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            }
        }
    }
}
