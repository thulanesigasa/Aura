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

// Aura Cart Management System
class AuraCart {
    constructor() {
        this.items = JSON.parse(localStorage.getItem('aura_cart')) || [];
        this.syncUI();
    }

    addItem(productId, name, price, shopId, imageUrl) {
        if (this.items.length > 0 && this.items[0].shopId !== shopId) {
            if (!confirm("You already have items from another shop. Clear cart and add this item?")) {
                return;
            }
            this.items = [];
        }

        const existing = this.items.find(i => i.id === productId);
        if (existing) {
            existing.quantity += 1;
        } else {
            this.items.push({
                id: productId,
                name: name,
                price: parseFloat(price),
                shopId: shopId,
                imageUrl: imageUrl,
                quantity: 1
            });
        }
        this.save();
    }

    removeItem(productId) {
        this.items = this.items.filter(i => i.id !== productId);
        this.save();
    }

    updateQuantity(productId, delta) {
        const item = this.items.find(i => i.id === productId);
        if (item) {
            item.quantity += delta;
            if (item.quantity <= 0) {
                this.removeItem(productId);
            } else {
                this.save();
            }
        }
    }

    clear() {
        this.items = [];
        this.save();
        localStorage.removeItem('aura_cart');
    }

    save() {
        localStorage.setItem('aura_cart', JSON.stringify(this.items));
        this.syncUI();
    }

    get count() {
        return this.items.reduce((sum, i) => sum + i.quantity, 0);
    }

    get total() {
        return this.items.reduce((sum, i) => sum + (i.price * i.quantity), 0);
    }

    syncUI() {
        const countElements = document.querySelectorAll('.cart-count');
        const totalElements = document.querySelectorAll('.cart-total');

        countElements.forEach(el => el.textContent = this.count);
        totalElements.forEach(el => el.textContent = 'R' + this.total.toFixed(2));

        this.renderCartItems();

        // Dispatch custom event for parts of the app that need to re-render
        window.dispatchEvent(new CustomEvent('aura-cart-updated', { detail: this }));
    }

    renderCartItems() {
        const container = document.getElementById('cartItemsList');
        if (!container) return;

        if (this.items.length === 0) {
            container.innerHTML = `
                <div class="empty-cart-msg text-center py-20">
                    <p class="text-mil-softDark italic">Your basket is empty.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.items.map(item => `
            <div class="flex items-center gap-4 group">
                <div class="w-16 h-16 bg-mil-softBg rounded-xl overflow-hidden border border-mil-border flex-shrink-0">
                    <img src="${item.imageUrl}" class="w-full h-full object-cover group-hover:scale-110 transition-transform">
                </div>
                <div class="flex-1">
                    <h4 class="text-sm font-bold text-mil-dark">${item.name}</h4>
                    <p class="text-[10px] text-mil-softDark font-medium">R${item.price.toFixed(2)}</p>
                    <div class="flex items-center gap-3 mt-2">
                        <button onclick="auraCart.updateQuantity(${item.id}, -1)" class="w-6 h-6 rounded-full border border-mil-border flex items-center justify-center text-mil-softDark hover:bg-mil-dark hover:text-white transition-all">-</button>
                        <span class="text-xs font-bold w-4 text-center">${item.quantity}</span>
                        <button onclick="auraCart.updateQuantity(${item.id}, 1)" class="w-6 h-6 rounded-full border border-mil-border flex items-center justify-center text-mil-softDark hover:bg-mil-dark hover:text-white transition-all">+</button>
                    </div>
                </div>
                <button onclick="auraCart.removeItem(${item.id})" class="text-red-400 hover:text-red-600 transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                </button>
            </div>
        `).join('');
    }
}

// Global UI Helper
window.toggleCartSidebar = function () {
    const sidebar = document.getElementById('cartSidebar');
    const content = sidebar.querySelector('.absolute.top-0.right-0');

    if (sidebar.classList.contains('hidden')) {
        sidebar.classList.remove('hidden');
        setTimeout(() => {
            content.classList.remove('translate-x-full');
            content.classList.add('translate-x-0');
        }, 10);
    } else {
        content.classList.remove('translate-x-0');
        content.classList.add('translate-x-full');
        setTimeout(() => sidebar.classList.add('hidden'), 500);
    }
}

// Global instance
window.auraCart = new AuraCart();
