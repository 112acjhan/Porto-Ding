import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Shield, 
  Zap, 
  BarChart3, 
  ArrowRight, 
  ArrowLeft,
  UserCircle2, 
  LogOut, 
  LogIn,
  Lock,
  Mail,
  User as UserIcon,
  ChevronRight
} from 'lucide-react';
import { cn } from '../lib/utils';
import { UserRole, User } from '../types';

interface LandingPageViewProps {
  onLogin: (user: User) => void;
}

export default function LandingPageView({ onLogin }: LandingPageViewProps) {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState<UserRole>('staff');

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
    {
      role: 'Managers',
      items: ['Real-time Executive Command', 'Decision Trace Visibility', 'Automated Performance KPI']
    },
    {
      role: 'Field Staff',
      items: ['Voice-to-Ticket Automation', 'Visual Evidence Validation', 'Low-Stock Pulse Alerts']
    },
    {
      role: 'Accountants',
      items: ['Neural Ledger Reconciliation', 'Fraud & Anomaly Detection', 'Instant Audit Evidence']
    }
  ];

  const handleAuth = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate auth
    const mockUser: User = {
      id: Math.random().toString(36).substr(2, 9),
      name: 'Alex Chen',
      role: selectedRole,
      email: 'alex@porto-ding.ai',
      avatar: 'https://picsum.photos/seed/user/128/128'
    };
    onLogin(mockUser);
  };

  return (
    <div className="min-h-screen bg-brand-bg text-brand-text-main relative overflow-hidden font-sans selection:bg-brand-accent selection:text-white">
      {/* Dynamic Background Elements */}
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
          <button 
            onClick={() => setShowAuthModal(true)}
            className="flex items-center gap-2 px-6 py-2 bg-brand-accent text-white rounded-xl text-xs font-bold transition-all hover:shadow-[0_0_20px_var(--color-brand-accent-glow)] active:scale-95 uppercase tracking-widest"
          >
            <LogIn size={14} /> Login
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 pt-20 pb-32 px-8 max-w-7xl mx-auto text-center">
        <motion.div
           initial={{ opacity: 0, y: 30 }}
           animate={{ opacity: 1, y: 0 }}
           transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-brand-surface border border-brand-border rounded-full text-[10px] font-bold text-brand-accent uppercase tracking-widest mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-brand-accent animate-pulse" />
            Empowering SMEs with Autonomous Intelligence
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tighter text-brand-text-main leading-[0.9] mb-8 max-w-4xl mx-auto">
            Orchestrate Your Operations <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-accent to-indigo-400">With PORTO-DING.</span>
          </h1>
          <p className="text-brand-text-dim text-lg md:text-xl max-w-2xl mx-auto leading-relaxed mb-12">
            Automate document processing, RAG enrichment, and decision-tree execution in a single, immersive interface.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button 
              onClick={() => setShowAuthModal(true)}
              className="w-full sm:w-auto px-8 py-4 bg-brand-accent text-white rounded-xl text-sm font-bold transition-all hover:scale-105 hover:shadow-[0_0_30px_var(--color-brand-accent-glow)] active:scale-95 flex items-center justify-center gap-3 group uppercase tracking-widest"
            >
              Get Started <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </button>
            <button className="w-full sm:w-auto px-8 py-4 border border-brand-border text-brand-text-main rounded-xl text-sm font-bold hover:bg-brand-surface transition-all active:scale-95 uppercase tracking-widest">
              Live Architecture
            </button>
          </div>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-32 text-left">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <motion.div 
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * idx }}
                className="bg-brand-surface border border-brand-border p-8 rounded-2xl hover:border-brand-accent/50 transition-all group relative overflow-hidden"
              >
                <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:opacity-10 transition-opacity">
                   <Icon size={120} />
                </div>
                <div className={cn("w-12 h-12 rounded-xl bg-brand-bg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform relative z-10", feature.color)}>
                  <Icon size={24} />
                </div>
                <h3 className="text-lg font-bold text-brand-text-main mb-3 uppercase tracking-tight relative z-10">{feature.title}</h3>
                <p className="text-brand-text-dim text-sm leading-relaxed relative z-10">{feature.desc}</p>
              </motion.div>
            );
          })}
        </div>

        {/* Technical Pipeline Section */}
        <section className="mt-48 text-left border-t border-brand-border pt-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
            <div>
              <h2 className="text-[10px] font-black text-brand-accent uppercase tracking-[0.4em] mb-4">Core Architecture</h2>
              <h3 className="text-4xl font-extrabold text-brand-text-main leading-tight mb-6">
                The Neural Pipeline <br/>
                <span className="text-brand-text-dim">From Fragmented Data to Action.</span>
              </h3>
              <p className="text-brand-text-dim leading-relaxed mb-8 max-w-lg">
                PORTO-DING doesn't just store data—it understands it. Our autonomous pipeline converts operational noise into structured business intelligence in milliseconds.
              </p>
              <div className="space-y-4">
                {roleBenefits.map((benefit) => (
                   <div key={benefit.role} className="p-4 bg-brand-surface/30 border border-brand-border rounded-xl">
                      <h4 className="text-xs font-black uppercase tracking-widest text-brand-text-main mb-2">{benefit.role}</h4>
                      <div className="flex flex-wrap gap-2">
                        {benefit.items.map(item => (
                          <span key={item} className="text-[9px] font-bold text-brand-text-dim bg-brand-bg px-2 py-1 rounded-md border border-brand-border whitespace-nowrap">
                            {item}
                          </span>
                        ))}
                      </div>
                   </div>
                ))}
              </div>
            </div>
            
            <div className="relative">
              <div className="absolute inset-0 bg-brand-accent/5 blur-[80px] rounded-full" />
              <div className="relative space-y-4">
                {pipeline.map((step, idx) => (
                  <motion.div 
                    key={step.label}
                    initial={{ opacity: 0, x: 20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: idx * 0.1 }}
                    className="flex items-center gap-6 p-6 bg-brand-surface border border-brand-border rounded-2xl group hover:border-brand-accent transition-colors"
                  >
                    <div className="w-10 h-10 rounded-lg bg-brand-bg flex items-center justify-center font-mono text-xs font-bold text-brand-accent border border-brand-border group-hover:shadow-[0_0_15px_var(--color-brand-accent-glow)] transition-all">
                       0{idx + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-center mb-1">
                        <h4 className="text-sm font-bold text-brand-text-main uppercase tracking-tight">{step.label}</h4>
                        <span className="text-[8px] font-black px-2 py-0.5 bg-brand-bg border border-brand-border rounded text-brand-success uppercase tracking-widest">{step.status}</span>
                      </div>
                      <p className="text-[10px] text-brand-text-dim leading-relaxed">{step.desc}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Global Stats Ticker */}
        <section className="mt-48 py-20 bg-brand-surface/30 border-y border-brand-border">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-12 text-center">
            {[
              { label: 'Neural Precision', value: '99.8%' },
              { label: 'Docs Processed', value: '1.4M+' },
              { label: 'Latency Avg', value: '12ms' },
              { label: 'Operations Saved', value: '24/7' },
            ].map((stat) => (
              <div key={stat.label}>
                <p className="text-3xl font-extrabold text-brand-text-main mb-2 tabular-nums">{stat.value}</p>
                <p className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em]">{stat.label}</p>
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* Auth Modal Overlay */}
      <AnimatePresence>
        {showAuthModal && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowAuthModal(false)}
              className="absolute inset-0 bg-brand-bg/80 backdrop-blur-md"
            />
            
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative w-full max-w-md bg-brand-surface border border-brand-border rounded-2xl shadow-2xl overflow-hidden shadow-brand-bg"
            >
              <div className="absolute top-6 left-6 z-10">
                <button 
                  onClick={() => setShowAuthModal(false)}
                  className="p-2 hover:bg-brand-bg rounded-lg text-brand-text-dim hover:text-brand-accent transition-all flex items-center gap-2 group"
                >
                  <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
                  <span className="text-[10px] font-black uppercase tracking-widest leading-none">Back</span>
                </button>
              </div>

              <div className="p-8">
                <div className="text-center mb-8">
                  <div className="w-16 h-16 bg-brand-bg rounded-2xl border border-brand-border flex items-center justify-center mx-auto mb-4 text-brand-accent shadow-[0_0_15px_var(--color-brand-accent-glow)]">
                    <UserCircle2 size={32} />
                  </div>
                  <h2 className="text-2xl font-bold tracking-tight text-brand-text-main uppercase">
                    PORTO-DING LOGIN
                  </h2>
                  <p className="text-brand-text-dim text-xs mt-1 uppercase tracking-widest">Select your operational zone</p>
                </div>

                <form onSubmit={handleAuth} className="space-y-4">
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    {(['manager', 'staff', 'accountant'] as UserRole[]).map((role) => (
                      <button
                        key={role}
                        type="button"
                        onClick={() => setSelectedRole(role)}
                        className={cn(
                          "py-2 rounded-lg text-[10px] font-black uppercase tracking-widest border transition-all",
                          selectedRole === role 
                            ? "bg-brand-accent/20 border-brand-accent text-brand-accent shadow-[0_0_10px_var(--color-brand-accent-glow)] whitespace-nowrap" 
                            : "bg-brand-bg border-brand-border text-brand-text-dim hover:border-brand-text-dim/50"
                        )}
                      >
                        {role}
                      </button>
                    ))}
                  </div>

                  <div className="space-y-1">
                    <div className="relative group">
                      <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-text-dim group-focus-within:text-brand-accent transition-colors" />
                      <input 
                        type="email" 
                        required
                        placeholder="Neural ID (Email)"
                        className="w-full bg-brand-bg border border-brand-border rounded-lg pl-10 pr-4 py-3 text-sm focus:border-brand-accent transition-all outline-none text-brand-text-main"
                      />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="relative group">
                      <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-text-dim group-focus-within:text-brand-accent transition-colors" />
                      <input 
                        type="password" 
                        required
                        placeholder="Access Key"
                        className="w-full bg-brand-bg border border-brand-border rounded-lg pl-10 pr-4 py-3 text-sm focus:border-brand-accent transition-all outline-none text-brand-text-main"
                      />
                    </div>
                  </div>

                  <button 
                    type="submit"
                    className="w-full py-4 bg-brand-accent text-white rounded-xl text-sm font-bold flex items-center justify-center gap-2 group hover:shadow-[0_0_20px_var(--color-brand-accent-glow)] active:scale-95 transition-all mt-4 uppercase tracking-widest"
                  >
                    Authorize Access <ChevronRight size={18} className="group-hover:translate-x-1 transition-transform" />
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
