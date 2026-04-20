import React, { useState } from 'react';
import { 
  FileLock2, 
  Terminal, 
  ShieldCheck, 
  Search, 
  Download,
  Filter,
  ArrowRight,
  ArrowUpDown,
  ArrowUp,
  ArrowDown
} from 'lucide-react';
import { cn } from '../lib/utils';
import { AuditLogEntry } from '../types';

const mockAuditLogs: AuditLogEntry[] = [
  { id: '1', timestamp: '14:20:11', user: 'Staff_01', action: 'Uploaded Order_A.png', details: 'File size: 1.2MB, Type: PNG' },
  { id: '2', timestamp: '14:21:05', user: 'GLM_Vision', action: 'Identified Intent', intent: 'ORDER_PLACEMENT', confidence: 0.98, target: 'Order_A' },
  { id: '3', timestamp: '14:21:30', user: 'System_Privacy', action: 'Masked PII', details: 'Masked Phone Number and Home Address for Staff_01' },
  { id: '4', timestamp: '14:25:12', user: 'Manager_Ahmad', action: 'Approved Access', target: 'Order_A', details: 'Granted session access to raw PII for shipping verification' },
  { id: '5', timestamp: '14:30:00', user: 'Staff_01', action: 'Modified Ticket', target: 'T-8821', details: 'Status changed from Pending to Processing' },
];

type SortField = 'timestamp' | 'user' | 'action';
type SortOrder = 'asc' | 'desc';

