import React, { useState } from 'react';
import { 
  FileText, 
  ExternalLink, 
  Eye, 
  CheckCircle2, 
  Clock, 
  AlertCircle,
  ChevronRight,
  User as UserIcon,
  X,
  Search,
  ArrowUpDown,
  ArrowUp,
  ArrowDown
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../lib/utils';
import { Ticket } from '../types';

const mockTickets: Ticket[] = [
  {
    id: 'T-8821',
    source: 'WhatsApp Image',
    evidenceUrl: 'https://picsum.photos/seed/order1/800/1200',
    task: 'New Order: 50x Premium Arabica Beans',
    state: 'Pending Manager Approval',
    priority: 'High',
    timestamp: '2024-03-21 14:20',
    extractionSummary: {
      intent: 'ORDER_PLACEMENT',
      confidence: 0.98,
      entities: { customer: 'Café de Luna', items: ['Arabica Beans'], total: 'RM 1,250' }
    }
  },
  {
    id: 'T-8822',
    source: 'PDF Invoice',
    evidenceUrl: 'https://picsum.photos/seed/invoice1/800/1200',
    task: 'Verify Shipping Details for Order #4411',
    state: 'Processing',
    priority: 'Medium',
    timestamp: '2024-03-21 14:15',
    extractionSummary: {
      intent: 'SHIPPING_VERIFICATION',
      confidence: 0.85,
      entities: { documentId: 'INV-4411', carrier: 'PosLaju' }
    }
  },
  {
    id: 'T-8823',
    source: 'WhatsApp Text',
    evidenceUrl: 'https://picsum.photos/seed/chat1/800/1200',
    task: 'Customer Inquiry: Refund Status',
    state: 'Action Required',
    priority: 'Low',
    timestamp: '2024-03-21 14:10',
    extractionSummary: {
      intent: 'CUSTOMER_SERVICE_QUERY',
      confidence: 0.92,
      entities: { issue: 'Refund', status: 'Pending' }
    }
  }
];

type SortField = 'timestamp' | 'id' | 'priority' | 'state';
type SortOrder = 'asc' | 'desc';

export default function TicketsView() {
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [showEvidence, setShowEvidence] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<SortField>('timestamp');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const getStatusColor = (state: string) => {
    switch (state) {
      case 'Processing': return 'text-brand-accent bg-brand-accent/10 border-brand-accent/20';
      case 'Pending Manager Approval': return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
      case 'Ready to Ship': return 'text-brand-success bg-brand-success/10 border-brand-success/20';
      case 'Action Required': return 'text-rose-500 bg-rose-500/10 border-rose-500/20';
      default: return 'text-brand-text-dim bg-brand-surface border-brand-border';
    }
  };

  const priorityWeight = { 'High': 3, 'Medium': 2, 'Low': 1 };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const filteredTickets = mockTickets
    .filter(t => 
      t.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.task.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.state.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.source.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      let comp = 0;
      switch (sortField) {
        case 'id': comp = a.id.localeCompare(b.id); break;
        case 'timestamp': comp = a.timestamp.localeCompare(b.timestamp); break;
        case 'priority': comp = (priorityWeight[a.priority as keyof typeof priorityWeight] || 0) - (priorityWeight[b.priority as keyof typeof priorityWeight] || 0); break;
        case 'state': comp = a.state.localeCompare(b.state); break;
      }
      return sortOrder === 'asc' ? comp : -comp;
    });

  const SortButton = ({ field, label }: { field: SortField, label: string }) => (
    <button 
      onClick={() => handleSort(field)}
      className={cn(
        "flex items-center gap-1.5 px-3 py-1.5 rounded-lg border transition-all text-[10px] font-bold uppercase tracking-widest",
        sortField === field 
          ? "bg-brand-accent/10 border-brand-accent text-brand-accent" 
          : "bg-brand-surface border-brand-border text-brand-text-dim hover:text-brand-text-main"
      )}
    >
      {label}
      {sortField === field && (
        sortOrder === 'asc' ? <ArrowUp size={12} /> : <ArrowDown size={12} />
      )}
    </button>
  );

  return (
    <div className="h-full flex gap-6 animate-in fade-in duration-500">
      {/* Ticket List */}
      <div className={cn(
        "flex-1 flex flex-col space-y-6 transition-all duration-300",
        showEvidence ? "pr-[400px]" : ""
      )}>
        <header className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">Operation Orchestrator</h2>
            <p className="text-brand-text-dim text-sm mt-0.5">Autonomous task generation from GLM vision parsing.</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-text-dim" />
              <input 
                type="text" 
                placeholder="Search tickets..." 
                className="bg-brand-surface border border-brand-border rounded-lg pl-9 pr-4 py-1.5 text-xs focus:border-brand-accent transition-all outline-none text-brand-text-main w-64"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
        </header>

        <div className="flex items-center gap-2 overflow-x-auto pb-2 custom-scrollbar">
          <span className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em] mr-2 shrink-0">Sort By:</span>
          <SortButton field="timestamp" label="Newest" />
          <SortButton field="priority" label="Priority" />
          <SortButton field="state" label="Status" />
          <SortButton field="id" label="ID" />
        </div>

        <div className="space-y-4">
          {filteredTickets.map((ticket) => (
            <div 
              key={ticket.id}
              onClick={() => setSelectedTicket(ticket)}
              className={cn(
                "group relative bg-brand-surface border rounded-xl p-5 cursor-pointer transition-all hover:shadow-xl",
                selectedTicket?.id === ticket.id ? "border-brand-accent shadow-brand-accent/5" : "border-brand-border hover:border-brand-text-dim/30"
              )}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-brand-bg flex items-center justify-center text-brand-text-dim group-hover:text-brand-accent transition-colors">
                    <FileText size={20} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                       <span className="text-xs font-black text-brand-text-dim tabular-nums tracking-tighter">{ticket.id}</span>
                       <span className="text-[10px] font-bold text-brand-text-dim/50 uppercase tracking-widest">• {ticket.source}</span>
                    </div>
                    <h3 className="font-bold text-brand-text-main mt-0.5">{ticket.task}</h3>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <span className={cn(
                    "text-[10px] font-bold px-2 py-1 rounded border uppercase tracking-widest",
                    getStatusColor(ticket.state)
                  )}>
                    {ticket.state}
                  </span>
                  <span className="text-[10px] font-bold text-brand-text-dim/50">{ticket.timestamp}</span>
                </div>
              </div>

              <div className="flex items-center justify-between mt-6 pt-4 border-t border-brand-border/50">
                <div className="flex items-center gap-4">
                  <div className="flex -space-x-2">
                    {[1, 2].map((i) => (
                      <div key={i} className="w-6 h-6 rounded-full border-2 border-brand-surface bg-brand-bg flex items-center justify-center">
                        <UserIcon size={12} className="text-brand-text-dim" />
                      </div>
                    ))}
                  </div>
                  <span className="text-[10px] font-bold text-brand-text-dim uppercase tracking-widest">2 Operations Assigned</span>
                </div>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedTicket(ticket);
                    setShowEvidence(true);
                  }}
                  className="flex items-center gap-2 text-[10px] font-black text-brand-accent hover:underline uppercase tracking-widest"
                >
                  View Evidence <ExternalLink size={12} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Side Panel: Evidence Viewer */}
      <AnimatePresence>
        {showEvidence && selectedTicket && (
          <motion.aside
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            className="fixed top-0 right-0 w-[400px] h-full bg-brand-surface border-l border-brand-border z-[60] shadow-2xl flex flex-col"
          >
            <header className="p-6 border-b border-brand-border flex items-center justify-between">
              <div>
                <h3 className="font-bold text-brand-text-main uppercase tracking-tight text-sm">Evidence Verification</h3>
                <p className="text-[10px] font-bold text-brand-text-dim uppercase tracking-widest mt-0.5">{selectedTicket.id}</p>
              </div>
              <button 
                onClick={() => setShowEvidence(false)}
                className="p-2 hover:bg-brand-bg rounded-lg text-brand-text-dim transition-colors"
              >
                <X size={18} />
              </button>
            </header>

            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              <div className="aspect-[3/4] bg-brand-bg rounded-xl border border-brand-border overflow-hidden relative group">
                <img 
                  src={selectedTicket.evidenceUrl} 
                  alt="Evidence" 
                  className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-500"
                  referrerPolicy="no-referrer"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                  <span className="text-[10px] font-bold text-white uppercase tracking-widest">Original Source Capture</span>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="text-[10px] font-black text-brand-accent uppercase tracking-[0.2em]">Master Extraction Payload</h4>
                <div className="bg-brand-bg border border-brand-border p-4 rounded-xl font-mono text-[11px] space-y-3">
                  <div className="flex justify-between">
                    <span className="text-brand-text-dim opacity-50">INTENT:</span>
                    <span className="text-brand-text-main font-bold">{selectedTicket.extractionSummary.intent}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-brand-text-dim opacity-50">CONFIDENCE:</span>
                    <span className="text-brand-success font-bold">{(selectedTicket.extractionSummary.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="h-[1px] bg-brand-border" />
                  <pre className="text-brand-text-dim leading-relaxed whitespace-pre-wrap">
                    {JSON.stringify(selectedTicket.extractionSummary.entities, null, 2)}
                  </pre>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em]">Operational Controls</h4>
                <div className="flex flex-col gap-2">
                  <button className="w-full py-3 bg-brand-accent text-white rounded-lg text-xs font-bold uppercase tracking-widest shadow-lg shadow-brand-accent/20 hover:scale-[1.02] transition-all">
                    Approve Extraction
                  </button>
                  <button className="w-full py-3 bg-brand-bg border border-brand-border text-brand-text-main rounded-lg text-xs font-bold uppercase tracking-widest hover:bg-brand-surface transition-all">
                    Flag for Review
                  </button>
                </div>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </div>
  );
}
