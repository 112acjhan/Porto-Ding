/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  ArrowUpRight, 
  FileText, 
  Zap, 
  Activity,
  ChevronRight
} from 'lucide-react';
import { motion } from 'motion/react';
import { cn } from '../lib/utils';

const activityLog = [
  { id: 1, type: 'upload', title: 'Invoice_Q3_Boutique.pdf uploaded', time: '2 mins ago', status: 'success' },
  { id: 2, type: 'action', title: 'Automated email sent to Vendor X', time: '15 mins ago', status: 'success' },
  { id: 3, type: 'processing', title: 'Inventory update initiated', time: '1 hour ago', status: 'pending' },
  { id: 4, type: 'error', title: 'File format error: receipt_corrupted.png', time: '3 hours ago', status: 'failed' },
];

const staffTickets = [
  { id: 'T-102', task: 'Refund Request: #ORD-9921', priority: 'High', status: 'Pending' },
  { id: 'T-105', task: 'Customer Support: Missing Item', priority: 'Medium', status: 'Active' },
  { id: 'T-108', task: 'New Inquiry: Loyalty Program', priority: 'Low', status: 'Review' },
];

const accountantTickets = [
  { id: 'T-201', task: 'Inventory Reconciliation: Coffee Stock', priority: 'High', status: 'Required' },
  { id: 'T-204', task: 'Tax Filing: Q1 GST Preparation', priority: 'Medium', status: 'In Progress' },
  { id: 'T-209', task: 'Audit Trace: Vendor Payment Discrepancy', priority: 'High', status: 'Escalated' },
];

interface DashboardViewProps {
  role?: string;
}

