
const Utils = {
  formatPrice(price) {
    if (price >= 1_000_000) {
      const m = price / 1_000_000;
      return m % 1 === 0 ? `${m} triệu đ` : `${m.toFixed(1)} triệu đ`;
    }
    if (price >= 1000) {
      return price.toLocaleString('vi-VN') + 'đ';
    }
    return `${price}đ`;
  },

  formatTime(date) {
    const d = date instanceof Date ? date : new Date(date);
    return d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
  },

  escapeHtml(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
  },

  markdownToHtml(text) {
    return text
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/`(.+?)`/g, '<code>$1</code>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>')
      .replace(/^/, '<p>')
      .replace(/$/, '</p>');
  },

  getPlatformClass(platform) {
    const map = { shopee: 'plat-shopee', tiki: 'plat-tiki', lazada: 'plat-lazada' };
    return map[platform?.toLowerCase()] || 'plat-shopee';
  },

  getPlatformLabel(platform) {
    const map = { shopee: 'Shopee', tiki: 'Tiki', lazada: 'Lazada' };
    return map[platform?.toLowerCase()] || platform;
  },

  getSellerTrustLabel(seller) {
    if (!seller) return '';
    const { rating = 0, verified = false } = seller;
    if (rating >= 4.8 && verified) return ' Nhà bán uy tín cao';
    if (rating >= 4.5) return 'Nhà bán tin cậy';
    if (rating >= 4.0) return 'Nhà bán tốt';
    return 'Nhà bán mới';
  },

  renderStars(rating) {
    const full = Math.floor(rating);
    const half = rating - full >= 0.5;
    let stars = '★'.repeat(full);
    if (half) stars += '½';
    return stars;
  },

  getDiscountPercent(price, original) {
    if (!original || original <= price) return 0;
    return Math.round((original - price) / original * 100);
  },

  debounce(fn, delay) {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
  },

  getSessionId() {
    let id = localStorage.getItem('shopbot_session_id');
    if (!id) {
      id = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('shopbot_session_id', id);
    }
    return id;
  },

  setSessionId(id) {
    localStorage.setItem('shopbot_session_id', id);
  },

  async apiPost(url, data) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },

  async apiGet(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }
};

window.Utils = Utils;