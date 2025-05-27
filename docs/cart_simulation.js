// cart_simulation.js

let products = [];
let discounts = [];
let cart = {}; // { productId: quantity, ... }

// DOM 參考
const catFilter = document.getElementById('categoryFilter');
const discFilter = document.getElementById('discountFilter');
const productList = document.getElementById('productList');
const cartItemsEl = document.getElementById('cartItems');
const cartSummaryEl = document.getElementById('cartSummary');
const confirmBtn = document.getElementById('confirmBtn');

// 啟動：拉 products 與 discounts
async function init() {
  [products, discounts] = await Promise.all([
    fetch('/api/products').then(r=>r.json()),
    fetch('/api/discounts').then(r=>r.json())
  ]);
  populateFilters();
  renderProducts();
  renderCart();
}
init();

// 填充 篩選選單
function populateFilters() {
  const cats = Array.from(new Set(products.map(p=>p.category)));
  cats.forEach(c=>{
    const opt = new Option(c, c);
    catFilter.append(opt);
  });

  const types = Array.from(new Set(discounts.map(d=>d.type)));
  types.forEach(t=>{
    const opt = new Option(t, t);
    discFilter.append(opt);
  });

  catFilter.onchange = renderProducts;
  discFilter.onchange = renderProducts;
}

// 根據篩選條件，渲染產品卡片
function renderProducts() {
  productList.innerHTML = '';
  const selCat = catFilter.value;
  const selDisc = discFilter.value;
  products
    .filter(p => !selCat || p.category === selCat)
    // 若選了折扣類型，僅顯示此類商品：檢查 discount_rules 內是否有此 type 作用於該 p.id
    .filter(p => {
      if (!selDisc) return true;
      return discounts.some(d => 
        d.type===selDisc
        && (
          d.product_id===p.id
          || (d.items && d.items.includes(p.id))
          || d.category===p.category
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
    btn.onclick = e => {
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

// 顯示購物車項目
function renderCart() {
  cartItemsEl.innerHTML = '';
  const items = Object.entries(cart).map(([id,qty])=>{
    const p = products.find(x=>x.id===id);
    const line = document.createElement('div');
    line.textContent = `🛒 ${p.name} × ${qty} = $${p.price*qty}`;
    cartItemsEl.append(line);
    return { id, price: p.price, category: p.category, qty };
  });

  // 計算折扣與總價：呼叫後端拆帳 API
  fetch('/api/cart_summary', {
    method: 'POST',
    body: new FormData(Object.entries(cart).reduce((f, [id,qty])=>{
      // FastAPI 接受 UploadFile，所以用 blob 方式
      f.append('file', new Blob([JSON.stringify({ items: items.map(i=>({ id: i.id, price: i.price, category: i.category })) })], { type: 'application/json' }), 'cart.json');
      return f;
    }, new FormData()))
  })
  .then(r => r.json())
  .then(data => {
    // data 是 array of invoices
    cartSummaryEl.innerHTML = '';
    data.forEach((inv,idx) => {
      const sub = document.createElement('div');
      sub.innerHTML = `<strong>發票 ${idx+1} 小計：$${inv.result.final_price}</strong>`;
      cartSummaryEl.append(sub);
      if (inv.result.used_discounts.length) {
        inv.result.used_discounts.forEach(d => {
          const dline = document.createElement('div');
          dline.className = 'discount-summary ' + d.type.replace(/\s+/g,'-');
          dline.textContent = `[${d.id}] ${d.type}: -$${d.amount} (${d.description})`;
          cartSummaryEl.append(dline);
        });
      }
    });
  });

}

// 確認並存檔
confirmBtn.onclick = () => {
  const payload = { items: Object.entries(cart).map(([id,qty])=>({ id, price: products.find(p=>p.id===id).price, category: products.find(p=>p.id===id).category, qty })) };
  fetch('/api/save_simulation', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(r => r.json())
  .then(res => alert(`已儲存到：${res.file}`))
  .catch(() => alert('存檔失敗'));
};
