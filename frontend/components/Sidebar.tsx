'use client';

import React, { useState, useEffect } from 'react';
import { X, MessageSquare, Plus, Trash2, Clock, Film, Sparkles } from 'lucide-react';
import { chatAPI } from '@/services/api';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
}

interface Conversation {
  id: string;
  title: string;
  timestamp: string;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose, onNewChat, onSelectConversation }) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = () => {
    const saved = localStorage.getItem('conversations') || '[]';
    const convIds = JSON.parse(saved);
    const titles = JSON.parse(localStorage.getItem('conversationTitles') || '{}');
    
    const convs = convIds.map((id: string) => ({
      id,
      title: titles[id] || `Chat ${id.slice(0, 8)}`,
      timestamp: localStorage.getItem(`conv_${id}_time`) || new Date().toISOString()
    }));
    
    // Sort by most recent
    convs.sort((a: Conversation, b: Conversation) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
    
    setConversations(convs);
  };

  const saveConversations = (newConversations: Conversation[]) => {
    setConversations(newConversations);
    const ids = newConversations.map(c => c.id);
    localStorage.setItem('conversations', JSON.stringify(ids));
  };

  const handleNewChat = () => {
    onNewChat();
    onClose();
  };

  const handleSelectConversation = (id: string) => {
    // Update timestamp
    const updated = conversations.map(c => 
      c.id === id ? { ...c, timestamp: new Date().toISOString() } : c
    );
    saveConversations(updated);
    localStorage.setItem(`conv_${id}_time`, new Date().toISOString());
    onSelectConversation(id);
    onClose();
  };

  const handleDeleteConversation = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const newConversations = conversations.filter(c => c.id !== id);
    saveConversations(newConversations);
    chatAPI.clearHistory(id);
    // Remove title
    const titles = JSON.parse(localStorage.getItem('conversationTitles') || '{}');
    delete titles[id];
    localStorage.setItem('conversationTitles', JSON.stringify(titles));
    localStorage.removeItem(`conv_${id}_time`);
  };

  const getIconForConversation = (title: string) => {
    if (title.includes('Lord of the Rings') || title.includes('LOTR')) {
      return '🧙';
    } else if (title.includes('Fast') || title.includes('Furious')) {
      return '🏎️';
    } else if (title.includes('Harry Potter')) {
      return '⚡';
    } else if (title.includes('Marvel') || title.includes('Avengers')) {
      return '🦸';
    } else if (title.includes('Star Wars')) {
      return '⭐';
    } else if (title.includes('Batman')) {
      return '🦇';
    } else if (title.includes('Interstellar')) {
      return '🚀';
    } else if (title.includes('Inception')) {
      return '🌀';
    } else {
      return '🎬';
    }
  };

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-full w-80 bg-[#0a0a0f]/95 backdrop-blur-xl border-r border-white/5 z-50 transform transition-all duration-500 ease-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 lg:relative lg:z-0 lg:flex lg:flex-col lg:shrink-0`}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-5 border-b border-white/5 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                <Film className="w-4 h-4 text-white" />
              </div>
              <div>
                <span className="font-semibold text-white">Chat History</span>
                <p className="text-xs text-white/30">{conversations.length} conversations</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={handleNewChat}
                className="p-2 hover:bg-white/5 rounded-xl transition-all duration-300 text-white/40 hover:text-white"
                title="New Chat"
                type="button"
              >
                <Plus className="w-4 h-4" />
              </button>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/5 rounded-xl transition-all duration-300 text-white/40 hover:text-white lg:hidden"
                title="Close sidebar"
                type="button"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Conversations */}
          <div className="flex-1 overflow-y-auto p-3 space-y-1 scrollbar-cinematic">
            {conversations.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 mx-auto bg-white/5 rounded-2xl flex items-center justify-center mb-4">
                  <MessageSquare className="w-8 h-8 text-white/20" />
                </div>
                <p className="text-sm text-white/30">No conversations yet</p>
                <p className="text-xs text-white/20 mt-1">Start a new chat to begin</p>
              </div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  className="group flex items-center justify-between p-3 hover:bg-white/5 rounded-xl transition-all duration-300 cursor-pointer"
                  onClick={() => handleSelectConversation(conv.id)}
                >
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <div className="w-8 h-8 bg-white/5 rounded-lg flex items-center justify-center shrink-0 text-lg">
                      {getIconForConversation(conv.title)}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="text-sm text-white/80 truncate group-hover:text-white transition-colors">
                        {conv.title}
                      </div>
                      <div className="text-xs text-white/30 truncate">
                        {new Date(conv.timestamp).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDeleteConversation(conv.id, e)}
                    className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-white/10 rounded-lg transition-all duration-300 shrink-0"
                    aria-label="Delete conversation"
                    type="button"
                  >
                    <Trash2 className="w-3.5 h-3.5 text-white/30 hover:text-red-400 transition-colors" />
                  </button>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-white/5 shrink-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                <span className="text-xs text-white/20">MovieVerse AI v1.0</span>
              </div>
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-pulse" />
                <div className="w-1.5 h-1.5 bg-pink-500 rounded-full animate-pulse delay-75" />
                <div className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-pulse delay-150" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;