export default function DashboardView({ role }: DashboardViewProps) {
  return (
    <div className="space-y-6 pb-10">
      <header className="flex justify-between items-center border-b border-brand-border pb-4">
        <div>
          <h2 className="text-xl font-bold">{role === 'manager' ? 'Executive Oversight' : 'System Operations Console'}</h2>
          <p className="text-brand-text-dim text-sm mt-0.5">
            {role === 'manager' 
              ? 'Real-time status of staff tickets and decision logs.' 
              : 'Priority operational tickets and system task status.'}
          </p>
        </div>
      </header>

      <section className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        {/* Role Specific Content */}
        {role === 'manager' ? (
          <>
            <div className="xl:col-span-8 bg-brand-surface p-6 rounded-xl border border-brand-border h-full flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em]">Pending Operational Approvals</h2>
                <button className="text-[10px] font-bold text-brand-accent uppercase tracking-widest hover:underline">View All</button>
              </div>
              <div className="space-y-3">
                 {[...staffTickets, ...accountantTickets.slice(0, 1)].map((ticket, idx) => (
                   <div key={idx} className="p-4 bg-brand-bg/50 border border-brand-border rounded-lg flex items-center justify-between group hover:border-brand-accent/30 transition-all">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-brand-surface border border-brand-border flex items-center justify-center text-brand-text-dim">
                          <Activity size={18} />
                        </div>
                        <div>
                          <p className="text-xs font-bold text-brand-text-main">{ticket.task}</p>
                          <p className="text-[9px] font-bold text-brand-text-dim uppercase mt-0.5">Ticket ID: {ticket.id} • Priority: {ticket.priority}</p>
                        </div>
                      </div>
                      <button className="px-3 py-1.5 bg-brand-accent/10 text-brand-accent text-[9px] font-black uppercase tracking-widest rounded transition-colors hover:bg-brand-accent hover:text-white border border-brand-accent/20">
                        Review
                      </button>
                   </div>
                 ))}
              </div>
            </div>

            <div className="xl:col-span-4 space-y-6">
              <div className="bg-brand-surface p-6 rounded-xl border border-brand-border h-full flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em]">System Event Feed</h2>
                </div>
                <div className="space-y-4">
                  {activityLog.map((log) => (
                    <div key={log.id} className="flex gap-4 items-center group text-brand-text-main">
                      <div className={cn(
                        "w-2 h-2 rounded-full shrink-0 shadow-[0_0_8px_currentColor]",
                        log.status === 'success' ? "text-brand-success" : "text-rose-500"
                      )} />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium truncate">{log.title}</p>
                        <p className="text-[9px] text-brand-text-dim mt-0.5 uppercase tracking-tighter font-bold">{log.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        ) : role === 'staff' ? (
          <>
            <div className="xl:col-span-8 bg-brand-surface p-6 rounded-xl border border-brand-border flex flex-col">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em]">Operational Task Pipeline</h2>
                <span className="text-[10px] font-bold text-brand-accent uppercase tracking-widest">{staffTickets.length} Priority Tasks</span>
              </div>
              <div className="space-y-4">
                {staffTickets.map((ticket) => (
                  <div key={ticket.id} className="flex items-center justify-between p-4 bg-brand-bg/50 border border-brand-border rounded-xl group hover:border-brand-accent/50 transition-all">
                    <div className="flex items-center gap-4">
                       <div className="w-10 h-10 rounded-lg bg-brand-bg border border-brand-border flex items-center justify-center text-brand-text-dim group-hover:text-brand-accent transition-colors">
                         <Clock size={18} />
                       </div>
                       <div>
                         <div className="flex items-center gap-2">
                            <span className="text-[10px] font-black text-brand-accent uppercase tracking-tighter">{ticket.id}</span>
                            <span className={cn(
                              "text-[8px] font-black px-1.5 py-0.5 rounded border uppercase tracking-widest",
                              ticket.priority === 'High' ? "bg-rose-500/10 text-rose-500 border-rose-500/20" : "bg-brand-bg border-brand-border text-brand-text-dim"
                            )}>
                              {ticket.priority} Priority
                            </span>
                         </div>
                         <p className="text-sm font-bold text-brand-text-main mt-1">{ticket.task}</p>
                       </div>
                    </div>
                    <button className="px-4 py-2 bg-brand-accent/10 hover:bg-brand-accent text-brand-accent hover:text-white text-[10px] font-black uppercase tracking-widest rounded-lg transition-all border border-brand-accent/20">
                      Process
                    </button>
                  </div>
                ))}
              </div>
            </div>
            <div className="xl:col-span-4 bg-brand-surface p-6 rounded-xl border border-brand-border">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em]">Execution Stream</h2>
              </div>
              <div className="space-y-4">
                {activityLog.map((log) => (
                  <div key={log.id} className="flex gap-4 items-center group text-brand-text-main">
                    <div className={cn(
                      "w-2 h-2 rounded-full shrink-0 shadow-[0_0_8px_currentColor]",
                      log.status === 'success' ? "text-brand-success" : "text-rose-500"
                    )} />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium truncate">{log.title}</p>
                      <p className="text-[9px] text-brand-text-dim mt-0.5 uppercase tracking-tighter font-bold">{log.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : (
          /* Accountant view */
          <>
            <div className="xl:col-span-8 bg-brand-surface p-6 rounded-xl border border-brand-border flex flex-col">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em]">Accounting Ticket Console</h2>
                <span className="text-[10px] font-bold text-brand-success uppercase tracking-widest">Inventory Sync Active</span>
              </div>
              <div className="space-y-4">
                {accountantTickets.map((ticket) => (
                  <div key={ticket.id} className="flex items-center justify-between p-4 bg-brand-bg/50 border border-brand-border rounded-xl group hover:border-brand-success/50 transition-all">
                    <div className="flex items-center gap-4">
                       <div className="w-10 h-10 rounded-lg bg-brand-bg border border-brand-border flex items-center justify-center text-brand-text-dim group-hover:text-brand-success transition-colors">
                         <FileText size={18} />
                       </div>
                       <div>
                         <div className="flex items-center gap-2">
                            <span className="text-[10px] font-black text-brand-success uppercase tracking-tighter">{ticket.id}</span>
                            <span className="text-[8px] font-black px-1.5 py-0.5 rounded border border-brand-border bg-brand-bg text-brand-text-dim uppercase tracking-widest">
                              {ticket.status}
                            </span>
                         </div>
                         <p className="text-sm font-bold text-brand-text-main mt-1">{ticket.task}</p>
                       </div>
                    </div>
                    <button className="px-4 py-2 bg-brand-success/10 hover:bg-brand-success text-brand-success hover:text-white text-[10px] font-black uppercase tracking-widest rounded-lg transition-all border border-brand-success/20">
                      Review
                    </button>
                  </div>
                ))}
              </div>
            </div>
            <div className="xl:col-span-4 bg-brand-surface p-6 rounded-xl border border-brand-border">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em]">Financial Pulse</h2>
              </div>
              <div className="space-y-6">
                 {[
                   { label: 'Unreconciled', val: '14', color: 'text-amber-500' },
                   { label: 'Verified Docs', val: '412', color: 'text-brand-success' },
                   { label: 'Anomaly Count', val: '0', color: 'text-brand-text-dim' },
                 ].map(item => (
                   <div key={item.label}>
                     <div className="flex justify-between items-end mb-2">
                        <span className="text-[10px] font-black text-brand-text-dim uppercase tracking-widest">{item.label}</span>
                        <span className={cn("text-xl font-black", item.color)}>{item.val}</span>
                     </div>
                     <div className="w-full h-1 bg-brand-bg rounded-full overflow-hidden">
                        <div className={cn("h-full w-2/3 bg-current", item.color)} />
                     </div>
                   </div>
                 ))}
              </div>
            </div>
          </>
        )}
      </section>
    </div>
  );
}
