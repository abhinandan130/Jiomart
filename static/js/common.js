/* ===============================
   COMMON JS UTILITIES
   =============================== */

document.addEventListener("DOMContentLoaded", () => {
    console.log("Common JS loaded");

    // Run cart count once globally
    if (typeof refreshCartCount === "function") {
        refreshCartCount();
    }
});

/* ---------- DOM HELPERS ---------- */

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

/* ---------- FETCH HELPER ---------- */

const apiFetch = (url, onSuccess, onError = null, options = {}) => {
    fetch(url, options)
        .then(res => {
            if (!res.ok) throw new Error("Network response failed");
            return res.json();
        })
        .then(data => onSuccess(data))
        .catch(err => {
            console.error("API Error:", err);
            if (onError) onError(err);
        });
};

/* ---------- ACTIVE CLASS TOGGLER ---------- */

const toggleActive = (elements, activeEl, className = "active") => {
    elements.forEach(el => el.classList.remove(className));
    activeEl.classList.add(className);
};

/* ---------- SIMPLE TOAST (OPTIONAL) ---------- */

const showToast = (message, type = "success") => {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerText = message;

    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add("show"), 50);
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

/* ===============================
   CART COUNT (GLOBAL)
   =============================== */
window.refreshCartCount = async function () {
    try {
        const res = await fetch("/api/cart/count/");
        if (!res.ok) return;

        const data = await res.json();
        const badge = document.getElementById("cart-count");
        if (!badge) return;

        if (data.count > 0) {
            badge.textContent = data.count;
            badge.style.display = "inline-block";
        } else {
            badge.style.display = "none";
        }
    } catch (err) {
        console.error("Cart count error:", err);
    }
};


/* ===============================
   CART HOVER LOGIC (NO HTML HERE)
=============================== */
document.addEventListener("DOMContentLoaded", () => {
    const cartHover = document.querySelector(".cart-hover");
    const emptyBox = document.getElementById("cart-hover-empty");
    const itemsBox = document.getElementById("cart-hover-items");
    const itemsContainer = document.getElementById("cart-hover-content");
    const totalContainer = document.getElementById("cart-hover-total");

    if (!cartHover || !itemsBox || !itemsContainer || !totalContainer) return;

    const hideAll = () => {
        emptyBox?.classList.add("d-none");
        itemsBox.classList.add("d-none");
    };

    const loadCartPreview = async () => {
        try {
            const res = await fetch("/api/cart/preview/");
            if (!res.ok) return;

            const data = await res.json();
            hideAll();

            // EMPTY CART
            if (!data.items || data.items.length === 0) {
                emptyBox?.classList.remove("d-none");
                return;
            }

            // ITEMS
            itemsContainer.innerHTML = "";

            data.items.forEach(item => {
                const row = document.createElement("div");
                row.className = "d-flex align-items-center justify-content-between gap-2 small";

                row.innerHTML = `
                    <div class="d-flex align-items-center gap-2">
                        <img src="${item.image}"
                            alt="${item.name}"
                            style="width:38px;height:38px;object-fit:contain;"
                            class="border rounded">

                        <div>
                            <strong>${item.name}</strong><br>
                            <span class="text-muted">Qty: ${item.quantity ?? item.qty}</span>
                        </div>
                    </div>

                    <div class="fw-semibold">₹${item.subtotal}</div>
                `;

                itemsContainer.appendChild(row);
            });


            totalContainer.textContent = `Total: ₹${data.total ?? data.total_amount}`;
            itemsBox.classList.remove("d-none");

        } catch (err) {
            console.error("Cart hover error:", err);
        }
    };

    cartHover.addEventListener("mouseenter", loadCartPreview);
});

/* ===============================
   LIVE SEARCH SUGGESTIONS
=============================== */

/* =========================
   JIOMART SEARCH (COMMON)
   ========================= */

const searchInput = document.getElementById("search-input");
const searchDropdown = document.getElementById("search-dropdown");

const suggestionsBox = document.getElementById("search-suggestions");
const productsBox = document.getElementById("search-products");
const categoriesBox = document.getElementById("search-categories");
const brandsBox = document.getElementById("search-brands");

