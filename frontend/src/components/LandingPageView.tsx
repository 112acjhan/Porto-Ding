import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Shield, Zap, BarChart3, ArrowRight, ArrowLeft,
  UserCircle2, LogIn, Lock, Mail, ChevronRight 
} from 'lucide-react';
import { cn } from '../lib/utils';
import { UserRole, User } from '../types';
import { api } from '../lib/api';

interface LandingPageViewProps {
  onLogin: (user: User) => void;
}

export default function LandingPageView({ onLogin }: LandingPageViewProps) {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState<UserRole>('staff');
  
  // 1. Updated state names to match your database (id instead of Email)
  const [id, setUserId] = useState('');  
  const [password, setPassword] = useState(''); 
  const [isLoading, setIsLoading] = useState(false);

  const features = [
    { 
      title: 'Neural Extraction', 
      desc: 'Autonomous GLM reasoning powered by Z.AI. Instantly converts messy WhatsApp images, voice notes, and PDFs into structured actionable data with 99.8% precision.',
      icon: Zap,
      color: 'text-brand-accent'
    },
    { 
      title: 'Adaptive RAG Vault', 
      desc: 'Your business intelligence, indexed. Seamlessly query your entire document history using vector embeddings and semantic search to find "that one invoice" from 2 years ago.',
      icon: Shield,
      color: 'text-brand-success'
    },
    { 
      title: 'PORTO-DING Hub', 
      desc: 'A unified operations console. Orchestrate field staff, manage procurement cycles, and automate accounting reconciliation from a single immersive interface.',
      icon: BarChart3,
      color: 'text-brand-accent'
    }
  ];

  const pipeline = [
    { label: 'Capture', desc: 'Fragmented data from WhatsApp/Voice/PDF', status: 'Inbound' },
    { label: 'Extract', desc: 'GLM entities & intent classification', status: 'Processing' },
    { label: 'Enrich', desc: 'RAG context & historical sync', status: 'Indexing' },
    { label: 'Reason', desc: 'Decision-tree logic & risk assessment', status: 'Analyzing' },
    { label: 'Execute', desc: 'Ticket generation & auto-fulfillment', status: 'Live' },
  ];

  const roleBenefits = [
    { role: 'Managers', items: ['Real-time Executive Command', 'Decision Trace Visibility', 'Automated Performance KPI'] },
    { role: 'Field Staff', items: ['Voice-to-Ticket Automation', 'Visual Evidence Validation', 'Low-Stock Pulse Alerts'] },
    { role: 'Accountants', items: ['Neural Ledger Reconciliation', 'Fraud & Anomaly Detection', 'Instant Audit Evidence'] }
  ];

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      // 2. Sending the id and password to your API
      const res = await api.login({ id: Number(id), password: password });
      const data = await res.json();
      
      if (res.ok) {
        const userData = data.user; 
        // localStorage.setItem('role', userData.role); // e.g., "MANAGER"
        // localStorage.setItem('id', userData.id.toString());
        // localStorage.setItem('username', userData.username);
        localStorage.setItem('user', JSON.stringify(userData));
        
        onLogin({
          id: userData.id.toString(),
          name: userData.username,
          role: userData.role.toLowerCase() as UserRole,
          email: `${userData.username}@porto-ding.ai`,
          avatar: 'https://picsum.photos/seed/user/128/128'
        });
      } else {
        alert(data.detail || "Authentication Failed. Please check your ID and Access Key.");
      }
    } catch (err) {
      // alert("Backend server offline. Please ensure main.py is running.");
      alert(err)
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-brand-bg text-brand-text-main relative overflow-hidden font-sans selection:bg-brand-accent selection:text-white">
      {/* Background Elements */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-[20%] -left-[10%] w-[60%] h-[60%] bg-brand-accent/5 rounded-full blur-[120px]" />
        <div className="absolute -bottom-[20%] -right-[10%] w-[60%] h-[60%] bg-indigo-500/5 rounded-full blur-[120px]" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-50 contrast-150 pointer-events-none" />
      </div>

      {/* Navigation */}
      <nav className="relative z-50 flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="text-brand-accent transform scale-125">
             <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
          </div>
          <span className="font-extrabold text-lg tracking-tight text-brand-text-main uppercase">PORTO-DING</span>
        </div>
        <div className="flex items-center gap-4">
          <button onClick={() => setShowAuthModal(true)} className="flex items-center gap-2 px-6 py-2 bg-brand-accent text-white rounded-xl text-xs font-bold transition-all hover:shadow-[0_0_20px_var(--color-brand-accent-glow)] active:scale-95 uppercase tracking-widest">
            <LogIn size={14} /> Login
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 pt-20 pb-32 px-8 max-w-7xl mx-auto text-center">
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: "easeOut" }}>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-brand-surface border border-brand-border rounded-full text-[10px] font-bold text-brand-accent uppercase tracking-widest mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-brand-accent animate-pulse" />
            Empowering SMEs with Autonomous Intelligence
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tighter text-brand-text-main leading-[0.9] mb-8 max-w-4xl mx-auto">
            Orchestrate Your Operations <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-accent to-indigo-400">With PORTO-DING.</span>
          </h1>
          <p className="text-brand-text-dim text-lg md:text-xl max-w-2xl mx-auto leading-relaxed mb-12">
            Automate document processing, RAG enrichment, and decision-tree execution in a single interface.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button onClick={() => setShowAuthModal(true)} className="w-full sm:w-auto px-8 py-4 bg-brand-accent text-white rounded-xl text-sm font-bold transition-all hover:scale-105 hover:shadow-[0_0_30px_var(--color-brand-accent-glow)] active:scale-95 flex items-center justify-center gap-3 group uppercase tracking-widest">
              Get Started <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </motion.div>
      </main>

      {/* Auth Modal */}
      <AnimatePresence>
        {showAuthModal && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setShowAuthModal(false)} className="absolute inset-0 bg-brand-bg/80 backdrop-blur-md" />
            
            <motion.div initial={{ opacity: 0, scale: 0.9, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.9, y: 20 }} className="relative w-full max-w-md bg-brand-surface border border-brand-border rounded-2xl shadow-2xl overflow-hidden shadow-brand-bg">
              <div className="p-8">
                <div className="text-center mb-8">
                  <div className="w-16 h-16 bg-brand-bg rounded-2xl border border-brand-border flex items-center justify-center mx-auto mb-4 text-brand-accent shadow-[0_0_15px_var(--color-brand-accent-glow)]">
                    <UserCircle2 size={32} />
                  </div>
                  <h2 className="text-2xl font-bold tracking-tight text-brand-text-main uppercase">PORTO-DING LOGIN</h2>
                </div>

                <form onSubmit={handleAuth} className="space-y-4">
                  {/* Role Selection (Optional UI, purely visual/filter) */}
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    {(['manager', 'staff', 'accountant'] as UserRole[]).map((role) => (
                      <button key={role} type="button" onClick={() => setSelectedRole(role)} className={cn("py-2 rounded-lg text-[10px] font-black uppercase tracking-widest border transition-all", selectedRole === role ? "bg-brand-accent/20 border-brand-accent text-brand-accent" : "bg-brand-bg border-brand-border text-brand-text-dim")}>
                        {role}
                      </button>
                    ))}
                  </div>

                  {/* 3. Username Input mapped to your DB "username" column */}
                  <div className="space-y-1">
                    <div className="relative group">
                      <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-text-dim" />
                      <input 
                        type="text" 
                        required
                        value={id}
                        onChange={(e) => setUserId(e.target.value)}
                        placeholder="Staff / Manager ID"
                        className="w-full bg-brand-bg border border-brand-border rounded-lg pl-10 pr-4 py-3 text-sm focus:border-brand-accent transition-all outline-none text-brand-text-main"
                      />
                    </div>
                  </div>

                  {/* 4. Password Input mapped to your DB "password_hash" validation */}
                  <div className="space-y-1">
                    <div className="relative group">
                      <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-text-dim" />
                      <input 
                        type="password" 
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Access Key"
                        className="w-full bg-brand-bg border border-brand-border rounded-lg pl-10 pr-4 py-3 text-sm focus:border-brand-accent transition-all outline-none text-brand-text-main"
                      />
                    </div>
                  </div>

                  <button 
                    type="submit"
                    disabled={isLoading}
                    className="w-full py-4 bg-brand-accent text-white rounded-xl text-sm font-bold flex items-center justify-center gap-2 group hover:shadow-[0_0_20px_var(--color-brand-accent-glow)] active:scale-95 transition-all mt-4 uppercase tracking-widest"
                  >
                    {isLoading ? "Authenticating..." : "Authorize Access"} <ChevronRight size={18} />
                  </button>
                </form>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}