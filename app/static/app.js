// CrowdPulse frontend logic. Vanilla JS, no framework/build step (see
// Architecture.md / Rules.md). Talks to the FastAPI backend via fetch and
// swaps in HTML fragments returned by the server — the server templates are
// the single source of truth for markup, this file just wires up events.

document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("upload-form");
  const uploadError = document.getElementById("upload-error");
  const briefBtn = document.getElementById("generate-brief-btn");
  const briefLoading = document.getElementById("brief-loading");
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const chatMessages = document.getElementById("chat-messages");

  function showUploadError(message) {
    uploadError.textContent = message;
    uploadError.classList.remove("hidden");
  }

  function hideUploadError() {
    uploadError.classList.add("hidden");
    uploadError.textContent = "";
  }

  // --- CSV Upload ---
  if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      hideUploadError();
      const fileInput = document.getElementById("csv-upload");
      if (!fileInput.files.length) {
        showUploadError("Please choose a CSV file first.");
        return;
      }
      const formData = new FormData();
      formData.append("file", fileInput.files[0]);

      try {
        const res = await fetch("/upload", { method: "POST", body: formData });
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: "Upload failed." }));
          showUploadError(err.detail || "Upload failed.");
          return;
        }
        const html = await res.text();
        document.getElementById("zone-grid-wrapper").outerHTML = html;
        if (briefBtn) briefBtn.disabled = false;
      } catch (err) {
        showUploadError("Network error while uploading. Please try again.");
      }
    });
  }

  // --- Generate AI Brief ---
  if (briefBtn) {
    briefBtn.addEventListener("click", async () => {
      briefBtn.disabled = true;
      briefLoading.classList.remove("hidden");
      try {
        const res = await fetch("/ai/brief", { method: "POST" });
        const html = await res.text();
        document.getElementById("ai-brief-container").innerHTML = html;
        attachActionButtons();
      } catch (err) {
        document.getElementById("ai-brief-container").innerHTML =
          '<div class="text-sm text-critical">Could not reach the server. Please try again.</div>';
      } finally {
        briefBtn.disabled = false;
        briefLoading.classList.add("hidden");
      }
    });
  }

  // --- Mark recommendation as actioned (delegated, since brief content is re-rendered) ---
  function attachActionButtons() {
    document.querySelectorAll(".log-action-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        btn.disabled = true;
        btn.textContent = "Logging...";
        try {
          const res = await fetch("/incidents", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              zone_name: btn.dataset.zone,
              action_taken: btn.dataset.action,
              status_at_time: btn.dataset.status,
            }),
          });
          if (res.ok) {
            const html = await res.text();
            document.getElementById("incident-log-container").innerHTML = html;
            btn.textContent = "Logged ✓";
          } else {
            btn.disabled = false;
            btn.textContent = "Mark as Actioned";
          }
        } catch (err) {
          btn.disabled = false;
          btn.textContent = "Mark as Actioned";
        }
      });
    });
  }
  attachActionButtons();

  // --- Ops Chat ---
  function appendMessage(text, sender) {
    const bubble = document.createElement("div");
    bubble.className =
      sender === "user"
        ? "text-sm bg-brand/20 text-textprimary rounded px-3 py-2 ml-8"
        : "text-sm bg-bgbase border border-edge text-textprimary rounded px-3 py-2 mr-8";
    bubble.textContent = text;
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  if (chatForm) {
    chatForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const message = chatInput.value.trim();
      if (!message) return;
      appendMessage(message, "user");
      chatInput.value = "";
      chatInput.disabled = true;

      const thinkingBubble = document.createElement("div");
      thinkingBubble.className = "text-sm text-textmuted italic mr-8";
      thinkingBubble.textContent = "Thinking...";
      chatMessages.appendChild(thinkingBubble);
      chatMessages.scrollTop = chatMessages.scrollHeight;

      try {
        const res = await fetch("/ai/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message }),
        });
        thinkingBubble.remove();
        if (res.ok) {
          const data = await res.json();
          appendMessage(data.reply, "ai");
        } else {
          const err = await res.json().catch(() => ({ detail: "Something went wrong." }));
          appendMessage(err.detail || "Something went wrong.", "ai");
        }
      } catch (err) {
        thinkingBubble.remove();
        appendMessage("Network error. Please try again.", "ai");
      } finally {
        chatInput.disabled = false;
        chatInput.focus();
      }
    });
  }
});
