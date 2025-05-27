// cart_simulation.js

// —— 1. 后端 API 基础 URL —— 
const API_BASE = 'http://localhost:8000/api';

let products = [];
let discounts = [];
let cart = {}; // { id: qty, ... }

// DOM 参考
const catFilter       = document.getElementById('categoryFilter');
const productList     = document.getElementById('productList');
const cartItemsEl     = document.getElementById('cartItems');
const submitBtn       = document.getElementById('submitCart');
const resultContainer = document.getElementById('simulationResult');

// —— 2. 初始化：拉产品 & 折扣 —— 
async function init() {
  [products, discounts] = await Promise.all([
    fetch(`${API_BASE}/products`).then(r => r.json()),
    fetch(`${API_BASE}/discounts`).then(r => r.json())
  ]);
  populateFilters();
  renderProducts();
  renderCartItems();
}
init();

// 填充「分類」下拉
function populateFilters() {
  catFilter.innerHTML = '<option value="">全部</option>';
  [...new Set(products.map(p => p.category))]
    .forEach(cat => catFilter.append(new Option(cat, cat)));
  catFilter.onchange = renderProducts;
}

// —— 3. 渲染產品卡片 —— 
function renderProducts() {
  productList.innerHTML = '';
  const selCat = catFilter.value;

  products
    .filter(p => !selCat || p.category === selCat)
    .forEach(p => {
      const qty = cart[p.id] || 0;
      const card = document.createElement('div');
      card.className = 'product-card';
      card.innerHTML = `
        <h4>${p.name}</h4>
        <div>類別：${p.category}</div>
        <div>價格：$${p.price}</div>
        <div class="qty-control">
          <button class="qty-btn" data-id="${p.id}" data-op="-">−</button>
          <span id="qty-${p.id}">${qty}</span>
          <button class="qty-btn" data-id="${p.id}" data-op="+">＋</button>
        </div>
      `;
      productList.append(card);
    });

  // 绑定＋／－
  document.querySelectorAll('.qty-btn').forEach(btn => {
    btn.onclick = () => {
      const id = btn.dataset.id, op = btn.dataset.op;
      cart[id] = (cart[id] || 0) + (op === '+' ? 1 : -1);
      if (cart[id] < 1) delete cart[id];
      document.getElementById(`qty-${id}`).textContent = cart[id] || 0;
      renderCartItems();
    };
  });
}

// —— 4. 渲染「您的購物車」 —— 
function renderCartItems() {
  cartItemsEl.innerHTML = '';
  Object.entries(cart).forEach(([id, qty]) => {
    const p = products.find(x => x.id === id);
    const line = document.createElement('div');
    line.textContent = `🛒 ${p.name} × ${qty} = $${p.price * qty}`;
    cartItemsEl.append(line);
  });
}

// —— 5. Submit 时调用拆帳，渲染结果 —— 
submitBtn.onclick = async () => {
  resultContainer.innerHTML = '';

  // 只传 id／price／category 给后端
  const items = Object.entries(cart).map(([id,qty]) => {
    const p = products.find(x=>x.id===id);
    return { id, price: p.price, category: p.category };
  });

  // 包成 file upload
  const fd = new FormData();
  fd.append('file',
    new Blob([JSON.stringify({ items })], { type: 'application/json' }),
    'cart.json'
  );

  const resp = await fetch(`${API_BASE}/cart_summary`, {
    method: 'POST',
    body: fd
  });
  const invoices = await resp.json();

  // 渲染每張發票
  invoices.forEach((inv, idx) => {
    const sub = document.createElement('div');
    sub.innerHTML = `<strong>發票 ${idx+1} 小計：$${inv.result.final_price}</strong>`;
    resultContainer.append(sub);

    inv.result.used_discounts.forEach(d => {
      const dline = document.createElement('div');
      dline.className = 'discount-summary';
      dline.textContent = `[${d.id}] ${d.type}: -$${d.amount} (${d.description})`;
      resultContainer.append(dline);
    });
  });
};
