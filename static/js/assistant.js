document.addEventListener("DOMContentLoaded", () => {
  const chatMessages = document.getElementById("chat-messages");
  const chatForm = document.getElementById("agent-chat-form");
  const queryInput = document.getElementById("agent-query-input");
  const langSelect = document.getElementById("agent-lang-select");
  const micBtn = document.getElementById("mic-btn");
  const micStatus = document.getElementById("mic-status");
  const activityPanel = document.getElementById("agent-activity-panel");

  // Web Speech API - Speech Recognition Setup
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;
  let isRecording = false;

  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      isRecording = true;
      if (micBtn) micBtn.style.background = "#dc2626";
      if (micStatus) micStatus.textContent = "Listening... Speak now";
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (queryInput) {
        queryInput.value = transcript;
        queryInput.focus();
      }
      if (micStatus) micStatus.textContent = "Voice captured. You can edit before sending.";
    };

    recognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      if (micStatus) micStatus.textContent = `Microphone notice: ${event.error}. Use text input fallback.`;
      resetMicUI();
    };

    recognition.onend = () => {
      resetMicUI();
    };
  } else {
    if (micBtn) {
      micBtn.title = "Browser speech recognition is not supported in this browser. Please use text typing.";
      micBtn.classList.add("btn-disabled");
    }
    if (micStatus) {
      micStatus.textContent = "Voice recognition requires Chrome, Edge, or a WebSpeech-compatible browser.";
    }
  }

  function resetMicUI() {
    isRecording = false;
    if (micBtn) micBtn.style.background = "";
  }

  if (micBtn && recognition) {
    micBtn.addEventListener("click", () => {
      if (isRecording) {
        recognition.stop();
      } else {
        const lang = langSelect ? langSelect.value : "en";
        recognition.lang = lang === "kn" ? "kn-IN" : "en-IN";
        try {
          recognition.start();
        } catch (e) {
          console.error(e);
        }
      }
    });
  }

  // Text-to-Speech Synthesis
  window.speakResponse = function(text) {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      // Remove markdown chars
      const cleanText = text.replace(/[*_#`]/g, "");
      const utterance = new SpeechSynthesisUtterance(cleanText);
      const lang = langSelect ? langSelect.value : "en";
      utterance.lang = lang === "kn" ? "kn-IN" : "en-IN";
      window.speechSynthesis.speak(utterance);
    } else {
      alert("Text-to-speech synthesis not supported on this browser.");
    }
  };

  // Chat Submission Form
  if (chatForm) {
    chatForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const query = queryInput.value.trim();
      if (!query) return;

      const lang = langSelect ? langSelect.value : "en";

      // Append User message
      appendMessage("user", query);
      queryInput.value = "";

      // Update Activity Panel
      if (activityPanel) {
        activityPanel.style.display = "block";
        activityPanel.innerHTML = `
          <div style="font-weight: 600; margin-bottom: 0.35rem; color: #1b4332;">🤖 Agent Activity Stages:</div>
          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <span class="status-pill status-active">1. Understanding Query</span>
            <span class="status-pill status-warning">2. Selecting Tools</span>
            <span class="status-pill status-standby">3. Retrieving Evidence</span>
            <span class="status-pill status-standby">4. Synthesizing Answer</span>
          </div>
        `;
      }

      // Append temporary typing indicator
      const typingId = "typing-" + Date.now();
      appendMessage("agent", "Thinking and consulting agronomic models...", typingId);

      try {
        const response = await fetch("/agent/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: query, language: lang })
        });

        const data = await response.json();
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        if (data.status === "success") {
          // Render detailed response with audio play button
          const msgContainer = document.createElement("div");
          msgContainer.className = "chat-bubble agent";
          
          let toolsHtml = "";
          if (data.tools_called && data.tools_called.length > 0) {
            const toolNames = data.tools_called.map(t => `<code style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px;">${t.tool}</code>`).join(" ");
            toolsHtml = `<div style="font-size: 0.8rem; color: #475569; margin-bottom: 0.5rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem;">🔧 Tools used: ${toolNames}</div>`;
          }

          msgContainer.innerHTML = `
            ${toolsHtml}
            <div style="white-space: pre-wrap;">${escapeHtml(data.response)}</div>
            <div style="margin-top: 0.6rem; display: flex; gap: 0.5rem;">
              <button class="btn btn-secondary" style="font-size: 0.75rem; padding: 3px 8px;" onclick="speakResponse(${JSON.stringify(data.response)})">🔊 Listen (TTS)</button>
            </div>
          `;
          chatMessages.appendChild(msgContainer);
          chatMessages.scrollTop = chatMessages.scrollHeight;

          // Render finished stages in Activity Panel
          if (activityPanel && data.stages) {
            const stagesHtml = data.stages.map(s => 
              `<div style="font-size: 0.8rem; margin-top: 0.25rem;"><strong>${s.stage}:</strong> ${s.detail}</div>`
            ).join("");
            activityPanel.innerHTML = `
              <div style="font-weight: 600; color: #1b4332;">✅ Tool-Execution Activity Summary:</div>
              ${stagesHtml}
            `;
          }
        } else {
          appendMessage("agent", "Error: " + (data.message || "Failed to process request."));
        }
      } catch (err) {
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();
        appendMessage("agent", "Network connection error while contacting agent service.");
      }
    });
  }

  function appendMessage(sender, text, id = null) {
    const msg = document.createElement("div");
    msg.className = `chat-bubble ${sender}`;
    if (id) msg.id = id;
    msg.textContent = text;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.innerText = text;
    return div.innerHTML;
  }
});