let searchTimer = null;

if (searchInput) {
    searchInput.addEventListener("input", () => {
        clearTimeout(searchTimer);

        const query = searchInput.value.trim();
        if (!query) {
            hideSearchDropdown();
            return;
        }

        searchTimer = setTimeout(() => {
            fetchSearchResults(query);
        }, 300); // debounce
    });
}

async function fetchSearchResults(query) {
    try {
        const res = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
        if (!res.ok) return;

        const data = await res.json();
        renderSearchResults(data);
    } catch (err) {
        console.error("Search error:", err);
    }
}

function renderSearchResults(data) {
    // show dropdown
    searchDropdown.classList.remove("d-none");

    /* -------- Suggestions -------- */
    suggestionsBox.innerHTML = "";

    data.suggestions.forEach(text => {
        const li = document.createElement("li");
        li.textContent = text;

        li.addEventListener("click", (e) => {
            e.preventDefault();      // ⬅ STOP form submit
            e.stopPropagation();     // ⬅ STOP bubbling

            const product = data.products.find(p => p.name === text);

            if (product && product.category) {
                window.location.href = `/category/${encodeURIComponent(product.category)}/`;
            } else {
                // fallback only if category missing
                searchInput.value = text;
                searchInput.form.submit();
            }
        });

        suggestionsBox.appendChild(li);
    });



    /* -------- Products -------- */
    productsBox.innerHTML = "";

    data.products.forEach(p => {
        productsBox.innerHTML += `
            <div class="search-product-card"
                data-product-id="${p.id}"
                data-category="${p.category}">

                <img src="${p.image}" alt="${p.name}">

                <div class="search-product-info">
                    <div class="search-product-name">${p.name}</div>
                    <div class="search-product-price">₹${p.price}</div>

                    <button
                        class="btn btn-sm btn-outline-primary search-add-btn"
                        data-product-id="${p.id}">
                        Add +
                    </button>
                </div>
            </div>
        `;
    });


    /* -------- Categories -------- */
    categoriesBox.innerHTML = "";

    data.categories.forEach(category => {
        const chip = document.createElement("span");
        chip.className = "search-chip";
        chip.textContent = category;

        chip.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            window.location.href = `/category/${encodeURIComponent(category)}/`;
        });

        categoriesBox.appendChild(chip);
    });



    /* -------- Brands -------- */
    brandsBox.innerHTML = "";

    data.brands.forEach(brand => {
        const chip = document.createElement("span");
        chip.className = "search-chip";
        chip.textContent = brand;

        chip.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            window.location.href = `/brand/${encodeURIComponent(brand)}/`;
        });

        brandsBox.appendChild(chip);
    });

}

function hideSearchDropdown() {
    searchDropdown.classList.add("d-none");
}

/* -------- Click outside to close -------- */
document.addEventListener("click", (e) => {
    if (!searchDropdown.contains(e.target) && !searchInput.contains(e.target)) {
        hideSearchDropdown();
    }
});



// SEARCH DROPDOWN PRODUCT INTERACTIONS
productsBox.addEventListener("click", function (e) {

    /* =========================
       ADD TO CART
       ========================= */
    if (e.target.classList.contains("search-add-btn")) {
        e.preventDefault();
        e.stopPropagation();

        // 🔐 LOGIN CHECK
        if (!window.IS_LOGGED_IN) {
            const modal = new bootstrap.Modal(
                document.getElementById("loginRequiredModal")
            );
            modal.show();
            return;
        }


        const productId = e.target.dataset.productId;

        fetch(`/api/cart/add/${productId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
            }
        })
        .then(res => {
            if (res.ok) {
                refreshCartCount();
            } else {
                console.error("Add to cart failed:", res.status);
            }
        })
        .catch(err => console.error("Add to cart error:", err));

        return;
    }


    /* =========================
       PRODUCT CARD CLICK
       ========================= */
    const card = e.target.closest(".search-product-card");
    if (!card) return;

    const category = card.dataset.category;
    if (category) {
        window.location.href = `/category/${encodeURIComponent(category)}/`;
    }
});




function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
}
