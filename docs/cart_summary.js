// cart_summary.js

//helper：把 type 转成合法 class 名
function slugify(str) {
  return str
    .replace(/[^\w\u4e00-\u9fa5]/g, '')
    .replace(/\s+/g, '-');
}

document.getElementById('cartFile').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  // 上傳並呼叫後端
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch('http://localhost:8000/api/cart_summary', {
    method: 'POST',
    body: formData
  });
  const invoices = await res.json();

  // 清空畫面
  const container = document.getElementById('result');
  container.innerHTML = '';

  // 逐張發票
  invoices.forEach((invoice, idx) => {
    const card = document.createElement('div');
    card.className = 'invoice-card';

    // 標題
    const title = document.createElement('h3');
    title.textContent = `發票 ${idx + 1}`;
    card.appendChild(title);

    // 商品
    invoice.items.forEach(item => {
      const row = document.createElement('div');
      row.className = 'item-line';
      row.textContent = `🛒 ${item.name || item.id} × 1 = $${item.price ?? 0}`;
      card.appendChild(row);
    });

    // 折扣區塊標題
    const used = invoice.result?.used_discounts || [];
    if (used.length > 0) {
      const hdr = document.createElement('div');
      hdr.className = 'discount-header';
      hdr.textContent = '折扣：';
      card.appendChild(hdr);

      // 每筆折扣一行，並依 type 上色
      used.forEach(d => {
        const line = document.createElement('div');
        const typeClass = slugify(d.type);
        line.classList.add('discount-summary', typeClass);
        line.textContent = `折扣： -$${d.amount ?? 0} [${d.id}] ${d.type}：${d.description}`;
        card.appendChild(line);
      });
    }

    // 小計
    const sub = document.createElement('div');
    sub.className = 'total';
    sub.textContent = `小計：$${invoice.result?.final_price ?? 0}`;
    card.appendChild(sub);

    container.appendChild(card);
  });

  // 結帳總覽
    const originalSum = invoices.reduce((s, inv) => s + (inv.result?.original_total ?? 0), 0);
    const discountSum = invoices.reduce((s, inv) => s + (inv.result?.total_discount ?? 0), 0);
    const finalSum    = invoices.reduce((s, inv) => s + (inv.result?.final_price ?? 0), 0);

    const summary = document.createElement('div');
    summary.className = 'summary-card';
    summary.innerHTML = `
    <h3>🧮 結帳總覽</h3>
    <div class="summary-line">💵 原始總金額：$${originalSum}</div>
    <div class="summary-line">🎁 折扣總金額：- $${discountSum}</div>
    <div class="summary-line">💰 最終付款金額：$${finalSum}</div>
    `;
    container.appendChild(summary);
});
