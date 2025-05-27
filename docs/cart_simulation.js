// cart_simulation.js

// —— 1. 设置你的后端 API 基础 URL ——
// 本地调试时：
const API_BASE = 'http://localhost:8000/api';
// 上线后改成你的线上地址即可
// const API_BASE = 'https://your-domain.com/api';

let products = [];
let discounts = [];
let cart = {}; // { productId: quantity }

// DOM 參考
const catFilter      = document.getElementById('categoryFilter');
const productList    = document.getElementById('productList');
const submitBtn      = document.getElementById('submitCart');
const resultContainer= document.getElementById('simulationResult');

// —— 2. 初始化：抓產品 & 折扣 —— 
async function init() {
  [products, discounts] = await Promise.all([
    fetch(`${API_BASE}/products`).then(r => r.json()),
    fetch(`${API_BASE}/discounts`).then(r => r.json())
  ]);

  // 填充「分類」下拉
  catFilter.innerHTML = '<option value="">全部</option>';
  Array.from(new Set(products.map(p => p.category)))
       .forEach(cat => {
         const o = document.createElement('option');
         o.value = cat; o.textContent = cat;
         catFilter.append(o);
       });

  // 監聽分類變動
  catFilter.addEventListener('change', renderProducts);

  // 第一次渲染
  renderProducts();
}

init();

// —— 3. 根據篩選與購物車，渲染產品卡片 —— 
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

  // 綁定＋／−按鈕
  document.querySelectorAll('.qty-btn').forEach(btn => {
    btn.onclick = () => {
      const id = btn.dataset.id, op = btn.dataset.op;
      cart[id] = cart[id] || 0;
      cart[id] += (op === '+' ? 1 : -1);
      if (cart[id] < 1) delete cart[id];
      document.getElementById(`qty-${id}`).textContent = cart[id] || 0;
    };
  });
}

// —— 4. 點「提交」呼叫拆帳 API，並把結果印到畫面 —— 
submitBtn.addEventListener('click', async () => {
  resultContainer.innerHTML = '';

  // 組出要傳給後端的 items list（不傳 qty，因為拆帳算法只看 price）
  const items = Object.entries(cart).map(([id, qty]) => {
    const p = products.find(x => x.id === id);
    return { id, price: p.price, category: p.category };
  });

  // 用 FormData 包成 file 上傳給 FastAPI
  const fd = new FormData();
  fd.append('file',
    new Blob([JSON.stringify({ items })], { type: 'application/json' }),
    'cart.json'
  );

  // 呼叫 /api/cart_summary
  const resp = await fetch(`${API_BASE}/cart_summary`, {
    method: 'POST',
    body: fd
  });
  const invoices = await resp.json();

  // 渲染每張發票結果
  invoices.forEach((inv, idx) => {
    const sub = document.createElement('div');
    sub.innerHTML = `<strong>發票 ${idx+1} 小計：$${inv.result.final_price}</strong>`;
    resultContainer.append(sub);

    inv.result.used_discounts.forEach(d => {
      const ddiv = document.createElement('div');
      ddiv.className = 'discount-summary';
      ddiv.textContent = `[${d.id}] ${d.type}: -$${d.amount} (${d.description})`;
      resultContainer.append(ddiv);
    });
  });
});
