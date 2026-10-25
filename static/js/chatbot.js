/**
 * AI Financial Advisor Chatbot Controller
 */

function formatMarkdown(text) {
  if (!text) return '';
  // Basic markdown parser for headings, bold, bullet points, numbers
  let formatted = text
    .replace(/^### (.*$)/gim, '<h4>$1</h4>')
    .replace(/^## (.*$)/gim, '<h3>$1</h3>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^\s*• (.*$)/gim, '<li>$1</li>')
    .replace(/^\s*(\d+)\. (.*$)/gim, '<li><strong>$1.</strong> $2</li>');

  // Wrap contiguous <li> into <ul>
  formatted = formatted.replace(/(<li>.*?<\/li>)+/gs, function(match) {
    return '<ul>' + match + '</ul>';
  });

  // Convert line breaks to paragraphs
  const paragraphs = formatted.split(/\n\s*\n/);
  return paragraphs.map(p => {
    if (p.startsWith('<h3>') || p.startsWith('<h4>') || p.startsWith('<ul>')) return p;
    return `<p>${p.replace(/\n/g, '<br>')}</p>`;
  }).join('');
}

function initChatbot() {
  const drawer = document.getElementById('chatDrawer');
  const triggerBtn = document.getElementById('chatDrawerTrigger');
  const closeBtn = document.getElementById('chatCloseBtn');
  const inputEl = document.getElementById('chatInput');
  const sendBtn = document.getElementById('chatSendBtn');
  const messagesContainer = document.getElementById('chatMessages');

  if (!drawer || !triggerBtn) return;

  triggerBtn.addEventListener('click', () => {
    drawer.classList.toggle('open');
    if (drawer.classList.contains('open')) {
      inputEl.focus();
      scrollToBottom();
    }
  });

  closeBtn.addEventListener('click', () => {
    drawer.classList.remove('open');
  });

  function scrollToBottom() {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  }

  function appendMessage(sender, text) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    if (sender === 'bot') {
      bubble.innerHTML = formatMarkdown(text);
    } else {
      bubble.textContent = text;
    }
    messagesContainer.appendChild(bubble);
    scrollToBottom();
  }

  function showTypingIndicator() {
    const typing = document.createElement('div');
    typing.id = 'botTyping';
    typing.className = 'chat-bubble bot';
    typing.innerHTML = '<span style="opacity: 0.6;">Thinking & crunching your financial data...</span>';
    messagesContainer.appendChild(typing);
    scrollToBottom();
    return typing;
  }

  async function sendMessage(msgText) {
    const text = msgText || inputEl.value.trim();
    if (!text) return;

    appendMessage('user', text);
    if (!msgText) inputEl.value = '';

    const typingIndicator = showTypingIndicator();

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await response.json();

      if (typingIndicator && typingIndicator.parentNode) {
        typingIndicator.parentNode.removeChild(typingIndicator);
      }

      if (data.reply) {
        appendMessage('bot', data.reply);
      } else if (data.error) {
        appendMessage('bot', `⚠️ ${data.error}`);
      }
    } catch (err) {
      if (typingIndicator && typingIndicator.parentNode) {
        typingIndicator.parentNode.removeChild(typingIndicator);
      }
      appendMessage('bot', '⚠️ Connection error. Please verify the backend server is running.');
    }
  }

  sendBtn.addEventListener('click', () => sendMessage());
  inputEl.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  });

  // Prompt chips
  document.querySelectorAll('.chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const prompt = btn.getAttribute('data-prompt');
      if (prompt) {
        if (!drawer.classList.contains('open')) {
          drawer.classList.add('open');
        }
        sendMessage(prompt);
      }
    });
  });

  // Load chat history
  loadChatHistory();
}

async function loadChatHistory() {
  const container = document.getElementById('chatMessages');
  if (!container) return;
  try {
    const res = await fetch('/api/chat/history');
    const data = await res.json();
    if (data.messages && data.messages.length > 0) {
      container.innerHTML = '';
      data.messages.forEach(m => {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${m.sender}`;
        if (m.sender === 'bot') {
          bubble.innerHTML = formatMarkdown(m.message);
        } else {
          bubble.textContent = m.message;
        }
        container.appendChild(bubble);
      });
      container.scrollTop = container.scrollHeight;
    }
  } catch (e) {
    console.error('Error loading chat history:', e);
  }
}
