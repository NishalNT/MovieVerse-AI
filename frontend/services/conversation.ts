export const conversationStorage = {
  // Get all conversations
  getAll: (): { id: string; title: string; timestamp: string }[] => {
    const ids = JSON.parse(localStorage.getItem("conversations") || "[]");
    const titles = JSON.parse(
      localStorage.getItem("conversationTitles") || "{}",
    );

    return ids.map((id: string) => ({
      id,
      title: titles[id] || `Chat ${id.slice(0, 8)}`,
      timestamp:
        localStorage.getItem(`conv_${id}_time`) || new Date().toISOString(),
    }));
  },

  // Add or update a conversation
  save: (id: string, title: string) => {
    const ids = JSON.parse(localStorage.getItem("conversations") || "[]");
    if (!ids.includes(id)) {
      ids.push(id);
      localStorage.setItem("conversations", JSON.stringify(ids));
    }

    const titles = JSON.parse(
      localStorage.getItem("conversationTitles") || "{}",
    );
    if (!titles[id]) {
      titles[id] = title;
      localStorage.setItem("conversationTitles", JSON.stringify(titles));
    }

    localStorage.setItem(`conv_${id}_time`, new Date().toISOString());
  },

  // Delete a conversation
  delete: (id: string) => {
    const ids = JSON.parse(localStorage.getItem("conversations") || "[]");
    const newIds = ids.filter((i: string) => i !== id);
    localStorage.setItem("conversations", JSON.stringify(newIds));

    const titles = JSON.parse(
      localStorage.getItem("conversationTitles") || "{}",
    );
    delete titles[id];
    localStorage.setItem("conversationTitles", JSON.stringify(titles));

    localStorage.removeItem(`conv_${id}_time`);
  },
};
