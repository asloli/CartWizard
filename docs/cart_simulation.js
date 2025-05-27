// cart_simulation.js

// —— 1. 设置你的后端 API 基础 URL ——
// 本地调试时：
const API_BASE = 'http://localhost:8000/api';
// 如果后端已经部署到线上，就改成：
// const API_BASE = 'https://your-backend-domain.com/api';

let products = [];
let discounts = [];
let cart = {}; // { productId: quantity }

// DOM 參考
const catFilter      = document.getElementById('categoryFilter');
const discFilter     = document.getElementById('discountFilter');
const productList    = document.getElementById('productList');
const cartItemsEl    = document.getElementById('cartItems');
const cartSummaryEl  = document.getElementById('cartSummary');
const confirmBtn     = document.getElementById('confirmBtn');

// —— 2. 初始化：抓取產品 & 折扣 —— 
async function init() {
  [products, discounts] = await Promise.all([
    fetch(`${API_BASE}/products`).then(r=>r.json()),
    fetch(`${API_BASE}/discounts`).then(r=>r.json())
  ]);
  populateFilters();
  renderProducts();
  renderCart();
}
init();

// 填充篩選選單
function populateFilters() {
  // 類別
  const cats = [...new Set(products.map(p=>p.category))];
  cats.forEach(c=>{
    catFilter.append(new Option(c, c));
  });
  // 折扣類型
  const types = [...new Set(discounts.map(d=>d.type))];
  types.forEach(t=>{
    discFilter.append(new Option(t, t));
  });

  catFilter.onchange  = renderProducts;
  discFilter.onchange = renderProducts;
}

// 根據篩選條件，渲染產品卡片
function renderProducts() {
  productList.innerHTML = '';
  const selCat  = catFilter.value;
  const selDisc = discFilter.value;

  products
    .filter(p => !selCat  || p.category === selCat)
    .filter(p => {
      if (!selDisc) return true;
      // 這裡判斷這筆產品是否有 selDisc 這類折扣
      return discounts.some(d => 
        d.type === selDisc
        && (
          d.product_id === p.id ||
          (d.items && d.items.includes(p.id)) ||
          d.category === p.category
        )
      );
    })
    .forEach(p => {
      const card = document.createElement('div');
      card.className = 'product-card';
      card.innerHTML = `
        <h4>${p.name}</h4>
        <div>類別：${p.category}</div>
        <div>價格：$${p.price}</div>
        <div class="qty-control">
          <button data-id="${p.id}" data-op="-" class="qty-btn">−</button>
          <span id="qty-${p.id}">${cart[p.id]||0}</span>
          <button data-id="${p.id}" data-op="+" class="qty-btn">＋</button>
        </div>
      `;
      productList.append(card);
    });

  // 綁定＋−事件
  document.querySelectorAll('.qty-btn').forEach(btn=>{
    btn.onclick = () => {
      const id = btn.dataset.id;
      const op = btn.dataset.op;
      cart[id] = cart[id]||0;
      cart[id] += (op==='+'?1:-1);
      if (cart[id] <= 0) delete cart[id];
      document.getElementById(`qty-${id}`).textContent = cart[id]||0;
      renderCart();
    };
  });
}

// 顯示購物車項目 + 呼叫拆帳 API
function renderCart() {
  cartItemsEl.innerHTML = '';
  // 組成 items list
  const items = Object.entries(cart).map(([id,qty])=>{
    const p = products.find(x=>x.id===id);
    const div = document.createElement('div');
    div.textContent = `🛒 ${p.name} × ${qty} = $${p.price * qty}`;
    cartItemsEl.append(div);
    return { id, price: p.price, category: p.category, qty };
  });

  // 呼叫後端拆帳
  const fd = new FormData();
  // FastAPI 這個接口期望一個 file 上傳，因此我們包成 blob
  fd.append('file',
    new Blob(
      [JSON.stringify({ items })],
      { type: 'application/json' }
    ),
    'cart.json'
  );

  fetch(`${API_BASE}/cart_summary`, {
    method: 'POST',
    body: fd
  })
  .then(r => r.json())
  .then(data => {
    cartSummaryEl.innerHTML = '';
    data.forEach((inv, idx) => {
      const sub = document.createElement('div');
      sub.innerHTML = `<strong>發票 ${idx+1} 小計：$${inv.result.final_price}</strong>`;
      cartSummaryEl.append(sub);
      inv.result.used_discounts.forEach(d => {
        const dline = document.createElement('div');
        dline.className = 'discount-summary ' + d.type.replace(/\s+/g,'-');
        dline.textContent = `[${d.id}] ${d.type}: -$${d.amount} (${d.description})`;
        cartSummaryEl.append(dline);
      });
    });
  });
}

// 確認並存檔
confirmBtn.onclick = () => {
  const payload = {
    items: Object.entries(cart).map(([id,qty])=>({
      id, qty,
      price: products.find(p=>p.id===id).price,
      category: products.find(p=>p.id===id).category
    }))
  };
  fetch(`${API_BASE}/save_simulation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(r => r.json())
  .then(res => alert(`已儲存到：${res.file}`))
  .catch(() => alert('存檔失敗'));
};
