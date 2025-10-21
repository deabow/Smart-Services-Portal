// Achievement Admin JavaScript
function updateVillageChoices(selectedArea) {
    const villageField = document.getElementById('id_village');
    if (!villageField) return;
    
    // Clear current options
    villageField.innerHTML = '<option value="">---------</option>';
    
    // Get villages for selected area
    const villages = window.villageChoices[selectedArea] || [];
    
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
    const areaField = document.getElementById('id_area');
    if (areaField) {
        // Set initial village choices
        updateVillageChoices(areaField.value);
        
        // Add change event listener
        areaField.addEventListener('change', function() {
            updateVillageChoices(this.value);
        });
    }
});
