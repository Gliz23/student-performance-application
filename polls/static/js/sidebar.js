document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const toggleButton = document.getElementById('toggleSidebar');

    // Initialize sidebar state
    function initializeSidebar() {
        const isVisible = localStorage.getItem('sidebarVisible') !== 'false';
        
        if (isVisible) {
            sidebar.classList.add('visible');
            sidebar.classList.remove('hidden');
            toggleButton.textContent = '❮';
        } else {
            sidebar.classList.add('hidden');
            sidebar.classList.remove('visible');
            toggleButton.textContent = '❯';
        }
    }

    // Toggle sidebar visibility
    function toggleSidebar() {
        const isVisible = sidebar.classList.contains('visible');
        
        if (isVisible) {
            sidebar.classList.remove('visible');
            sidebar.classList.add('hidden');
            toggleButton.textContent = '❯';
            localStorage.setItem('sidebarVisible', 'false');
        } else {
            sidebar.classList.remove('hidden');
            sidebar.classList.add('visible');
            toggleButton.textContent = '❮';
            localStorage.setItem('sidebarVisible', 'true');
        }
    }

    // Initialize
    initializeSidebar();

    // Event listeners
    toggleButton.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleSidebar();
    });

    // Debugging
    console.log('Sidebar initialized:', {
        visible: sidebar.classList.contains('visible'),
        hidden: sidebar.classList.contains('hidden')
    });
});