document.addEventListener("DOMContentLoaded", () => {
    const isAuthenticated = document.body.dataset.authenticated === "true";

    const showLoginPopup = () => {
        const modal = new bootstrap.Modal(
            document.getElementById("loginRequiredModal")
        );
        modal.show();
    };

    const addToCart = async (productId, redirect = false) => {
        try {
            const res = await fetch(`/api/cart/add/${productId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken()
                }
            });

            if (!res.ok) return;

            if (typeof refreshCartCount === "function") {
                refreshCartCount();
            }

            if (redirect) {
                window.location.href = "/cart/";
            }

        } catch (err) {
            console.error("Add to cart error:", err);
        }
    };

    document.addEventListener("click", (e) => {
        const addBtn = e.target.closest(".add-to-cart-btn");
        const buyBtn = e.target.closest(".buy-now-btn");

        if (!addBtn && !buyBtn) return;

        const productId = (addBtn || buyBtn).dataset.productId;

        if (!isAuthenticated) {
            showLoginPopup();
            return;
        }

        if (addBtn) addToCart(productId);
        if (buyBtn) addToCart(productId, true);
    });
});

function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]")?.value;
}


document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".product-section").forEach(section => {

        const row = section.querySelector(".product-row");
        const leftBtn = section.querySelector(".product-carousel-btn.left");
        const rightBtn = section.querySelector(".product-carousel-btn.right");
        const viewAll = section.querySelector(".view-all-link");

        if (!row) return;

        // Check if row overflows
        const isOverflowing = row.scrollWidth > row.clientWidth;

        if (isOverflowing) {
            // Show arrows
            if (leftBtn) leftBtn.style.display = "flex";
            if (rightBtn) rightBtn.style.display = "flex";

            // Show View All
            if (viewAll) viewAll.style.display = "inline";
        }
    });

});