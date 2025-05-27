// cart_simulation.js

const API_BASE = 'http://localhost:8000/api';

let products = [];
let discounts = [];
let cart = {};

// DOM 元素
const catFilter      = document.getElementById('categoryFilter');
const discountFilter = document.getElementById('discountFilter');
const productList    = document.getElementById('productList');
const cartItemsEl    = document.getElementById('cartItems');
const resultContainer= document.getElementById('simulationResult');
const submitBtn      = document.getElementById('submitCart');

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

function populateFilters() {
  // 分類
  catFilter.innerHTML = '<option value="">全部</option>';
  [...new Set(products.map(p => p.category))].forEach(cat =>
    catFilter.append(new Option(cat, cat))
  );
  catFilter.onchange = renderProducts;

  // 折扣類型
  discountFilter.innerHTML = '<option value="">全部</option>';
  [...new Set(discounts.map(d => d.type))].forEach(type =>
    discountFilter.append(new Option(type, type))
  );
  discountFilter.onchange = renderProducts;
}

function renderProducts() {
  productList.innerHTML = '';
  const selCat = catFilter.value;
  const selType = discountFilter.value;

  // 建立「折扣類型對應的商品 ID 集合」
  let discountItems = new Set();
  if (selType) {
    discounts
      .filter(d => d.type === selType)
      .forEach(d => {
        // 如果是品項折扣（滿件、組合、獨立）直接取 d.items
        if (Array.isArray(d.items)) {
          d.items.forEach(id => discountItems.add(id));
        }
        // 如果是分類/滿額折扣，用 d.category 全包
        if (d.category) {
          products
            .filter(p => p.category === d.category)
            .forEach(p => discountItems.add(p.id));
        }
      });
  }

  products
    .filter(p =>
      (!selCat || p.category === selCat) &&
      (!selType || discountItems.has(p.id))
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
    btn.onclick = () => {
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

  // ——— 呼叫 /cart_summary 拆帳 ———
  const fd = new FormData();
  fd.append('file',
    new Blob([JSON.stringify({ items })], { type: 'application/json' }),
    'cart.json'
  );
  let invoices;
  try {
    const resp = await fetch(`${API_BASE}/cart_summary`, { method: 'POST', body: fd });
    invoices = await resp.json();
  } catch (e) {
    console.error('拆帳錯誤', e);
    return;
  }

  // 顯示發票數
  const header = document.createElement('h3');
  header.textContent = `📄 本次共產生 ${invoices.length} 張發票`;
  resultContainer.append(header);

  // 顯示每張發票明細
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
      const no = document.createElement('div');
      no.textContent = '此發票未享有任何折扣';
      resultContainer.append(no);
    }
  });

  // ——— 呼叫 /simulate_addon 加購推薦 ———
  try {
    const resp2 = await fetch(`${API_BASE}/simulate_addon`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items })
    });
    const addonData = await resp2.json();

    const addonSec = document.createElement('div');
    addonSec.innerHTML = '<h3>🔎 加購推薦</h3>';
    addonData.recommendations.forEach(r => {
      const line = document.createElement('div');
      line.textContent = `${r.name}：加購得分 ${r.score}`;
      addonSec.append(line);
    });
    resultContainer.append(addonSec);
  } catch (e) {
    console.error('加購推薦錯誤', e);
  }
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
