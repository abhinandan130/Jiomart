document.addEventListener("DOMContentLoaded", () => {
    if (typeof refreshCartCount === "function") {
        refreshCartCount();
    }

    // Fix dividers on initial load as well
    fixCartDividers();
});

/* =========================
   + / - QUANTITY HANDLER
   ========================= */
document.addEventListener("click", async (e) => {
    const btn =
        e.target.classList.contains("qty-btn")
            ? e.target
            : e.target.closest("button.qty-btn");

    if (!btn) return;

    const itemId = btn.dataset.id;
    const action = btn.dataset.action;

    try {
        const res = await fetch(`/api/cart/update/${itemId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ action })
        });

        if (!res.ok) {
            console.warn("Cart update failed:", res.status);
            return;
        }

        const data = await res.json();

        const cartItemEl = document.getElementById(`cart-item-${itemId}`);
        const qtyEl = document.getElementById(`qty-${itemId}`);
        const subtotalEl = document.getElementById(`subtotal-${itemId}`);
        const totalEl = document.getElementById("cart-total");

        // 🔥 Robust removal detection
        const itemRemoved =
            data.removed === true ||
            data.quantity === 0 ||
            data.quantity === undefined;

        if (itemRemoved) {
            if (cartItemEl) cartItemEl.remove();

            if (totalEl) {
                totalEl.textContent = `₹ ${data.cart_total}`;
            }

            if (typeof refreshCartCount === "function") {
                refreshCartCount();
            }

            // 🔥 Recalculate dividers after removal
            fixCartDividers();

            if (data.cart_total === 0) {
                location.reload();
            }
            return;
        }

        // 🔄 LIVE UI UPDATES
        if (qtyEl) qtyEl.textContent = data.quantity;
        if (subtotalEl) subtotalEl.textContent = `₹ ${data.subtotal}`;
        if (totalEl) totalEl.textContent = `₹ ${data.cart_total}`;

        if (typeof refreshCartCount === "function") {
            refreshCartCount();
        }

        // 🔥 Ensure dividers stay correct
        fixCartDividers();

    } catch (err) {
        console.error("Cart update error:", err);
    }
});

/* =========================
   FIX CART DIVIDERS (<hr>)
   ========================= */
function fixCartDividers() {
    const cartItems = document.querySelectorAll(".cart-item");

    cartItems.forEach((item, index) => {
        // Remove existing hr if any
        const hr = item.querySelector("hr");
        if (hr) hr.remove();

        // Add hr only if NOT last item
        if (index < cartItems.length - 1) {
            const divider = document.createElement("hr");
            divider.className = "my-4";
            item.appendChild(divider);
        }
    });
}

/* =========================
   CSRF TOKEN
   ========================= */
function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]")?.value;
}



