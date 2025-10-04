async function sendMessage() {
    const inputField = document.getElementById("user-input");
    const message = inputField.value.trim();
    if (!message) return;
  
    addMessage(message, "user");
    inputField.value = "";
    inputField.style.height = "auto";
  
    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
  
      const data = await response.json();
      addMessage(formatBotMessage(data.reply), "bot");
    } catch (err) {
      addMessage("⚠️ Error connecting to server.", "bot");
    }
  }
  
  // Add message to chat
  function addMessage(text, sender) {
    const chatBox = document.getElementById("chat-box");
    const msg = document.createElement("div");
    msg.classList.add("message", sender);
    msg.innerHTML = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
  }
  
  // Format bot message: handle Markdown and special characters
  function formatBotMessage(text) {
    let html = text
      // Headings: #### → bold
      .replace(/###### (.*)/g, "<b style='font-size:0.9em'>$1</b><br>")
      .replace(/##### (.*)/g, "<b style='font-size:1em'>$1</b><br>")
      .replace(/#### (.*)/g, "<b style='font-size:1.05em'>$1</b><br>")
      .replace(/### (.*)/g, "<b style='font-size:1.1em'>$1</b><br>")
      .replace(/## (.*)/g, "<b style='font-size:1.2em'>$1</b><br>")
      .replace(/# (.*)/g, "<b style='font-size:1.3em'>$1</b><br>")
      // Bold **text**
      .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>")
      // Italics *text*
      .replace(/\*(.*?)\*/g, "<i>$1</i>")
      // Bullets: - item
      .replace(/^\s*-\s+(.*)$/gm, "• $1<br>")
      // Numbered lists: 1. item
      .replace(/^\s*\d+\.\s+(.*)$/gm, "$1<br>")
      // Inline code: `text`
      .replace(/`(.*?)`/g, "<code>$1</code>")
      // Links: [text](url)
      .replace(/\[(.*?)\]\((.*?)\)/g, "<a href='$2' target='_blank'>$1</a>")
      // Line breaks
      .replace(/\n/g, "<br>");
  
    return html;
  }
  
  // Auto-resize textarea
  const textarea = document.getElementById("user-input");
  textarea.addEventListener("input", () => {
    textarea.style.height = "auto";
    textarea.style.height = textarea.scrollHeight + "px";
  });
  