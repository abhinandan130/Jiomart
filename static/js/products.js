document.addEventListener("DOMContentLoaded", () => {
    fetch("http://127.0.0.1:8000/api/products/")
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById("product-container");

            if (data.products.length === 0) {
                container.innerHTML =
                    "<p class='text-center text-muted'>No products available</p>";
                return;
            }

            data.products.forEach(product => {
                container.innerHTML += `
                    <div class="col-lg-3 col-md-4 col-sm-6">
                        <div class="card product-card shadow-sm h-100">

                            <img src="${product.image}"
                                class="card-img-top">

                            <div class="card-body">
                                <h6 class="fw-semibold">${product.name}</h6>
                                <p class="fw-bold text-primary mb-2">₹ ${product.price}</p>
                            </div>

                            <div class="card-footer bg-white border-0">
                                <button class="btn btn-sm btn-outline-primary w-100">
                                    Add to Cart
                                </button>
                            </div>

                        </div>
                    </div>
                `;

            });
        })
        .catch(err => {
            console.error("Error loading products:", err);
        });
});
