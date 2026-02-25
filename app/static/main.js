document.addEventListener('DOMContentLoaded', () => {
    // Select the search input and all the shop cards
    const searchInput = document.getElementById('shopSearch');
    const shopCards = document.querySelectorAll('.shop-card');

    if (searchInput) {
        // Real-time event listener for typing
        searchInput.addEventListener('input', (event) => {
            const query = event.target.value.toLowerCase().trim();

            shopCards.forEach(card => {
                // Find the shop-name element within each card
                const shopNameElement = card.querySelector('.shop-name');

                if (shopNameElement) {
                    const shopName = shopNameElement.textContent.toLowerCase();

                    // Dynamically filter DOM elements
                    if (shopName.includes(query)) {
                        card.style.display = ''; // Show matching cards
                    } else {
                        card.style.display = 'none'; // Hide non-matching cards immediately
                    }
                }
            });
        });
    }
    // Hamburger Menu Logic
    const menuToggle = document.getElementById('menuToggle');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const menuIconOpen = document.querySelector('.menu-icon-open');
    const menuIconClose = document.querySelector('.menu-icon-close');

    if (menuToggle && dropdownMenu) {
        let isMenuOpen = false;

        menuToggle.addEventListener('click', () => {
            isMenuOpen = !isMenuOpen;

            if (!isMenuOpen) {
                // Close Menu
                dropdownMenu.classList.remove('menu-open', 'border-b');
                dropdownMenu.classList.add('menu-closed', 'border-b-0');

                menuIconOpen.classList.remove('hidden');
                menuIconClose.classList.add('hidden');
            } else {
                // Open Menu
                dropdownMenu.classList.remove('menu-closed', 'border-b-0');
                dropdownMenu.classList.add('menu-open', 'border-b');

                menuIconOpen.classList.add('hidden');
                menuIconClose.classList.remove('hidden');
            }
        });
    }
});
