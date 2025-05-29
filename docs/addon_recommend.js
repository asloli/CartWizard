// helper：把 type 轉成合法 class 名
function slugify(str) {
  return str
    .replace(/[^\w\u4e00-\u9fa5]/g, '')
    .replace(/\s+/g, '-');
}

// 上傳並呼叫 /api/recommend_addon
document.getElementById('addonFile').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch('http://localhost:8000/api/recommend_addon', {
    method: 'POST',
    body: formData
  });
  const data = await res.json();
  const { addon_id, before, after } = data;

  // 清空
  const orig = document.getElementById('originalResult');
  const rec  = document.getElementById('recommendResult');
  orig.innerHTML = '';
  rec.innerHTML  = '';

  // 顯示建議加購商品
  const header = document.createElement('h3');
  header.textContent = `🔔 建議加購商品：${addon_id}`;
  rec.appendChild(header);

  //共用渲染函式
  function renderInvoices(invoices, container, title) {
    const t = document.createElement('h4');
    t.textContent = title;
    container.appendChild(t);

    invoices.forEach((inv, idx) => {
      const card = document.createElement('div');
      card.className = 'invoice-card';
      // 發票標題
      const h = document.createElement('h5');
      h.textContent = `發票 ${idx + 1}`;
      card.appendChild(h);

      // 商品
      inv.items.forEach(item => {
        const row = document.createElement('div');
        row.className = 'item-line';
        row.textContent = `🛒 ${item.name || item.id} × 1 = $${item.price ?? 0}`;
        card.appendChild(row);
      });

      // 折扣
      const used = inv.result?.used_discounts || [];
      if (used.length > 0) {
        const hdr = document.createElement('div');
        hdr.className = 'discount-header';
        hdr.textContent = '折扣：';
        card.appendChild(hdr);

        used.forEach(d => {
          const line = document.createElement('div');
          const cls = slugify(d.type);
          line.className = `discount-summary ${cls}`;
          line.textContent = `折扣： -$${d.amount ?? 0} [${d.id}] ${d.type}：${d.description}`;
          card.appendChild(line);
        });
      }

      // 小計
      const sub = document.createElement('div');
      sub.className = 'total';
      sub.textContent = `小計：$${inv.result?.final_price ?? 0}`;
      card.appendChild(sub);

      container.appendChild(card);
    });
  }

  // 渲染「加購前」與「加購後」
  renderInvoices(before, orig, '▶️ 加購前發票拆帳');
  renderInvoices(after,  rec,  '▶️ 加購後發票拆帳');
});