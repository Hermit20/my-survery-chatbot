const chatLog = document.getElementById("chat-log");
const messageInput = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const endBtn = document.getElementById("end-btn");

/**
 * Render a message to the chat log
 * @param {String} speaker - "User" or "Assistant"
 * @param {String} text - Message text
 */
function renderMessage(speaker, text) {
  const div = document.createElement("div");
  div.classList.add("message");
  div.classList.add(speaker.toLowerCase());
  div.textContent = `${speaker}: ${text}`;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight; // auto-scroll
}

/**
 * Send the user's message to the Flask server
 */
sendBtn.addEventListener("click", async () => {
  const userMessage = messageInput.value.trim();
  if (!userMessage) return;

  // Render user message
  renderMessage("User", userMessage);
  messageInput.value = "";

  // Send to Flask server
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMessage }),
    });
    const data = await response.json();
    // Render AI response
    const aiReply = data.reply;
    renderMessage("Assistant", aiReply);
  } catch (error) {
    console.error("Error sending message:", error);
    renderMessage("Assistant", "Error: Could not reach server.");
  }
});

/**
 * End conversation - request final JSON summary
 */
endBtn.addEventListener("click", async () => {
  try {
    const response = await fetch("/end_conversation", {
      method: "POST",
    });
   

    // data.summary should contain the JSON array
    renderMessage("Assistant", "Conversation ended. ");
    

  } catch (error) {
    console.error("Error ending conversation:", error);
    renderMessage("Assistant", "Error: Could not retrieve summary.");
  }
});
