
const Chat = {
  sessionId: null,
  isLoading: false,
  messageCount: 0,

  init() {
    this.sessionId = Utils.getSessionId();
    document.getElementById('sessionInfo').textContent =
      'Phiên: ' + this.sessionId.slice(-8);
  },

  async sendMessage(text) {
    if (this.isLoading || !text.trim()) return;

    this.isLoading = true;
    this._setLoading(true);

    const welcome = document.getElementById('welcomeScreen');
    if (welcome) welcome.classList.add('hidden');

    this._appendMessage('user', text);

    this._showTyping(true);

    try {
      const data = await Utils.apiPost('/api/chat/message', {
        message: text,
        session_id: this.sessionId
      });

      this._showTyping(false);

      if (data.session_id && data.session_id !== this.sessionId) {
        this.sessionId = data.session_id;
        Utils.setSessionId(this.sessionId);
      }

      this._appendMessage('bot', data.reply);

      if (data.products && data.products.length > 0) {
        Products.renderPanel(data.products);
        Products.openPanel();
      }

    } catch (err) {
      this._showTyping(false);
      this._appendMessage('bot', 'Đã xảy ra lỗi kết nối. Vui lòng thử lại.');
      console.error('Chat error:', err);
    } finally {
      this.isLoading = false;
      this._setLoading(false);
    }
  },

  _appendMessage(role, text) {
    const list = document.getElementById('messagesList');
    const msg = document.createElement('div');
    msg.className = `message ${role}`;
    msg.innerHTML = `
      <div class="message-avatar">${role === 'user' ? 'B' : 'ơ...'}</div>
      <div class="message-content">
        <div class="message-bubble">${
          role === 'bot' ? Utils.markdownToHtml(text) : Utils.escapeHtml(text)
        }</div>
        <div class="message-time">${Utils.formatTime(new Date())}</div>
      </div>
    `;
    list.appendChild(msg);
    this._scrollToBottom();
    this.messageCount++;
  },

  _showTyping(show) {
    const el = document.getElementById('typingIndicator');
    el.classList.toggle('hidden', !show);
    if (show) this._scrollToBottom();
  },

  _setLoading(loading) {
    const btn = document.getElementById('sendBtn');
    const input = document.getElementById('chatInput');
    btn.disabled = loading || !input.value.trim();
    input.disabled = loading;
  },

  _scrollToBottom() {
    const container = document.getElementById('messagesContainer');
    setTimeout(() => {
      container.scrollTop = container.scrollHeight;
    }, 50);
  },

  newSession() {
    const newId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    this.sessionId = newId;
    Utils.setSessionId(newId);
    document.getElementById('sessionInfo').textContent = 'Phiên: ' + newId.slice(-8);
    document.getElementById('messagesList').innerHTML = '';
    Products.clearPanel();
    const welcome = document.getElementById('welcomeScreen');
    if (welcome) welcome.classList.remove('hidden');
    this.messageCount = 0;
  }
};

window.Chat = Chat;