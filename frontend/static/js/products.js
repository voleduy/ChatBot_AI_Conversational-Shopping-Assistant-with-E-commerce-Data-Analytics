
const Products = {
  currentProducts: [],

  renderPanel(products) {
    this.currentProducts = products;
    const list = document.getElementById('productList');
    
    if (!products || products.length === 0) {
      list.innerHTML = `
        <div class="panel-empty">
          <span> ... </span>
          <p>Không tìm thấy sản phẩm phù hợp</p>
        </div>`;
      return;
    }

    list.innerHTML = products.map(p => this._renderCard(p)).join('');
  },

  _renderCard(p) {
    const discount = Utils.getDiscountPercent(p.price, p.original_price);
    const platClass = Utils.getPlatformClass(p.platform);
    const platLabel = Utils.getPlatformLabel(p.platform);
    const trust = Utils.getSellerTrustLabel(p.seller);
    const stars = Utils.renderStars(p.product_rating || 0);

    return `
      <a href="/product/${p.id}" target="_blank" class="product-card" data-id="${p.id}">
        <div class="product-card-header">
          <div class="product-thumb">
            <img 
              src="${p.images?.[0] || ''}" 
              alt="${Utils.escapeHtml(p.name)}"
              onerror="this.parentElement.innerHTML='Box'"
              loading="lazy"
            />
          </div>
          <div class="product-card-info">
            <div class="product-card-name">${Utils.escapeHtml(p.name)}</div>
            <span class="product-card-platform ${platClass}">${platLabel}</span>
          </div>
        </div>
        
        <div class="product-card-price">
          ${Utils.formatPrice(p.price)}
          ${p.original_price > p.price 
            ? `<span class="product-card-original">${Utils.formatPrice(p.original_price)}</span>` 
            : ''}
          ${discount > 0 ? `<span style="font-size:0.7rem;background:rgba(255,107,107,0.15);color:#ff6b6b;padding:1px 5px;border-radius:4px;margin-left:4px">-${discount}%</span>` : ''}
        </div>
        
        <div class="product-card-rating">
          <span class="stars">${stars}</span>
          <span>${p.product_rating?.toFixed(1) || 0}</span>
          <span style="color:var(--text-muted)">(${(p.review_count || 0).toLocaleString()})</span>
        </div>
        
        <div class="seller-trust">${trust}</div>
        
        ${p.ai_reason ? `<div class="ai-reason">Lý do ${Utils.escapeHtml(p.ai_reason)}</div>` : ''}
        
        <span class="product-card-cta">Xem chi tiết →</span>
      </a>
    `;
  },

  openPanel() {
    const panel = document.getElementById('productPanel');
    panel.classList.add('open');
  },

  closePanel() {
    const panel = document.getElementById('productPanel');
    panel.classList.remove('open');
  },

  clearPanel() {
    const list = document.getElementById('productList');
    list.innerHTML = `
      <div class="panel-empty">
        <span> ... </span>
        <p>Kết quả sẽ hiển thị khi bạn tìm kiếm sản phẩm</p>
      </div>`;
    this.currentProducts = [];
  }
};

window.Products = Products;