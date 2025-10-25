// Achievement Admin JavaScript
function updateVillageChoices(selectedArea) {
    const villageField = document.getElementById('id_village');
    if (!villageField) return;
    
    // Clear current options
    villageField.innerHTML = '<option value="">---------</option>';
    
    // Debug: Check if villageChoices exists
    if (!window.villageChoices) {
        console.error('villageChoices not found in window object');
        return;
    }
    
    // Get villages for selected area
    const villages = window.villageChoices[selectedArea] || [];
    console.log('Selected area:', selectedArea, 'Available villages:', villages);
    
    // Add new options
    villages.forEach(village => {
        const option = document.createElement('option');
        option.value = village[0];
        option.textContent = village[1];
        villageField.appendChild(option);
    });
    
    // Clear current village selection
    villageField.value = '';
}

// Initialize village choices when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Achievement admin script loaded');
    console.log('Available village choices:', window.villageChoices);
    
    const areaField = document.getElementById('id_area');
    if (areaField) {
        console.log('Area field found:', areaField.value);
        // Set initial village choices
        updateVillageChoices(areaField.value);
        
        // Add change event listener
        areaField.addEventListener('change', function() {
            console.log('Area changed to:', this.value);
            updateVillageChoices(this.value);
        });
    } else {
        console.error('Area field not found');
    }
});