export default function LogsView() {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<SortField>('timestamp');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const filteredLogs = mockAuditLogs
    .filter(log => 
      log.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.details?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.target?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.intent?.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      let comp = 0;
      switch (sortField) {
        case 'timestamp': comp = a.timestamp.localeCompare(b.timestamp); break;
        case 'user': comp = a.user.localeCompare(b.user); break;
        case 'action': comp = a.action.localeCompare(b.action); break;
      }
      return sortOrder === 'asc' ? comp : -comp;
    });

  const SortButton = ({ field, label }: { field: SortField, label: string }) => (
    <button 
      onClick={() => handleSort(field)}
      className={cn(
        "flex items-center gap-1.5 px-3 py-1.5 rounded-full border transition-all text-[9px] font-black uppercase tracking-widest",
        sortField === field 
          ? "bg-brand-accent/10 border-brand-accent text-brand-accent shadow-[0_0_10px_var(--color-brand-accent-glow)]" 
          : "bg-brand-bg border-brand-border text-brand-text-dim hover:text-brand-text-main"
      )}
    >
      {label}
      {sortField === field && (
        sortOrder === 'asc' ? <ArrowUp size={10} /> : <ArrowDown size={10} />
      )}
    </button>
  );

  return (
    <div className="h-full flex flex-col space-y-6 pb-20 animate-in fade-in duration-500 font-sans">
      <header className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">Immutability Ledger</h2>
          <p className="text-brand-text-dim text-sm mt-0.5">Professional-grade audit trail of all operational neural events.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-3 py-1.5 bg-brand-surface border border-brand-border rounded-lg text-xs font-bold text-brand-text-main hover:bg-brand-bg transition-all uppercase tracking-widest">
            <Download size={14} /> Export Secure Log
          </button>
        </div>
      </header>

      <div className="bg-brand-surface border border-brand-border rounded-xl shadow-2xl overflow-hidden flex flex-col flex-1">
        {/* Ledger Toolbar */}
        <div className="p-4 border-b border-brand-border bg-brand-bg/50 flex items-center justify-between">
           <div className="flex items-center gap-4">
              <div className="relative w-64">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-text-dim" />
                <input 
                  type="text" 
                  placeholder="Filter by User or Event..." 
                  className="w-full bg-brand-bg border border-brand-border rounded-lg pl-10 pr-4 py-2 text-xs focus:border-brand-accent outline-none"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <div className="flex gap-2">
                <SortButton field="timestamp" label="Time" />
                <SortButton field="user" label="User" />
                <SortButton field="action" label="Action" />
              </div>
              <div className="h-4 w-[1px] bg-brand-border mx-2" />
              <div className="flex gap-2 items-center">
                <span className="px-3 py-1 bg-brand-accent/10 border border-brand-accent/20 rounded-full text-[9px] font-black text-brand-accent uppercase tracking-widest">Live Flow</span>
                <span className="px-3 py-1 bg-brand-bg border border-brand-border rounded-full text-[9px] font-black text-brand-text-dim uppercase tracking-widest flex items-center gap-1.5">
                  <ShieldCheck size={10} className="text-brand-success" /> Tamper-Proof
                </span>
              </div>
           </div>
           <div className="flex items-center gap-2 text-[10px] font-bold text-brand-text-dim uppercase tracking-widest">
             <Terminal size={14} /> Node v4.12
           </div>
        </div>

        {/* Ledger Core */}
        <div className="flex-1 overflow-y-auto font-mono text-[11px] leading-relaxed p-6 selection:bg-brand-accent selection:text-white bg-[radial-gradient(circle_at_0%_0%,rgba(59,130,246,0.03)_0%,transparent_50%)]">
           <div className="space-y-3">
              {filteredLogs.map((log) => (
                <div key={log.id} className="group flex items-start gap-4 hover:bg-brand-bg/40 p-3 rounded-lg transition-colors border border-transparent hover:border-brand-border/50">
                  <span className="text-brand-text-dim/50 shrink-0 w-20">[{log.timestamp}]</span>
                  
                  <div className="flex-1 flex flex-col gap-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className={cn(
                        "px-1.5 py-0.5 rounded text-[9px] font-bold tracking-tight uppercase border",
                        log.user.startsWith('Staff') ? "bg-brand-accent/5 text-brand-accent border-brand-accent/20" :
                        log.user.startsWith('Manager') ? "bg-brand-success/5 text-brand-success border-brand-success/20" :
                        "bg-brand-surface text-brand-text-dim border-brand-border"
                      )}>
                        {log.user}
                      </span>
                      <span className="text-brand-text-dim opacity-70">Executed</span>
                      <span className="text-brand-text-main font-bold">{log.action}</span>
                      {log.target && (
                        <>
                          <ArrowRight size={10} className="text-brand-text-dim/50" />
                          <span className="text-brand-accent font-black tracking-tighter hover:underline cursor-pointer">{log.target}</span>
                        </>
                      )}
                    </div>

                    {/* Meta Data Context */}
                    <div className="flex flex-col gap-1 pl-4 border-l border-brand-border/50 mt-1">
                      {log.intent && (
                        <div className="flex items-center gap-2">
                           <span className="text-[9px] font-black text-brand-text-dim/40 uppercase tracking-widest">Intent:</span>
                           <span className="text-brand-success font-bold px-1.5 bg-brand-success/5 rounded">{log.intent}</span>
                           <span className="text-[9px] font-black text-brand-text-dim/40 uppercase tracking-widest ml-2">Conf:</span>
                           <span className="text-brand-success tabular-nums">{(log.confidence! * 100).toFixed(0)}%</span>
                        </div>
                      )}
                      {log.details && (
                        <div className="flex items-start gap-2">
                           <span className="text-[9px] font-black text-brand-text-dim/40 uppercase tracking-widest shrink-0">Details:</span>
                           <span className="text-brand-text-dim italic leading-tight">{log.details}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              <div className="flex items-center gap-3 p-3 opacity-30 animate-pulse">
                 <div className="w-1 h-1 rounded-full bg-brand-accent" />
                 <span className="text-[9px] font-bold uppercase tracking-[0.2em] italic">Awaiting Next Neural Hook...</span>
              </div>
           </div>
        </div>

        {/* Audit Verification Stamp */}
        <div className="px-6 py-4 bg-brand-bg border-t border-brand-border flex items-center justify-between">
           <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 text-[10px] font-black text-brand-text-dim/60 uppercase tracking-widest">
                <FileLock2 size={12} className="text-brand-accent" />
                Ledger SHA-256 Verified
              </div>
           </div>
           <div className="text-[9px] font-bold text-brand-text-dim/40 uppercase tracking-widest">
             Auto-Archiving in 12h 42m
           </div>
        </div>
      </div>
    </div>
  );
}
