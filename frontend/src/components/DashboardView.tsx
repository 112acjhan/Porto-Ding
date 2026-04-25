import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  AlertCircle, 
  FileText, 
  Activity,
  X,
  ExternalLink,
  ShieldCheck,
  Loader2
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../lib/utils';
import { UserRole } from '../types';

interface DashboardViewProps {
  role: UserRole;
}

export default function DashboardView({ role }: DashboardViewProps) {
  const [tickets, setTickets] = useState<any[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isActionLoading, setIsActionLoading] = useState(false);

  // 1. FETCH ACTIVE TICKETS
  const fetchTickets = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/tickets/active');
      const data = await response.json();
      setTickets(data);
    } catch (err) {
      console.error("Failed to fetch tickets:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, []);

  // 2. FETCH TICKET DETAILS
  const handleTicketClick = async (ticket: any) => {
    try {
      const res = await fetch(`http://127.0.0.1:5000/api/intake/documents/${ticket.doc_id}?user_role=${role.toUpperCase()}`);
      const docData = await res.json();
      
      // Combine ticket state with database document record
      setSelectedTicket({ ...ticket, ...docData });
    } catch (err) {
      console.error("Details retrieval failed:", err);
      alert("Could not load document details.");
    }
  };

  // 3. ACTION HANDLER
  const handleAction = async (ticketId: number, action: 'approve' | 'claim' | 'complete') => {
    setIsActionLoading(true);
    const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
    
    let url = `http://127.0.0.1:5000/tickets/${ticketId}/${action}`;
    let method = 'POST';
    let body: any = null;

    if (action === 'approve') {
      body = JSON.stringify({ approving_manager_id: storedUser.id });
    } else if (action === 'claim') {
      url = `http://127.0.0.1:5000/tickets/${ticketId}/claim?staff_id=${storedUser.id}`;
    }

    try {
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body
      });

      if (res.ok) {
        await fetchTickets(); 
        setSelectedTicket(null); 
      } else {
        const err = await res.json();
        alert(`Action failed: ${err.detail}`);
      }
    } catch (error) {
      console.error("Workflow Error:", error);
    } finally {
      setIsActionLoading(false);
    }
  };

  return (
    <div className="space-y-6 pb-24">
      <header className="flex justify-between items-center border-b border-brand-border pb-4">
        <div>
          <h2 className="text-xl font-bold">{role === 'manager' ? 'Executive Oversight' : 'Operations Dashboard'}</h2>
          <p className="text-brand-text-dim text-sm mt-0.5">
            {role === 'manager' ? 'Audit approval queue and system events.' : 'Manage your active tasks and workflow.'}
          </p>
        </div>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        <div className="xl:col-span-8 bg-brand-surface p-6 rounded-xl border border-brand-border">
          <h2 className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em] mb-4">
            {role === 'manager' ? 'Pending Managerial Approvals' : 'Assigned Task Pipeline'}
          </h2>

          {isLoading ? (
            <div className="flex items-center justify-center py-20 text-brand-text-dim"><Loader2 className="animate-spin mr-2" /> Loading Registry...</div>
          ) : (
            <div className="space-y-3">
              {tickets
                .filter(t => role === 'manager' ? t.status === 'PENDING_APPROVAL' : t.status !== 'PENDING_APPROVAL')
                .map((ticket) => (
                  <div key={ticket.id} onClick={() => handleTicketClick(ticket)} className="p-4 bg-brand-bg/50 border border-brand-border rounded-lg flex items-center justify-between group hover:border-brand-accent/30 transition-all cursor-pointer">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-brand-surface border border-brand-border flex items-center justify-center text-brand-text-dim">
                        {ticket.status === 'IN_PROGRESS' ? <Clock size={18} className="text-amber-500" /> : <Activity size={18} />}
                      </div>
                      <div>
                        <p className="text-xs font-bold text-brand-text-main">{ticket.intent_category}</p>
                        <p className="text-[9px] font-bold text-brand-text-dim uppercase mt-0.5">
                          ID: #{ticket.id} • Status: <span className={cn(ticket.status === 'IN_PROGRESS' ? "text-amber-500" : "")}>{ticket.status}</span>
                        </p>
                      </div>
                    </div>
                    
                    <div onClick={(e) => e.stopPropagation()}>
                      {role === 'manager' && ticket.status === 'PENDING_APPROVAL' && (
                        <button onClick={() => handleAction(ticket.id, 'approve')} className="px-3 py-1.5 bg-brand-accent/10 text-brand-accent text-[9px] font-black uppercase rounded border border-brand-accent/20 hover:bg-brand-accent hover:text-white transition-all">
                          Grant Approval
                        </button>
                      )}
                      {role === 'staff' && ticket.status === 'NEW' && (
                        <button onClick={() => handleAction(ticket.id, 'claim')} className="px-3 py-1.5 bg-brand-accent/10 text-brand-accent text-[9px] font-black uppercase rounded border border-brand-accent/20 hover:bg-brand-accent hover:text-white transition-all">
                          Accept Task
                        </button>
                      )}
                      {role === 'staff' && ticket.status === 'IN_PROGRESS' && (
                        <button onClick={() => handleAction(ticket.id, 'complete')} className="px-3 py-1.5 bg-brand-success/10 text-brand-success text-[9px] font-black uppercase rounded border border-brand-success/20 hover:bg-brand-success hover:text-white transition-all">
                          Complete Task
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              {tickets.length === 0 && <div className="text-center py-10 text-brand-text-dim text-xs uppercase font-bold opacity-50">No Active Tickets Found</div>}
            </div>
          )}
        </div>

        {/* Sidebar / Stats Section */}
        <div className="xl:col-span-4 space-y-6">
          <div className="bg-brand-surface p-6 rounded-xl border border-brand-border">
            <h2 className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em] mb-4">Pipeline Status</h2>
            <div className="space-y-4">
              {[
                { label: 'Unassigned', val: tickets.filter(t => t.status === 'NEW').length, color: 'text-brand-accent' },
                { label: 'In Progress', val: tickets.filter(t => t.status === 'IN_PROGRESS').length, color: 'text-amber-500' },
                { label: 'Awaiting Mgr', val: tickets.filter(t => t.status === 'PENDING_APPROVAL').length, color: 'text-rose-500' },
              ].map(stat => (
                <div key={stat.label} className="flex justify-between items-center">
                  <span className="text-[10px] font-bold text-brand-text-dim uppercase">{stat.label}</span>
                  <span className={cn("text-lg font-black", stat.color)}>{stat.val}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* DETAIL MODAL */}
      <AnimatePresence>
        {selectedTicket && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }} className="bg-brand-surface border border-brand-border rounded-2xl p-8 max-w-4xl w-full shadow-2xl relative overflow-hidden flex flex-col max-h-[90vh]">
               <div className="absolute top-0 left-0 w-full h-1 bg-brand-accent opacity-50" />
               
               <div className="flex justify-between items-start mb-6 shrink-0">
                  <div>
                    <h3 className="text-2xl font-black text-brand-text-main flex items-center gap-3">
                      Ticket #{selectedTicket.id}
                      <span className="text-xs px-2 py-1 bg-brand-bg rounded-md text-brand-text-dim border border-brand-border">
                        {selectedTicket.intent_category}
                      </span>
                    </h3>
                  </div>
                  <button onClick={() => setSelectedTicket(null)} className="p-2 hover:bg-brand-bg rounded-lg text-brand-text-dim transition-colors"><X size={20} /></button>
               </div>

               <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-6 overflow-y-auto custom-scrollbar pr-2">
                  {/* LEFT COLUMN: Metadata */}
                  <div className="space-y-6">
                    <div>
                      <label className="text-[10px] font-black text-brand-text-dim uppercase block mb-1">Client Name</label>
                      <p className="text-sm font-bold text-brand-text-main">
                        {selectedTicket.display_name || selectedTicket.client_name || 'Unknown'}
                      </p>
                    </div>
                    <div>
                      <label className="text-[10px] font-black text-brand-text-dim uppercase block mb-1">Client Phone Number</label>
                      <p className="text-sm font-bold text-brand-text-main">
                        {(!selectedTicket.identifier || selectedTicket.identifier === selectedTicket.display_name || selectedTicket.identifier.startsWith("WEB_")) 
                          ? 'Unknown' 
                          : selectedTicket.identifier}
                      </p>
                    </div>
                    <div>
                      <label className="text-[10px] font-black text-brand-text-dim uppercase block mb-1">Deadline</label>
                      <p className="text-sm font-bold text-brand-text-main">
                        {selectedTicket.deadline || 'No deadline specified'}
                      </p>
                    </div>
                    <div>
                      <label className="text-[10px] font-black text-brand-text-dim uppercase block mb-1">Source URL</label>
                      {selectedTicket.gcs_url && selectedTicket.gcs_url.startsWith('http') ? (
                        <a href={selectedTicket.gcs_url} target="_blank" rel="noreferrer" className="text-xs font-bold text-brand-accent flex items-center gap-1 hover:underline break-all">
                          View Original File <ExternalLink size={12} />
                        </a>
                      ) : (
                        <p className="text-xs font-bold text-rose-500 flex items-center gap-1 break-all">
                          <AlertCircle size={12} className="shrink-0" /> {selectedTicket.gcs_url || 'Not available'}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* RIGHT COLUMN: Extracted Data */}
                  <div className="space-y-6 flex flex-col">
                    <div className="bg-brand-bg/50 p-4 rounded-xl border border-brand-border">
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-[9px] font-black text-brand-text-dim uppercase">Formal Summary</label>
                        <ShieldCheck size={14} className="text-brand-success" />
                      </div>
                      <p className="text-xs leading-relaxed text-brand-text-main italic">
                        {selectedTicket.formal_summary || "// Summary not provided by server"}
                      </p>
                    </div>

                    <div className="bg-brand-bg/50 p-4 rounded-xl border border-brand-border flex-1 flex flex-col min-h-[200px]">
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-[9px] font-black text-brand-text-dim uppercase">Raw Text from Document</label>
                        <FileText size={14} className="text-brand-text-dim" />
                      </div>
                      <div className="text-[10px] leading-relaxed text-brand-text-main font-mono overflow-y-auto custom-scrollbar flex-1 whitespace-pre-wrap max-h-[300px]">
                        {selectedTicket.raw_text || "// Raw text not provided by server"}
                      </div>
                    </div>
                  </div>
               </div>

               <div className="flex gap-3 shrink-0 pt-4 border-t border-brand-border">
                  <button className="flex-1 py-4 bg-brand-bg border border-brand-border rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-brand-bg/80 transition-all" onClick={() => setSelectedTicket(null)}>
                    Dismiss Details
                  </button>
                  
                  {role === 'staff' && selectedTicket.status === 'NEW' && (
                    <button 
                      className="flex-1 py-4 bg-brand-accent text-white rounded-xl font-black text-[10px] uppercase tracking-widest shadow-lg shadow-brand-accent/20 active:scale-95 transition-all" 
                      onClick={() => handleAction(selectedTicket.id, 'claim')}
                    >
                      {isActionLoading ? <Loader2 className="animate-spin mx-auto" size={14} /> : 'Accept This Task'}
                    </button>
                  )}
               </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}