import React, { useState, useRef } from 'react';
import { 
  FileUp, 
  X, 
  FileText, 
  CheckCircle2, 
  Eye, 
  Trash2, 
  Loader2,
  Tag,
  Search,
  History as HistoryIcon,
  ShieldCheck,
  User as UserIcon,
  Database,
  ArrowUpDown,
  ArrowUp,
  ArrowDown
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../lib/utils';
import { FileData, UserRole } from '../types';

interface DocumentsViewProps {
  role: UserRole;
}

const mockFiles: FileData[] = [
  { id: '1', name: 'Invoice_2024_Q1.pdf', size: 1200000, type: 'application/pdf', uploadDate: '2024-03-20', status: 'completed', progress: 100, classification: 'Invoice', extractedText: '{\n  "documentType": "Invoice",\n  "invoiceNumber": "INV-001",\n  "date": "2024-03-20",\n  "vendor": "Starlight Supplies",\n  "total": "RM 1,250.00",\n  "items": [\n    { "desc": "Premium Arabica", "qty": 50, "price": 25.00 }\n  ]\n}' },
  { id: '2', name: 'Staff_Contract_Template.docx', size: 450000, type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', uploadDate: '2024-03-19', status: 'completed', progress: 100, classification: 'Legal', extractedText: '{\n  "documentType": "Legal Contract",\n  "title": "Standard Employment Agreement",\n  "version": "v4.2",\n  "clausesCount": 24,\n  "lastReviewedBy": "Legal_Team"\n}' },
];

type SortField = 'uploadDate' | 'name' | 'size' | 'classification';
type SortOrder = 'asc' | 'desc';

export default function DocumentsView({ role }: DocumentsViewProps) {
  const [files, setFiles] = useState<FileData[]>(mockFiles);
  const [isDragging, setIsDragging] = useState(false);
  const [viewingFile, setViewingFile] = useState<FileData | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<SortField>('uploadDate');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const simulateUpload = (newFiles: File[]) => {
    const fileEntries: FileData[] = newFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      uploadDate: new Date().toISOString().split('T')[0],
      status: 'uploading',
      progress: 0,
    }));

    setFiles(prev => [...fileEntries, ...prev]);

    fileEntries.forEach(file => {
      let progress = 0;
      const interval = setInterval(() => {
        progress += 10;
        setFiles(current => 
          current.map(f => f.id === file.id ? { ...f, progress } : f)
        );
        if (progress >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setFiles(current => 
              current.map(f => f.id === file.id ? { 
                ...f, 
                status: 'completed', 
                classification: 'Automated Extraction',
                extractedText: '{\n  "intent": "NEW_DOC_RECOGNIZED",\n  "status": "ANALYZED",\n  "confidence": 0.94,\n  "extractedFields": { "detected": "Text/Meta" }\n}'
              } : f)
            );
          }, 800);
        }
      }, 150);
    });
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const filteredFiles = files
    .filter(f => 
      f.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.classification?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.extractedText?.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      let comp = 0;
      switch (sortField) {
        case 'name': comp = a.name.localeCompare(b.name); break;
        case 'uploadDate': comp = a.uploadDate.localeCompare(b.uploadDate); break;
        case 'size': comp = a.size - b.size; break;
        case 'classification': comp = (a.classification || '').localeCompare(b.classification || ''); break;
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
    <div className="space-y-6 pb-20 animate-in fade-in duration-500">
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold">{role === 'manager' ? 'The Vault (Audit Library)' : 'Document Hub'}</h2>
          <p className="text-brand-text-dim text-sm mt-0.5">
            {role === 'manager' ? 'Complete audit trail and library of all operational records.' : 'Streamline document ingestion and GLM vision processing.'}
          </p>
        </div>
        <div className="relative w-full sm:w-72">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-text-dim" />
          <input 
            type="text" 
            placeholder={role === 'manager' ? "Search library..." : "Search documents..."} 
            className="w-full bg-brand-surface border border-brand-border rounded-lg pl-10 pr-4 py-2 text-xs focus:border-brand-accent outline-none transition-all"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </header>

      <div className="flex items-center gap-2 overflow-x-auto pb-1 custom-scrollbar">
        <span className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em] mr-2 shrink-0">Sort By:</span>
        <SortButton field="uploadDate" label="Date" />
        <SortButton field="name" label="Name" />
        <SortButton field="size" label="Size" />
        <SortButton field="classification" label="Type" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        <div className="xl:col-span-8 space-y-6">
          {/* Staff Upload Section */}
          {role === 'staff' && (
            <div 
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(e) => { e.preventDefault(); setIsDragging(false); simulateUpload(Array.from(e.dataTransfer.files) as File[]); }}
              onClick={() => fileInputRef.current?.click()}
              className={cn(
                "relative border-2 border-dashed rounded-xl p-12 flex flex-col items-center justify-center transition-all cursor-pointer bg-brand-surface border-brand-border",
                isDragging && "border-brand-accent bg-brand-accent/5 scale-[0.99]"
              )}
            >
              <input type="file" hidden multiple ref={fileInputRef} onChange={(e) => e.target.files && simulateUpload(Array.from(e.target.files) as File[])} />
              <div className="w-16 h-16 rounded-xl bg-brand-bg border border-brand-border flex items-center justify-center mb-4 text-brand-accent">
                <FileUp size={32} />
              </div>
              <h3 className="text-md font-bold text-brand-text-main mb-1">Upload Source Evidence</h3>
              <p className="text-brand-text-dim text-xs uppercase tracking-widest font-bold">PDF, PNG, XLSX • Max 50MB</p>
            </div>
          )}

          {/* Library / List */}
          <div className="bg-brand-surface rounded-xl border border-brand-border overflow-hidden">
            <div className="p-4 border-b border-brand-border flex items-center justify-between bg-brand-bg/20">
              <h3 className="text-[10px] font-black text-brand-text-dim uppercase tracking-widest leading-none">
                {role === 'manager' ? 'Global Repository' : 'Recent Upload History'}
              </h3>
              <span className="text-[9px] font-bold text-brand-text-dim uppercase tracking-widest">{filteredFiles.length} Documents</span>
            </div>
            <div className="divide-y divide-brand-border/30">
              {filteredFiles.map((file) => (
                <div key={file.id} className="p-3 flex items-center justify-between group hover:bg-brand-bg/50 transition-colors">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className="w-10 h-10 bg-brand-bg border border-brand-border rounded-lg flex items-center justify-center text-brand-text-dim group-hover:text-brand-accent transition-all">
                      <FileText size={18} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-brand-text-main text-xs truncate">{file.name}</span>
                        {file.status === 'completed' && <CheckCircle2 size={12} className="text-brand-success shrink-0 shadow-[0_0_8px_var(--color-brand-success)]" />}
                      </div>
                      <div className="flex items-center gap-2 mt-0.5 text-[10px] font-bold text-brand-text-dim uppercase tracking-tighter opacity-60">
                        <span>{formatSize(file.size)}</span>
                        <div className="w-0.5 h-0.5 rounded-full bg-brand-border" />
                        <span>{file.uploadDate}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-1 ml-4 shrink-0">
                     {file.status === 'completed' ? (
                       <button 
                         onClick={() => setViewingFile(file)}
                         className="px-3 py-1.5 bg-brand-bg border border-brand-border hover:border-brand-accent text-brand-accent rounded-lg transition-all text-[10px] font-black uppercase tracking-widest flex items-center gap-2"
                       >
                         {role === 'manager' ? 'View Audit' : 'Extraction'} <Eye size={12} />
                       </button>
                     ) : (
                       <div className="flex items-center gap-2 px-3 py-1.5 text-brand-text-dim/50 text-[10px] font-bold uppercase tracking-widest">
                         <Loader2 size={12} className="animate-spin" /> Processing
                       </div>
                     )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Audit / Detail Panel */}
        <div className="xl:col-span-4 space-y-6">
          <AnimatePresence mode="wait">
            {viewingFile ? (
              <motion.div 
                key="preview-active"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="bg-brand-surface rounded-xl border border-brand-border p-6 shadow-2xl sticky top-6"
              >
                <div className="flex items-center justify-between mb-6">
                  <h3 className="font-black text-[11px] tracking-[0.2em] text-brand-text-main uppercase">{role === 'manager' ? 'Document Audit Log' : 'Master Extraction'}</h3>
                  <button onClick={() => setViewingFile(null)} className="p-1.5 hover:bg-brand-bg rounded-md transition-colors text-brand-text-dim">
                    <X size={16} />
                  </button>
                </div>

                <div className="space-y-6">
                  {role === 'manager' && (
                    <div className="space-y-3">
                       <h4 className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em]">Access History</h4>
                       <div className="space-y-2">
                          {[
                            { user: 'Staff_Alex', action: 'Uploaded', time: '14:20' },
                            { user: 'System_AI', action: 'Extracted', time: '14:21' },
                            { user: 'Manager_Sarah', action: 'Accessed PII', time: '14:45' }
                          ].map((log, i) => (
                            <div key={i} className="flex items-center justify-between p-2 bg-brand-bg/50 border border-brand-border rounded-lg text-[10px]">
                              <div className="flex items-center gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-brand-accent" />
                                <span className="font-bold text-brand-text-main">{log.user}</span>
                                <span className="text-brand-text-dim uppercase tracking-tighter opacity-50">{log.action}</span>
                              </div>
                              <span className="text-brand-text-dim font-mono">{log.time}</span>
                            </div>
                          ))}
                       </div>
                    </div>
                  )}

                  <div className="p-4 bg-brand-bg rounded-xl border border-brand-border relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-2 opacity-20 text-brand-success rotate-12">
                      <ShieldCheck size={40} />
                    </div>
                    <div className="flex items-center justify-between mb-3 text-[10px] font-black text-brand-text-dim tracking-[0.15em] uppercase">
                      <span>GLM VISION PAYLOAD</span>
                      <span className="text-brand-success">Verified</span>
                    </div>
                    <div className="font-mono text-[11px] leading-relaxed text-brand-text-main bg-black/40 p-3 rounded border border-brand-border/50 max-h-60 overflow-y-auto custom-scrollbar">
                       {viewingFile.extractedText}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button className="flex-1 py-3 bg-brand-accent text-white text-[10px] font-black rounded-lg transition-all active:scale-95 shadow-[0_0_20px_var(--color-brand-accent-glow)] uppercase tracking-[0.15em]">
                      Export Audit Trace
                    </button>
                  </div>
                </div>
              </motion.div>
            ) : (
              <div className="bg-brand-surface/30 rounded-xl border border-dashed border-brand-border p-12 text-center">
                <div className="w-12 h-12 bg-brand-bg border border-brand-border rounded-xl flex items-center justify-center mx-auto mb-4 text-brand-text-dim opacity-30">
                  <Database size={24} />
                </div>
                <h4 className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em]">Select Document for Audit</h4>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
