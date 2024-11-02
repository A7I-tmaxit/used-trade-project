let userBalance = 0;
let userName = "";
let transactions = [];
let selectedProductId = null;
let userId = "";

// Show a specific section and hide others
function showSection(sectionId) {
    const sections = ["login", "register", "mainPage", "myPage", "sellPage", "productDetailPage", "mySalesPage", "wishlistPage"];
    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.classList.add("d-none");
    });
    document.getElementById(sectionId).classList.remove("d-none");
}

// Function to transition to the main page after successful login or registration
function transitionToMainPage() {
    showSection("mainPage");
    loadProductList();
}

// Login function
function login() {
    const username = document.getElementById("loginUsername").value;
    const password = document.getElementById("loginPassword").value;

    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Login successful") {
            userBalance = data.balance;
            userName = data.name;
            userId = data.userId;
            transitionToMainPage();
        } else {
            document.getElementById("loginMessage").innerText = data.message;
        }
    })
    .catch(error => console.error("Error during login:", error));
}

// Register function
function register() {
    const username = document.getElementById("registerUsername").value;
    const password = document.getElementById("registerPassword").value;
    const name = document.getElementById("registerName").value;
    const balance = parseInt(document.getElementById("registerBalance").value);

    fetch("/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, name, balance })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "User registered successfully") {
            userBalance = balance;
            userName = name;
            userId = data.userId;
            transitionToMainPage();
        } else {
            document.getElementById("registerMessage").innerText = data.message;
        }
    })
    .catch(error => console.error("Error during registration:", error));
}

function showProductDetail(product) {
    selectedProductId = product.id;
    const productDetail = document.getElementById("productDetail");

    let imageHtml = product.images.map(img => `<img src="${img}" class="img-fluid mb-2" alt="Product Image">`).join("");
    
    productDetail.innerHTML = `
        ${imageHtml}
        <h3>${product.name}</h3>
        <p>${product.description}</p>
        <p><strong>가격: ${product.price} 원</strong></p>
        <p><strong>판매자: ${product.sellerName || "Unknown"}</strong></p>
    `;
    showSection("productDetailPage");
}

// Show My Page with user details
function showMyPage() {
    document.getElementById("profileName").innerText = userName;
    document.getElementById("accountBalance").innerText = `${userBalance} 원`;
    showSection("myPage");
}

// Load and show My Sales Page
function loadMySales() {
    fetch(`http://localhost:8080/user_sales?userId=${userId}`)
        .then(response => response.json())
        .then(items => {
            const mySalesList = document.getElementById("mySalesList");
            mySalesList.innerHTML = "";

            if (Object.keys(items).length === 0) {
                mySalesList.innerHTML = "<p>등록된 판매 상품이 없습니다.</p>";
            } else {
                Object.values(items).forEach(item => {
                    const itemCard = document.createElement("div");
                    itemCard.classList.add("card", "m-2");
                    itemCard.style.width = "18rem";
                    itemCard.innerHTML = `
                        <img src="${item.image}" class="card-img-top" alt="Product Image">
                        <div class="card-body">
                            <h5 class="card-title">${item.name}</h5>
                            <p class="card-text">가격: ${item.price} 원</p>
                            <p class="card-text">판매자: ${item.sellerName || userName}</p>
                        </div>
                    `;
                    itemCard.onclick = () => showProductDetail(item);
                    mySalesList.appendChild(itemCard);
                });
            }
        })
        .catch(error => console.error("Error loading sales items:", error));
}

// Show Wishlist Page (similar structure to My Sales)
function showWishlistPage() {
    loadWishlist();
    showSection("wishlistPage");
}

function sellProduct() {
    const productName = document.getElementById("productName").value;
    const productDescription = document.getElementById("productDescription").value;
    const productPrice = parseInt(document.getElementById("productPrice").value);
    const productImageFiles = document.getElementById("productImage").files;

    if (productImageFiles.length > 0) {
        let images = [];
        const readerPromises = Array.from(productImageFiles).map((file) => {
            return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = () => {
                    images.push(reader.result);
                    resolve();
                };
                reader.readAsDataURL(file);
            });
        });

        Promise.all(readerPromises).then(() => {
            const mainImage = images[0];  // Use the first image as main image

            fetch("/add_product", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: productName,
                    description: productDescription,
                    price: productPrice,
                    images: images,  // Send all images
                    mainImage: mainImage,  // Separate main image
                    sellerName: userName,
                    userId: userId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message === "Product added successfully") {
                    showMainPage();
                    loadProductList();
                } else {
                    console.error("Error adding product:", data.message);
                }
            })
            .catch(error => console.error("Error adding product:", error));
        });
    }
}

// Show Sell Page
function showSellPage() {
    showSection("sellPage");
}

// Show Main Page
function showMainPage() {
    showSection("mainPage");
    loadProductList();
}

function loadProductList() {
    fetch("/products")
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to load products");
            }
            return response.json();
        })
        .then(products => displayProductList(products))
        .catch(error => console.error("Error loading products:", error));
}

function displayProductList(products) {
    const productList = document.getElementById("productList");
    productList.innerHTML = '';

    if (Object.keys(products).length === 0) {
        productList.innerHTML = "<p>등록된 상품이 없습니다.</p>";
    } else {
        Object.values(products).forEach(product => {
            const productCard = document.createElement("div");
            productCard.classList.add("card", "m-2");
            productCard.style.width = "18rem";

            // Calculate relative time (e.g., "5일 전")
            const dateAdded = new Date(product.dateAdded);
            const timeDiff = Math.floor((new Date() - dateAdded) / (1000 * 60 * 60 * 24));
            const relativeTime = timeDiff > 0 ? `${timeDiff}일 전` : "오늘";

            productCard.innerHTML = `
                <img src="${product.mainImage}" class="card-img-top" alt="Product Image">
                <div class="card-body">
                    <h5 class="card-title">${product.name}</h5>
                    <p class="card-text"><strong>${product.price.toLocaleString()} 원</strong></p>
                    <small class="text-muted">${relativeTime}</small>
                </div>
            `;
            productCard.onclick = () => showProductDetail(product);
            productList.appendChild(productCard);
        });
    }
}

function showMySalesPage() {
    fetch(`http://localhost:8080/user_sales?userId=${userId}`)
        .then(response => response.json())
        .then(items => {
            const mySalesList = document.getElementById("mySalesList");
            mySalesList.innerHTML = "";

            if (Object.keys(items).length === 0) {
                mySalesList.innerHTML = "<p>등록된 판매 상품이 없습니다.</p>";
            } else {
                Object.values(items).forEach(item => {
                    const itemCard = document.createElement("div");
                    itemCard.classList.add("card", "m-2");
                    itemCard.style.width = "18rem";
                    itemCard.innerHTML = `
                        <img src="${item.mainImage}" class="card-img-top" alt="Product Image">
                        <div class="card-body">
                            <h5 class="card-title">${item.name}</h5>
                            <p class="card-text"><strong>${item.price.toLocaleString()} 원</strong></p>
                            <small class="text-muted">${item.dateAdded}</small>
                        </div>
                    `;
                    mySalesList.appendChild(itemCard);
                });
            }

            // Show the My Sales Page section and hide other sections
            showSection("mySalesPage");
        })
        .catch(error => console.error("Error loading sales items:", error));
}

// Back Button for each page
document.querySelectorAll(".btn-secondary").forEach(button => {
    button.onclick = showMainPage;
});