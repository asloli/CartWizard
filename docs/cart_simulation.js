document.addEventListener("DOMContentLoaded", () => {
  const productListDiv = document.getElementById("productList");
  const resultDiv = document.getElementById("simulationResult");
  const categorySelect = document.getElementById("categoryFilter");
  const submitBtn = document.getElementById("submitCart");

  let allProducts = [];

  // 讀取產品清單
  fetch("../data/raw/products.json")
    .then(res => res.json())
    .then(data => {
      allProducts = data;
      renderCategoryOptions(data);
      renderProductList(data);
    });

  categorySelect.addEventListener("change", () => {
    const selected = categorySelect.value;
    const filtered = selected === "ALL" ? allProducts : allProducts.filter(p => p.category === selected);
    renderProductList(filtered);
  });

  submitBtn.addEventListener("click", async () => {
    const selectedItems = Array.from(document.querySelectorAll(".product-qty"))
      .filter(input => parseInt(input.value) > 0)
      .map(input => ({ id: input.dataset.pid }));

    if (selectedItems.length === 0) {
      resultDiv.innerHTML = "<p>❗ 請選擇至少一項商品。</p>";
      return;
    }

    const res = await fetch("http://localhost:8000/api/simulate_addon", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: selectedItems })
    });
    const data = await res.json();
    renderRecommendations(data.recommendations);
  });

  function renderCategoryOptions(data) {
    const categories = [...new Set(data.map(p => p.category))];
    categorySelect.innerHTML = `<option value="ALL">全部</option>` +
      categories.map(c => `<option value="${c}">${c}</option>`).join("");
  }

  function renderProductList(products) {
    productListDiv.innerHTML = "";
    products.forEach(p => {
      const card = document.createElement("div");
      card.className = "invoice-card";
      card.innerHTML = `
        <strong>${p.name}</strong>（${p.category}）<br>
        價格：$${p.price}
        <input type="number" class="product-qty" data-pid="${p.id}" min="0" max="5" value="0" style="margin-left:1em; width:60px">
      `;
      productListDiv.appendChild(card);
    });
  }

  function renderRecommendations(list) {
    resultDiv.innerHTML = "<h3>✨ 推薦加購：</h3>" +
      list.map(r => `<div class='item-line'>${r.name}（分數：${r.score}）</div>`).join("");
  }
});
