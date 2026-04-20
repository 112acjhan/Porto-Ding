import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Bot, 
  Cpu, 
  Terminal, 
  X,
  MessageSquare,
  Sparkles,
  Command,
  Minimize2
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../lib/utils';
import { ChatMessage } from '../types';

const INITIAL_MESSAGES: ChatMessage[] = [
  { id: '1', sender: 'ai', content: 'Neural Link established. I am monitoring the Inventory and Ticket systems. How can I facilitate your operations?', timestamp: 'NOW' },
];

export default function ChatBubble() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [inputValue, setInputValue] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isThinking, isOpen]);

  const handleSend = () => {
    if (!inputValue.trim()) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsThinking(true);

    setTimeout(() => {
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        content: "I've queried the Inventory Ledger and recent Action Logs. The 'Premium Arabica' stock is currently below the minThreshold. I recommend escalating the pending WhatsApp order T-8821 for immediate fulfillment.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        type: 'action',
        actionDetails: {
          tool: 'RAG_SCAN_LOGS',
          result: 'Match found: Low_Stock_Warning',
          status: 'success'
        }
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsThinking(false);
    }, 1800);
  };

  return (
    <>
      {/* Floating Bubble */}
      <motion.button
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(true)}
        className={cn(
          "fixed bottom-8 right-8 z-[100] w-14 h-14 rounded-full flex items-center justify-center text-white shadow-2xl transition-all duration-300",
          isOpen ? "scale-0 opacity-0" : "bg-brand-accent shadow-brand-accent/40"
        )}
      >
        <div className="relative">
          <MessageSquare size={24} />
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-brand-success rounded-full border-2 border-brand-accent animate-pulse" />
        </div>
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 100, scale: 0.8, transformOrigin: 'bottom right' }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 100, scale: 0.8 }}
            className="fixed bottom-8 right-8 z-[110] w-[380px] h-[520px] bg-brand-surface border border-brand-border rounded-2xl shadow-3xl flex flex-col overflow-hidden"
          >
            {/* Header */}
            <header className="p-4 border-b border-brand-border bg-brand-bg/50 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-brand-surface border border-brand-border flex items-center justify-center text-brand-accent">
                  <Bot size={18} />
                </div>
                <div>
                  <h3 className="font-bold text-[10px] uppercase tracking-widest text-brand-text-main leading-none">GLM STANDBY</h3>
                  <div className="flex items-center gap-1.5 mt-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-brand-success animate-pulse" />
                    <span className="text-[8px] font-bold text-brand-success uppercase tracking-widest">Neural Link Sync</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                 <button onClick={() => setIsOpen(false)} className="p-1.5 hover:bg-brand-bg rounded-md text-brand-text-dim transition-colors">
                   <Minimize2 size={16} />
                 </button>
              </div>
            </header>

            {/* Messages Area */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
              {messages.map((msg) => (
                <div key={msg.id} className={cn(
                  "flex w-full",
                  msg.sender === 'user' ? "justify-end" : "justify-start"
                )}>
                  <div className={cn(
                    "max-w-[85%] space-y-1",
                    msg.sender === 'user' ? "items-end" : "items-start"
                  )}>
                    <div className={cn(
                      "px-3 py-2 rounded-xl text-xs leading-relaxed",
                      msg.sender === 'user' 
                        ? "bg-brand-accent text-white rounded-tr-none shadow-lg shadow-brand-accent/20" 
                        : "bg-brand-bg text-brand-text-main border border-brand-border rounded-tl-none"
                    )}>
                      {msg.content}
                    </div>
                    {msg.type === 'action' && msg.actionDetails && (
                      <div className="p-2 bg-brand-bg/50 border border-brand-border rounded-lg font-mono text-[9px] text-brand-text-dim">
                        <div className="flex items-center gap-2 mb-1 text-brand-success opacity-70 font-bold uppercase tracking-widest">
                          <Terminal size={10} /> Trace Context
                        </div>
                        <p className="truncate opacity-60">{msg.actionDetails.tool}() - {msg.actionDetails.result}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isThinking && (
                <div className="flex justify-start">
                   <div className="flex items-center gap-2 px-3 py-1.5 bg-brand-bg border border-brand-border rounded-full rounded-tl-none">
                      <div className="flex gap-1">
                        <div className="w-1 h-1 bg-brand-accent rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-1 h-1 bg-brand-accent rounded-full animate-bounce" style={{ animationDelay: '200ms' }} />
                        <div className="w-1 h-1 bg-brand-accent rounded-full animate-bounce" style={{ animationDelay: '400ms' }} />
                      </div>
                      <span className="text-[8px] font-bold text-brand-accent uppercase tracking-[0.2em] italic">Synthesizing...</span>
                   </div>
                </div>
              )}
            </div>

            {/* Input Box */}
            <div className="p-4 bg-brand-bg border-t border-brand-border">
              <div className="flex items-center gap-2 bg-brand-surface p-1 rounded-lg border border-brand-border">
                <input 
                  type="text" 
                  placeholder="Ask about inventory or tickets..."
                  className="flex-1 bg-transparent border-none outline-none text-xs text-brand-text-main px-3 py-2 placeholder:text-brand-text-dim"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                />
                <button 
                  onClick={handleSend}
                  disabled={!inputValue.trim() || isThinking}
                  className="p-2 bg-brand-accent text-white rounded-md disabled:opacity-30 disabled:grayscale transition-all hover:scale-105 active:scale-95"
                >
                  <Send size={14} />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
