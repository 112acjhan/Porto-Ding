/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  FileUp, 
  Database, 
  History, 
  Menu,
  X,
  LogOut,
  Ticket as TicketIcon,
  Package
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from './lib/utils';
import DashboardView from './components/DashboardView';
import DocumentsView from './components/DocumentsView';
import TicketsView from './components/TicketsView';
import InventoryBaseView from './components/InventoryView';
import LogsView from './components/LogsView';
import LandingPageView from './components/LandingPageView';
import ChatBubble from './components/ChatBubble';
import { User, UserRole } from './types';

type ViewType = 'dashboard' | 'documents' | 'tickets' | 'inventory' | 'logs';

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [activeView, setActiveView] = useState<ViewType>('dashboard');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);

  const handleLogin = (newUser: User) => {
    setUser(newUser);
    setActiveView('dashboard');
  };

  const handleLogout = () => {
    setUser(null);
  };

  const getNavItems = () => {
    const base = [
      { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
      { id: 'inventory', label: 'Inventory', icon: Package },
    ];

    if (user?.role === 'manager') {
      return [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'inventory', label: 'Inventory', icon: Package },
        { id: 'documents', label: 'Staff Documents', icon: Database },
        { id: 'logs', label: 'Decision Logs', icon: History },
      ];
    }

    if (user?.role === 'staff') {
      return [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'inventory', label: 'Inventory', icon: Package },
        { id: 'documents', label: 'Document Hub', icon: FileUp },
      ];
    }

    if (user?.role === 'accountant') {
      return [
        ...base,
        { id: 'documents', label: 'Financial Records', icon: Database },
      ];
    }

    return base;
  };

  const renderView = () => {
    if (!user) return null;
    switch (activeView) {
      case 'dashboard': return <DashboardView role={user.role} />;
      case 'documents': return <DocumentsView role={user.role} />;
      case 'tickets': return <TicketsView />;
      case 'inventory': return <InventoryBaseView />;
      case 'logs': return <LogsView />;
      default: return <DashboardView role={user.role} />;
    }
  };

  if (!user) {
    return (
      <AnimatePresence mode="wait">
        <motion.div
          key="landing"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="h-full"
        >
          <LandingPageView onLogin={handleLogin} />
        </motion.div>
      </AnimatePresence>
    );
  }

  return (
    <div className="flex h-screen bg-brand-bg text-brand-text-main overflow-hidden font-sans">
      {/* Sidebar */}
      <motion.aside 
        initial={false}
        animate={{ width: isSidebarOpen ? 220 : 80 }}
        className={cn(
          "relative h-full flex flex-col bg-brand-sidebar border-r border-brand-border z-50",
          !isSidebarOpen && "items-center"
        )}
      >
        <div className="p-6 flex items-center justify-between">
          {isSidebarOpen ? (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center gap-3"
            >
              <div className="text-brand-accent transform scale-125">
                 <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
              </div>
              <span className="font-extrabold text-sm tracking-tight text-brand-accent uppercase">PORTO-DING</span>
            </motion.div>
          ) : (
            <div className="text-brand-accent">
               <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
            </div>
          )}
        </div>

        <nav className="flex-1 px-3 space-y-1 mt-4">
          {getNavItems().map((item) => {
            const Icon = item.icon;
            const isActive = activeView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveView(item.id as ViewType)}
                className={cn(
                  "w-full flex items-center gap-3 p-3 rounded-lg transition-all group relative text-sm font-medium",
                  isActive 
                    ? "bg-brand-surface text-brand-text-main border-l-3 border-brand-accent" 
                    : "text-brand-text-dim hover:text-brand-text-main hover:bg-brand-surface/50"
                )}
              >
                <Icon size={18} className={cn(isActive ? "text-brand-accent" : "text-brand-text-dim group-hover:text-brand-text-main")} />
                {isSidebarOpen && (
                  <motion.span 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                  >
                    {item.label}
                  </motion.span>
                )}
              </button>
            );
          })}
        </nav>

        <div className="p-4 border-t border-brand-border space-y-1">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-rose-500/10 text-rose-500 transition-colors"
          >
            <LogOut size={18} />
            {isSidebarOpen && <span className="font-medium text-sm">Logout</span>}
          </button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-full overflow-hidden relative text-brand-text-main">
        {/* Header */}
        <header className="h-16 flex items-center justify-between px-8 bg-brand-bg border-b border-brand-border sticky top-0 z-40">
          <div className="flex items-center gap-4">
             <button 
              onClick={toggleSidebar}
              className="p-2 hover:bg-brand-surface rounded-lg text-brand-text-dim"
            >
              <Menu size={18} />
            </button>
            <h1 className="text-lg font-semibold tracking-tight uppercase tracking-widest text-xs font-bold text-brand-text-dim">
              System Console / <span className="text-brand-text-main">{activeView}</span>
            </h1>
          </div>

          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <p className="text-[10px] font-black text-brand-text-main uppercase tracking-tighter leading-none">{user.name}</p>
                <p className="text-[9px] font-bold text-brand-text-dim uppercase tracking-widest mt-1">{user.role}</p>
              </div>
              <div className="w-8 h-8 rounded-lg bg-brand-surface border border-brand-border flex items-center justify-center overflow-hidden">
                <img src={user.avatar} alt="avatar" className="w-full h-full object-cover" referrerPolicy="no-referrer" />
              </div>
            </div>
          </div>
        </header>

        {/* View Content */}
        <main className="flex-1 overflow-y-auto p-6 scroll-smooth">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeView}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="h-full"
            >
              {renderView()}
            </motion.div>
          </AnimatePresence>
        </main>

        {/* Global Floating AI Chat */}
        <ChatBubble />
      </div>
    </div>
  );
}


