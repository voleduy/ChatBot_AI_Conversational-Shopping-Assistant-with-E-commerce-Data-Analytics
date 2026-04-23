
document.addEventListener('DOMContentLoaded', () => {
  Chat.init();

  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const charCount = document.getElementById('charCount');

  input.addEventListener('input', () => {
    const len = input.value.length;
    charCount.textContent = `${len}/1000`;
    sendBtn.disabled = !input.value.trim() || Chat.isLoading;

    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitMessage();
    }
  });

  sendBtn.addEventListener('click', submitMessage);

  function submitMessage() {
    const text = input.value.trim();
    if (!text || Chat.isLoading) return;
    input.value = '';
    input.style.height = 'auto';
    charCount.textContent = '0/1000';
    sendBtn.disabled = true;
    Chat.sendMessage(text);
  }

  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const msg = chip.dataset.msg;
      input.value = msg;
      input.dispatchEvent(new Event('input'));
      input.focus();
      setTimeout(submitMessage, 150);
    });
  });

  document.getElementById('newChatBtn')?.addEventListener('click', () => {
    Chat.newSession();
  });

  document.getElementById('mobileSidebarToggle')?.addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
  });

  document.getElementById('sidebarToggle')?.addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
  });

  document.getElementById('panelClose')?.addEventListener('click', () => {
    Products.closePanel();
  });

  document.getElementById('modalClose')?.addEventListener('click', () => {
    document.getElementById('productModal').classList.add('hidden');
  });

  document.getElementById('productModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'productModal') {
      document.getElementById('productModal').classList.add('hidden');
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.getElementById('productModal')?.classList.add('hidden');
      document.getElementById('sidebar')?.classList.remove('open');
    }
  });

  input.focus();
});