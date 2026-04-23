// ===== PRODUCT DETAIL PAGE =====

document.addEventListener('DOMContentLoaded', async () => {
  const main = document.getElementById('detailMain');
  
  try {
    const data = await Utils.apiGet(`/api/products/${productId}`);
    
    if (!data.success || !data.product) {
      main.innerHTML = `<div style="text-align:center;padding:60px;color:var(--text-secondary)">
        <div style="font-size:3rem;margin-bottom:16px">huh ....</div>
        <h2>Không tìm thấy sản phẩm</h2>
        <p style="margin-top:8px;margin-bottom:24px">Sản phẩm có thể đã hết hàng hoặc không tồn tại</p>
        <a href="/" style="color:var(--primary-light);text-decoration:none">← Quay lại tìm kiếm</a>
      </div>`;
      return;
    }

    const p = data.product;
    const discount = Utils.getDiscountPercent(p.price, p.original_price);
    const platClass = Utils.getPlatformClass(p.platform);
    const platLabel = Utils.getPlatformLabel(p.platform);
    const trust = Utils.getSellerTrustLabel(p.seller);
    const stars = Utils.renderStars(p.product_rating || 0);
    const seller = p.seller || {};

    // Specs table
    const specs = p.specs || {};
    const specsRows = Object.entries(specs)
      .map(([k, v]) => `<tr><td>${Utils.escapeHtml(k)}</td><td>${Utils.escapeHtml(String(v))}</td></tr>`)
      .join('');

    // Tags
    const tags = (p.tags || [])
      .map(t => `<span style="padding:3px 8px;background:var(--bg-elevated);border:1px solid var(--border);border-radius:999px;font-size:0.75rem;color:var(--text-secondary)">#${Utils.escapeHtml(t)}</span>`)
      .join('');

    document.title = `${p.name} – ShopBot AI`;

    main.innerHTML = `
      <div class="product-detail-grid">
        
        <!-- Image Section -->
        <div class="product-image-section">
          <img 
            src="${p.images?.[0] || ''}" 
            alt="${Utils.escapeHtml(p.name)}"
            onerror="this.parentElement.innerHTML='Box'"
          />
        </div>

        <!-- Info Section -->
        <div class="product-info-section">
          <span class="product-platform-badge ${platClass}">${platLabel}</span>
          
          <h1 class="product-title">${Utils.escapeHtml(p.name)}</h1>

          <div class="product-price-row">
            <span class="price-current">${Utils.formatPrice(p.price)}</span>
            ${p.original_price > p.price 
              ? `<span class="price-original">${Utils.formatPrice(p.original_price)}</span>
                 <span class="price-discount">-${discount}%</span>`
              : ''}
          </div>

          <div class="product-stats">
            <div class="stat-pill">
              <span class="stars" style="color:#f7971e">${stars}</span>
              <span>${p.product_rating?.toFixed(1) || 0}/5</span>
            </div>
            <div class="stat-pill">
              Đánh giá: ${(p.review_count || 0).toLocaleString()} đánh giá
            </div>
            <div class="stat-pill">
              Hàng đã bán ${(p.sold_count || 0).toLocaleString()}
            </div>
            <div class="stat-pill" style="color:${p.stock > 10 ? 'var(--accent2)' : 'var(--accent)'}">
              ${p.stock > 10 ? '✅' : '⚠️'} Còn ${p.stock} sản phẩm
            </div>
          </div>

          <!-- Seller Card -->
          <div class="seller-card">
            <div class="seller-name">Shop: ${Utils.escapeHtml(seller.name || 'Nhà bán')}</div>
            <div class="seller-meta">
              <span>Rating: ${seller.rating || 0}/5</span>
              <span>Phản hồi: ${seller.response_rate || 0}%</span>
              <span>Đơn hàng: ${(seller.total_sales || 0).toLocaleString()} đơn</span>
              ${seller.verified ? '<span style="color:var(--accent2)">Đã xác thực</span>' : ''}
            </div>
            <div style="margin-top:6px;font-size:0.8rem;color:var(--accent2)">${trust}</div>
          </div>

          <!-- Description -->
          <div>
            <h3 style="font-size:0.9rem;margin-bottom:8px;color:var(--text-secondary)">Mô tả sản phẩm</h3>
            <div class="product-description">${Utils.escapeHtml(p.description || '')}</div>
          </div>

          ${tags ? `<div style="display:flex;flex-wrap:wrap;gap:6px">${tags}</div>` : ''}

          <!-- Buy Button -->
          <button class="btn-buy primary" onclick="alert('Chức năng mua hàng sẽ được kích hoạt sau khi kết nối sàn thật!')">
            Mua ngay trên ${platLabel}
          </button>
          
          <a href="/" class="btn-buy" style="background:var(--bg-elevated);color:var(--primary-light);border:1px solid var(--border-accent)">
            Hỏi thêm AI về sản phẩm này
          </a>
        </div>
      </div>

      <!-- Specs Table -->
      ${specsRows ? `
      <div style="margin-top:32px">
        <h2 style="font-size:1rem;font-weight:600;margin-bottom:16px">📋 Thông số kỹ thuật</h2>
        <table class="specs-table">
          <tbody>${specsRows}</tbody>
        </table>
      </div>
      ` : ''}
    `;

  } catch (err) {
    console.error('Product detail error:', err);
    main.innerHTML = `<div style="text-align:center;padding:60px;color:var(--text-secondary)">
      <div style="font-size:3rem;margin-bottom:16px">⚠️</div>
      <h2>Lỗi tải sản phẩm</h2>
      <p style="margin-top:8px">Không thể kết nối máy chủ</p>
    </div>`;
  }
});