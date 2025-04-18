document.addEventListener('DOMContentLoaded', function() {
    // Copy page URL button
    const copyPageButton = document.querySelector('.copy-button button');
    if (copyPageButton) {
        copyPageButton.addEventListener('click', function() {
            const url = window.location.href;
            navigator.clipboard.writeText(url).then(function() {
                const icon = copyPageButton.querySelector('i');
                const originalClass = icon.className;
                
                // Change to check icon
                icon.className = 'fas fa-check';
                
                // Reset after 2 seconds
                setTimeout(function() {
                    icon.className = originalClass;
                }, 2000);
            });
        });
    }
    
    // Copy code buttons
    const copyCodeButtons = document.querySelectorAll('.copy-code');
    copyCodeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const codeBlock = button.parentNode.querySelector('code');
            const code = codeBlock.textContent;
            
            navigator.clipboard.writeText(code).then(function() {
                const icon = button.querySelector('i');
                const originalClass = icon.className;
                
                // Change to check icon
                icon.className = 'fas fa-check';
                
                // Reset after 2 seconds
                setTimeout(function() {
                    icon.className = originalClass;
                }, 2000);
            });
        });
    });
    
    // Feedback buttons
    const feedbackButtons = document.querySelectorAll('.feedback-buttons button');
    feedbackButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const feedbackSection = document.querySelector('.feedback-section');
            feedbackSection.innerHTML = '<p>Thank you for your feedback!</p>';
        });
    });
    
    // Search functionality
    const searchInput = document.querySelector('.search-bar input');
    const searchButton = document.querySelector('.search-bar button');
    
    if (searchInput && searchButton) {
        searchButton.addEventListener('click', function() {
            handleSearch();
        });
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
    }
    
    function handleSearch() {
        const query = searchInput.value.trim();
        if (query) {
            // In a real implementation, this would redirect to a search results page
            // For now, we'll just alert
            alert('Search functionality would search for: ' + query);
        }
    }
    
    // Mobile navigation toggle
    const mobileNavToggle = document.createElement('button');
    mobileNavToggle.className = 'mobile-nav-toggle';
    mobileNavToggle.innerHTML = '<i class="fas fa-bars"></i>';
    
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebar && window.innerWidth < 1024) {
        document.querySelector('header .container').appendChild(mobileNavToggle);
        
        mobileNavToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            
            const icon = mobileNavToggle.querySelector('i');
            if (sidebar.classList.contains('active')) {
                icon.className = 'fas fa-times';
            } else {
                icon.className = 'fas fa-bars';
            }
        });
    }
    
    // Add anchor links to headings
    const headings = document.querySelectorAll('h2[id], h3[id], h4[id]');
    headings.forEach(function(heading) {
        const anchor = document.createElement('a');
        anchor.className = 'anchor-link';
        anchor.href = '#' + heading.id;
        anchor.innerHTML = '<i class="fas fa-link"></i>';
        heading.appendChild(anchor);
    });
    
    // Highlight current page in sidebar
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-nav a');
    
    sidebarLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath || 
            (currentPath.endsWith('/') && link.getAttribute('href') === 'index.html')) {
            link.parentNode.classList.add('active');
        }
    });
});
