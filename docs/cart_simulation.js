// cart_simulation.js

const API_BASE = 'http://localhost:8000/api';

let products = [];
let discounts = [];
let cart = {};

// DOM 元素
const catFilter = document.getElementById('categoryFilter');
const discountFilter = document.getElementById('discountFilter');
const productList = document.getElementById('productList');
const cartItemsEl = document.getElementById('cartItems');
const resultContainer = document.getElementById('simulationResult');
const submitBtn = document.getElementById('submitCart');

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

// 填充分類與折扣類型
function populateFilters() {
  catFilter.innerHTML = '<option value="">全部</option>';
  [...new Set(products.map(p => p.category))].forEach(cat => {
    catFilter.append(new Option(cat, cat));
  });
  catFilter.onchange = renderProducts;

  discountFilter.innerHTML = '<option value="">全部</option>';
  [...new Set(discounts.map(d => d.type))].forEach(type => {
    discountFilter.append(new Option(type, type));
  });
  discountFilter.onchange = renderProducts;
}

function renderProducts() {
  productList.innerHTML = '';
  const selCat = catFilter.value;
  const selDiscountType = discountFilter.value;

  // 找到該折扣類型涉及的商品ID
  let discountItems = null;
  if (selDiscountType) {
    discountItems = new Set();
    discounts
      .filter(d => d.type === selDiscountType)
      .forEach(d => {
        if (d.items) d.items.forEach(id => discountItems.add(id));
      });
  }

  products
    .filter(p =>
      (!selCat || p.category === selCat) &&
      (!selDiscountType || (discountItems && discountItems.has(p.id)))
    )
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

  bindQtyButtons();
}

function bindQtyButtons() {
  document.querySelectorAll('.qty-btn').forEach(btn => {
    btn.onclick = async () => {
      const id = btn.dataset.id, op = btn.dataset.op;
      cart[id] = (cart[id] || 0) + (op === '+' ? 1 : -1);
      if (cart[id] < 1) delete cart[id];
      document.getElementById(`qty-${id}`).textContent = cart[id] || 0;
      renderCartItems();
    };
  });
}

async function renderCartItems() {
  cartItemsEl.innerHTML = '';
  Object.entries(cart).forEach(([id, qty]) => {
    const p = products.find(x => x.id === id);
    const line = document.createElement('div');
    line.textContent = `🛒 ${p.name} × ${qty} = $${p.price * qty}`;
    cartItemsEl.append(line);
  });
  await updateSimulation();
}

async function updateSimulation() {
  resultContainer.innerHTML = '';
  const items = Object.entries(cart).map(([id, qty]) => {
    const p = products.find(x => x.id === id);
    return { id, price: p.price, category: p.category };
  });

  if (items.length === 0) return;

  // 取得拆帳結果
  const fd = new FormData();
  fd.append('file',
    new Blob([JSON.stringify({ items })], { type: 'application/json' }),
    'cart.json'
  );
  const resp = await fetch(`${API_BASE}/cart_summary`, { method: 'POST', body: fd });
  const invoices = await resp.json();

  // 顯示「共幾張發票」
  const header = document.createElement('h3');
  header.textContent = `📄 本次共產生 ${invoices.length} 張發票`;
  resultContainer.append(header);

  // 顯示每張發票的總價與折扣明細
  invoices.forEach((inv, idx) => {
    const sub = document.createElement('div');
    sub.className = 'invoice-summary';
    sub.innerHTML = `<strong>發票 ${idx + 1} 小計：$${inv.result.final_price}</strong>`;
    resultContainer.append(sub);

    if (inv.result.used_discounts.length > 0) {
      inv.result.used_discounts.forEach(d => {
        const dline = document.createElement('div');
        dline.className = 'discount-summary';
        dline.textContent = `[${d.id}] ${d.type}: -$${d.amount} (${d.description})`;
        resultContainer.append(dline);
      });
    } else {
      const noDiscount = document.createElement('div');
      noDiscount.textContent = '此發票未享有任何折扣';
      resultContainer.append(noDiscount);
    }
  });

  // 呼叫即時加購推薦
  const respAddon = await fetch(`${API_BASE}/simulate_addon`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items })
  });
  const addonData = await respAddon.json();

  const addonSection = document.createElement('div');
  addonSection.innerHTML = '<h3>🔎 加購推薦</h3>';
  addonData.recommendations.forEach(r => {
    const line = document.createElement('div');
    line.textContent = `${r.name}：加購得分 ${r.score}`;
    addonSection.append(line);
  });
  resultContainer.append(addonSection);
}

submitBtn.onclick = async () => {
  const items = Object.entries(cart).map(([id, qty]) => {
    const p = products.find(x => x.id === id);
    return { id, price: p.price, category: p.category };
  });
  const resp = await fetch(`${API_BASE}/save_simulation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items })
  });
  const result = await resp.json();
  alert(`✅ 已存檔！檔案名稱：${result.file}`);
};
