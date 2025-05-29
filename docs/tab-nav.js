// tab-nav.js
document.addEventListener('DOMContentLoaded', () => {
  // 取得当前文件名
  const page = location.pathname.split('/').pop();
  document.querySelectorAll('.tab-nav a').forEach(a => {
    if (a.getAttribute('href') === page) {
      a.classList.add('active');
    }
  });
});