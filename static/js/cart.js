// ================================
// CSRF TOKEN
// ================================
function getCSRFToken() {
    return document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];
}

// ================================
// LOAD CART COUNT (ALWAYS FROM SERVER)
// ================================
function loadCartCount() {
    fetch("/api/cart/count/", {
        cache: "no-store",
        headers: { "Accept": "application/json" }
    })
    .then(res => res.json())
    .then(data => {
        const el = document.getElementById("cart-count");
        if (!el) return;

        if (data.count > 0) {
            el.innerText = data.count;
            el.style.display = "inline-block";
        } else {
            el.innerText = "";
            el.style.display = "none";
        }
    })
    .catch(err => console.error("Cart count error:", err));
}

// ================================
// ADD TO CART (HOME PAGE)
// ================================
document.addEventListener("click", function (e) {
    const btn = e.target.closest(".add-to-cart-btn");
    if (!btn) return;

    const productId = btn.dataset.productId;

    fetch(`/api/cart/add/${productId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Accept": "application/json"
        }
    })
    .then(async res => {
        const data = await res.json();

        if (!res.ok || data.error) {
            alert("Login required to add items to cart.");
            return;
        }

        if (data.already_exists) {
            const confirmUpdate = confirm(
                "This product is already in your cart.\nDo you want to increase the quantity?"
            );
            if (!confirmUpdate) return;
        }

        // 🔥 Always sync navbar count from DB
        loadCartCount();
    })
    .catch(err => console.error(err));
});

// ================================
// UPDATE QUANTITY (+ / -) — CART PAGE
// ================================
document.addEventListener("click", function (e) {
    const btn = e.target.closest(".qty-btn");
    if (!btn) return;

    const itemId = btn.dataset.id;
    const action = btn.dataset.action;

    fetch("/api/cart/update-qty/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        },
        body: new URLSearchParams({
            item_id: itemId,
            action: action
        })
    })
    .then(async res => {
        const data = await res.json();

        if (!res.ok || data.error) {
            alert("Login required to update cart.");
            return;
        }

        if (!data.success) return;

        // Item removed
        if (data.deleted) {
            document.getElementById(`row-${itemId}`)?.remove();
        } else {
            document.getElementById(`qty-${itemId}`).innerText = data.quantity;
            document.getElementById(`subtotal-${itemId}`).innerText =
                `₹${data.item_subtotal}`;
        }

        // Update cart total
        const totalEl = document.getElementById("cart-total");
        if (totalEl) totalEl.innerText = `₹${data.cart_total}`;

        // Empty cart UI
        if (data.cart_total === 0) {
            document.getElementById("cart-wrapper")?.classList.add("d-none");
            document.getElementById("empty-cart")?.classList.remove("d-none");
        }

        // 🔥 Keep navbar in sync
        loadCartCount();
    })
    .catch(err => console.error(err));
});

// ================================
// BUY NOW
// ================================
document.addEventListener("click", function (e) {
    const btn = e.target.closest(".buy-now-btn");
    if (!btn) return;

    const productId = btn.dataset.productId;

    fetch(`/api/cart/add/${productId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        },
        body: new URLSearchParams({
            mode: "buy_now"
        })
    })
    .then(async res => {
        const data = await res.json();

        if (!res.ok || data.error) {
            alert("Login required to buy this product.");
            return;
        }

        // Sync cart count
        loadCartCount();

        // 🚀 Redirect if backend sends redirect_url
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        }
    })
    .catch(err => console.error(err));
});

// ================================
// PAGE LOAD + BACK/FORWARD FIX 🔥
// ================================
document.addEventListener("DOMContentLoaded", loadCartCount);

// Handles browser back/forward cache
window.addEventListener("pageshow", function () {
    loadCartCount();
});