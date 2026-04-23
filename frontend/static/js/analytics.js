
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const data = await Utils.apiGet('/api/analytics/dashboard');
    const d = data.data || {};

    document.querySelector('#totalSearches .stat-value').textContent =
      (d.total_searches || 0).toLocaleString();
    document.querySelector('#totalProducts .stat-value').textContent =
      (d.product_stats?.total || 0).toLocaleString();
    document.querySelector('#totalCategories .stat-value').textContent =
      Object.keys(d.product_stats?.by_category || {}).length;

    const topCats = d.top_categories || [];
    renderBarChart('categoryChart', topCats.map(c => ({
      label: _formatCatName(c._id),
      value: c.count
    })));

    const priceData = d.price_distribution || [];
    renderBarChart('priceChart', priceData.map(p => ({
      label: typeof p._id === 'string' ? p._id : _formatPriceBucket(p._id),
      value: p.count
    })));


    const platData = d.product_stats?.by_platform || {};
    renderDonutChart('platformChart', Object.entries(platData).map(([k, v]) => ({
      label: Utils.getPlatformLabel(k),
      value: v,
      color: k === 'shopee' ? '#ee4d2d' : k === 'tiki' ? '#1a94ff' : '#f57820'
    })));

    const catData = d.product_stats?.by_category || {};
    renderBarChart('productCatChart', Object.entries(catData)
      .sort((a, b) => b[1] - a[1])
      .map(([k, v]) => ({ label: k, value: v }))
    );

    if (!topCats.length && !priceData.length) {
      document.getElementById('categoryChart').innerHTML =
        '<p style="color:var(--text-muted);font-size:0.82rem;padding:8px">Chưa có dữ liệu tìm kiếm. Hãy bắt đầu chat!</p>';
      document.getElementById('priceChart').innerHTML =
        '<p style="color:var(--text-muted);font-size:0.82rem;padding:8px">Chưa có dữ liệu giá cả.</p>';
    }

  } catch (err) {
    console.error('Analytics error:', err);
  }
});

function renderBarChart(containerId, items) {
  const container = document.getElementById(containerId);
  if (!items || items.length === 0) {
    container.innerHTML = '<p style="color:var(--text-muted);font-size:0.82rem">Chưa có dữ liệu</p>';
    return;
  }
  const max = Math.max(...items.map(i => i.value), 1);
  container.innerHTML = items.slice(0, 8).map(item => `
    <div class="bar-item">
      <span class="bar-label" title="${item.label}">${item.label}</span>
      <div class="bar-track">
        <div class="bar-fill" style="width:${(item.value / max * 100).toFixed(1)}%"></div>
      </div>
      <span class="bar-count">${item.value}</span>
    </div>
  `).join('');
}

function renderDonutChart(containerId, items) {
  const container = document.getElementById(containerId);
  if (!items || items.length === 0) {
    container.innerHTML = '<p style="color:var(--text-muted);font-size:0.82rem">Chưa có dữ liệu</p>';
    return;
  }
  const total = items.reduce((s, i) => s + i.value, 0);
  container.innerHTML = items.map(item => `
    <div class="donut-item">
      <div class="donut-color" style="background:${item.color}"></div>
      <span class="donut-label">${item.label}</span>
      <span class="donut-value">${item.value} (${Math.round(item.value/total*100)}%)</span>
    </div>
  `).join('');
}

function _formatCatName(catId) {
  const map = {
    'dien-thoai': 'Điện thoại', 'laptop': 'Laptop', 'tai-nghe': 'Tai nghe',
    'gia-dung': 'Gia dụng', 'my-pham': 'Mỹ phẩm', 'sach': 'Sách',
    'giay-dep': 'Giày dép', 'dong-ho-thong-minh': 'Đồng hồ thông minh',
    'phu-kien-may-tinh': 'Phụ kiện máy tính', 'thuc-pham': 'Thực phẩm',
    'thoi-trang-nam': 'Thời trang nam'
  };
  return map[catId] || catId;
}

function _formatPriceBucket(id) {
  if (typeof id === 'number') {
    if (id === 0) return 'Dưới 500k';
    return Utils.formatPrice(id) + '+';
  }
  return String(id);
}