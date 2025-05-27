// cart_simulation.js
const API_BASE = 'http://localhost:8000/api';

let products = [], discounts = [], cart = {};

const catFilter       = document.getElementById('categoryFilter');
const discountFilter  = document.getElementById('discountFilter');
const productList     = document.getElementById('productList');
const cartItemsEl     = document.getElementById('cartItems');
const resultContainer = document.getElementById('simulationResult');
const submitBtn       = document.getElementById('submitCart');

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
  catFilter.innerHTML = '<option value="">全部</option>';
  [...new Set(products.map(p => p.category))]
    .forEach(c => catFilter.append(new Option(c, c)));
  catFilter.onchange = renderProducts;

  discountFilter.innerHTML = '<option value="">全部</option>';
  [...new Set(discounts.map(d => d.type))]
    .forEach(t => discountFilter.append(new Option(t, t)));
  discountFilter.onchange = renderProducts;
}

function renderProducts() {
  productList.innerHTML = '';
  const selCat = catFilter.value, selType = discountFilter.value;

  // 折扣類型相關商品集合
  let discountItems = new Set();
  if (selType) {
    discounts.filter(d => d.type === selType).forEach(d => {
      if (Array.isArray(d.items)) {
        d.items.forEach(id => discountItems.add(id));
      }
      if (d.category) {
        products.filter(p => p.category===d.category)
                .forEach(p=>discountItems.add(p.id));
      }
    });
  }

  products
    .filter(p =>
      (!selCat || p.category===selCat) &&
      (!selType || discountItems.has(p.id))
    )
    .forEach(p => {
      const qty = cart[p.id]||0;
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
      cart[id] = (cart[id]||0) + (op==='+'?1:-1);
      if (cart[id]<1) delete cart[id];
      document.getElementById(`qty-${id}`).textContent = cart[id]||0;
      renderCartItems();
    };
  });
}

async function renderCartItems() {
  cartItemsEl.innerHTML = '';
  Object.entries(cart).forEach(([id,qty]) => {
    const p = products.find(x=>x.id===id);
    const line = document.createElement('div');
    line.textContent = `🛒 ${p.name} × ${qty} = $${p.price*qty}`;
    cartItemsEl.append(line);
  });
  await updateSimulation();
}

async function updateSimulation() {
  resultContainer.innerHTML = '';
  const items = Object.entries(cart).map(([id,qty])=>{
    const p = products.find(x=>x.id===id);
    return {id,price:p.price,category:p.category};
  });
  if (!items.length) return;

  // -- 拆帳 API --
  const fd = new FormData();
  fd.append('file',
    new Blob([JSON.stringify({items})],{type:'application/json'}),
    'cart.json'
  );
  let invoices;
  try {
    const resp = await fetch(`${API_BASE}/cart_summary`, {
      method:'POST', body:fd, mode:'cors'
    });
    invoices = await resp.json();
  } catch(e) {
    resultContainer.textContent = '❌ 拆帳請求失敗';
    console.error(e);
    return;
  }

  // --- 顯示發票數與明細 ---
  const h = document.createElement('h3');
  h.textContent = `📄 共產生 ${invoices.length} 張發票`;
  resultContainer.append(h);

  invoices.forEach((inv,idx)=>{
    // 1. 列出該發票的商品
    const itemWrap = document.createElement('div');
    itemWrap.className = 'invoice-items';
    itemWrap.innerHTML = `<strong>發票 ${idx+1} 商品：</strong>`;
    inv.items.forEach(i=>{
      const el = document.createElement('div');
      el.textContent = `– ${i.name||i.id}  $${i.price}`;
      itemWrap.append(el);
    });
    resultContainer.append(itemWrap);

    // 2. 小計 & 折扣
    const sub = document.createElement('div');
    sub.className = 'invoice-summary';
    sub.innerHTML = `<strong>小計：$${inv.result.final_price}</strong>`;
    resultContainer.append(sub);

    if (inv.result.used_discounts.length) {
      inv.result.used_discounts.forEach(d=>{
        const dl = document.createElement('div');
        dl.className = 'discount-summary';
        dl.textContent = `[${d.id}] ${d.type}: -$${d.amount} (${d.description})`;
        resultContainer.append(dl);
      });
    } else {
      const none = document.createElement('div');
      none.textContent = '– 無折扣';
      resultContainer.append(none);
    }
  });

  // -- 加購推薦 API --
    // —— 呼叫 02 頁面同樣的「recommend_addon」——
  const fd2 = new FormData();
  fd2.append(
    'file',
    new Blob([JSON.stringify({ items })], { type: 'application/json' }),
    'cart.json'
  );
  let recJson;
  try {
    const resp2 = await fetch(`${API_BASE}/recommend_addon`, {
      method: 'POST',
      body: fd2,
      mode: 'cors'
    });
    recJson = await resp2.json();
  } catch (e) {
    console.error('加購推薦請求失敗', e);
    const errEl = document.createElement('div');
    errEl.style.color = 'red';
    errEl.textContent = '❌ 即時加購推薦失敗';
    resultContainer.append(errEl);
    return;
  }

  // 顯示唯一的「推薦加購商品」
  const addonSection = document.createElement('div');
  addonSection.innerHTML = '<h3>🔎 AI 加購推薦</h3>';
  if (recJson.addon_id) {
    // 從 products 裡找出名稱
    const prod = products.find(p => p.id === recJson.addon_id);
    const name = prod ? prod.name : recJson.addon_id;
    addonSection.append(document.createTextNode(`✨ 建議加購：${name}`));
  } else {
    addonSection.append(document.createTextNode('😕 暫無加購建議'));
  }
  resultContainer.append(addonSection);
}

submitBtn.onclick = async () => {
  const items = Object.entries(cart).map(([id,qty])=>{
    const p = products.find(x=>x.id===id);
    return {id,price:p.price,category:p.category};
  });
  const resp = await fetch(`${API_BASE}/save_simulation`,{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({items})
  });
  const r = await resp.json();
  alert(`✅ 已存檔：${r.file}`);
};
