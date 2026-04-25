import React, { useState, useRef, useEffect } from 'react';
import { 
  FileUp, X, FileText, CheckCircle2, Eye, Trash2, 
  Loader2, Tag, Search, History as HistoryIcon, 
  ShieldCheck, User as UserIcon, Database, ArrowUpDown, ArrowUp, ArrowDown,
  RefreshCw, Plus
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../lib/utils';
import { FileData, UserRole } from '../types';

interface DocumentsViewProps {
  role: UserRole;
}

const mockFiles: FileData[] = [
  { id: '1', name: 'Invoice_2024_Q1.pdf', size: 1200000, type: 'application/pdf', uploadDate: '2024-03-20', status: 'completed', progress: 100, classification: 'Invoice', extractedText: '{\n  "documentType": "Invoice",\n  "vendor": "Starlight Supplies"\n}' },
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
  const [isSyncing, setIsSyncing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const fetchLibrary = async () => {
    setIsSyncing(true);
    try {
      // 1. Get the currently logged-in user
      const storedUser = localStorage.getItem('user');
      const currentUser = storedUser ? JSON.parse(storedUser) : null;
      
      // 2. Build the secure URL parameters
      const roleParam = `user_role=${role.toUpperCase()}`;
      const userParam = currentUser?.id ? `&user_id=${currentUser.id}` : '';
      
      // 3. Fetch with credentials
      const response = await fetch(`http://127.0.0.1:5000/api/intake/documents?limit=20&${roleParam}${userParam}`);
      const docs = await response.json();
      
      const historicalFiles: FileData[] = docs.map((doc: any) => {
        const realFileName = doc.gcs_url && doc.gcs_url !== "[RESTRICTED - View via Extraction Only]"
          ? doc.gcs_url.split('_').slice(1).join('_') 
          : `Document_${doc.id} (Secured)`;

        return {
          id: doc.id.toString(),
          name: realFileName,
          size: 0, 
          type: 'application/pdf',
          uploadDate: new Date(doc.created_at).toISOString().split('T')[0],
          status: 'completed', 
          progress: 100,
          classification: doc.source_platform
        };
      });
      
      setFiles(historicalFiles);
    } catch (err) {
      console.error("Failed to fetch document library", err);
    } finally {
      setIsSyncing(false);
    }
  };

  useEffect(() => {
    fetchLibrary();
  }, []);

  // --- UPLOAD LOGIC ---
  const handleFileUpload = async (newFiles: File[]) => {
    const fileEntries: FileData[] = newFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      uploadDate: new Date().toISOString().split('T')[0],
      status: 'uploading',
      progress: 30,
    }));

    setFiles(prev => [...fileEntries, ...prev]);

    const storedUser = localStorage.getItem('user');
    const currentUser = storedUser ? JSON.parse(storedUser) : null;

    for (const file of newFiles) {
      const formData = new FormData();
      formData.append('file', file);
      const sender_id = currentUser ? `WEB_${currentUser.username}` : `WEB_CLIENT_${role.toUpperCase()}`;
      formData.append('sender_id', sender_id);
      formData.append('user_role', role.toUpperCase());
      formData.append('source_platform', 'WEB');
      if (currentUser && currentUser.id) {
        formData.append("uploader_id", currentUser.id.toString());
      }

      try {
        const response = await fetch('http://127.0.0.1:5000/api/intake/document', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) throw new Error('Upload failed');
        const data = await response.json();

        // SAFETY CHECK: Duplicate Bouncer
        if (data.status === 'DUPLICATE') {
          alert(`Duplicate Found: ${data.message} (Original Document ID: ${data.existing_id})`);
          setFiles(current => current.filter(f => f.name !== file.name)); // Remove from UI
          continue; // Skip the rest of the loop
        }

        // SAFETY CHECK: Irrelevant Bouncer
        if (data.status === 'IRRELEVANT') {
          alert(`Rejected: ${data.message} Please upload a valid Order, Procurement, or Refund document.`);
          setFiles(current => current.filter(f => f.name !== file.name)); // Remove from UI
          continue; // Skip the rest of the loop
        }

        setFiles(current => 
          current.map(f => f.name === file.name ? { 
            ...f, 
            id: data.ticket.doc_id.toString(), // Fix: use doc_id from the ticket
            status: 'completed', 
            progress: 100,
            classification: data.master_json.classification.intent_category,
            extractedText: JSON.stringify(data.master_json, null, 2) 
          } : f)
        );
      } catch (error) {
        console.error("Inbound Error:", error);
        alert(`An error occurred while uploading ${file.name}`);
        setFiles(current => current.filter(f => f.name !== file.name));
      }
    }
  };

  const handleViewExtraction = async (file: FileData) => {
    try {
      const res = await fetch(`http://127.0.0.1:5000/api/intake/documents/${file.id}?user_role=${role.toUpperCase()}`);
      const data = await res.json();
      
      setViewingFile({
        ...file,
        extractedText: JSON.stringify(data.content_summary || data, null, 2)
      });
    } catch (err) {
      console.error("Security retrieval failed", err);
    }
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
    .filter(f => f.name.toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => {
      let comp = 0;
      switch (sortField) {
        case 'name': comp = a.name.localeCompare(b.name); break;
        case 'uploadDate': comp = a.uploadDate.localeCompare(b.uploadDate); break;
        case 'size': comp = a.size - b.size; break;
      }
      return sortOrder === 'asc' ? comp : -comp;
    });

  const SortButton = ({ field, label }: { field: SortField, label: string }) => (
    <button onClick={() => handleSort(field)} className={cn("flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-[10px] font-bold uppercase tracking-widest transition-all", sortField === field ? "bg-brand-accent/10 border-brand-accent text-brand-accent" : "bg-brand-surface border-brand-border text-brand-text-dim hover:border-brand-text-dim/50")}>
      {label} {sortField === field && (sortOrder === 'asc' ? <ArrowUp size={12} /> : <ArrowDown size={12} />)}
    </button>
  );

  return (
    <div className="relative min-h-screen space-y-6 pb-24 animate-in fade-in duration-500">
      {/* 1. HEADER SECTION */}
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold">{role === 'manager' ? 'The Vault (Audit Library)' : 'Document Hub'}</h2>
          <p className="text-brand-text-dim text-sm mt-0.5">Streamline document ingestion and GLM vision processing.</p>
        </div>
        <div className="relative w-full sm:w-72">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-text-dim" />
          <input type="text" placeholder="Search library..." className="w-full bg-brand-surface border border-brand-border rounded-lg pl-10 pr-4 py-2 text-xs focus:border-brand-accent outline-none transition-all" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
        </div>
      </header>

      {/* 2. SORTING BAR */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 custom-scrollbar">
        <span className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em] mr-2 shrink-0">Sort By:</span>
        <SortButton field="uploadDate" label="Date" />
        <SortButton field="name" label="Name" />
        <SortButton field="size" label="Size" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        {/* 3. MAIN LIST */}
        <div className="xl:col-span-8 space-y-6">
          {role === 'staff' && (
            <div 
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(e) => { e.preventDefault(); setIsDragging(false); handleFileUpload(Array.from(e.dataTransfer.files) as File[]); }}
              onClick={() => fileInputRef.current?.click()}
              className={cn("relative border-2 border-dashed rounded-xl p-12 flex flex-col items-center justify-center cursor-pointer bg-brand-surface border-brand-border transition-all hover:bg-brand-surface/80", isDragging && "border-brand-accent bg-brand-accent/5")}
            >
              <input type="file" hidden multiple ref={fileInputRef} onChange={(e) => e.target.files && handleFileUpload(Array.from(e.target.files) as File[])} />
              <div className="w-16 h-16 rounded-xl bg-brand-bg border border-brand-border flex items-center justify-center mb-4 text-brand-accent transition-transform group-hover:scale-110"><FileUp size={32} /></div>
              <h3 className="text-md font-bold text-brand-text-main mb-1">Upload Source Evidence</h3>
              <p className="text-brand-text-dim text-xs uppercase tracking-widest font-bold">Excel, Word, PDF, PPT • Max 50MB</p>
            </div>
          )}

          <div className="bg-brand-surface rounded-xl border border-brand-border overflow-hidden shadow-sm">
            <div className="p-4 border-b border-brand-border flex items-center justify-between bg-brand-bg/20">
              <h3 className="text-[10px] font-black text-brand-text-dim uppercase tracking-widest">Global Repository</h3>
              <span className="text-[9px] font-bold text-brand-text-dim uppercase tracking-widest">{filteredFiles.length} Documents</span>
            </div>
            <div className="divide-y divide-brand-border/30 max-h-[600px] overflow-y-auto custom-scrollbar">
              {filteredFiles.map((file) => (
                <div key={file.id} className="p-3 flex items-center justify-between group hover:bg-brand-bg/50 transition-colors">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className="w-10 h-10 bg-brand-bg border border-brand-border rounded-lg flex items-center justify-center text-brand-text-dim group-hover:text-brand-accent transition-colors"><FileText size={18} /></div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-brand-text-main text-xs truncate">{file.name}</span>
                        {file.status === 'completed' && <CheckCircle2 size={12} className="text-brand-success shadow-[0_0_8px_rgba(34,197,94,0.4)]" />}
                      </div>
                      <div className="flex items-center gap-2 mt-0.5 text-[10px] font-bold text-brand-text-dim uppercase opacity-60">
                        <span>{formatSize(file.size)}</span> • <span>{file.uploadDate}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 ml-4 shrink-0">
                     {file.status === 'completed' ? (
                       <button onClick={() => handleViewExtraction(file)} className="px-3 py-1.5 bg-brand-bg border border-brand-border hover:border-brand-accent text-brand-accent rounded-lg text-[10px] font-black uppercase tracking-widest flex items-center gap-2 transition-all active:scale-95">
                         Extraction <Eye size={12} />
                       </button>
                     ) : (
                       <div className="flex items-center gap-2 px-3 py-1.5 text-brand-text-dim/50 text-[10px] font-bold uppercase"><Loader2 size={12} className="animate-spin" /> Processing</div>
                     )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 4. PREVIEW PANEL */}
        <div className="xl:col-span-4 space-y-6">
          <AnimatePresence mode="wait">
            {viewingFile ? (
              <motion.div key="preview" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} className="bg-brand-surface rounded-xl border border-brand-border p-6 shadow-2xl sticky top-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="font-black text-[11px] tracking-[0.2em] text-brand-text-main uppercase">Master Extraction</h3>
                  <button onClick={() => setViewingFile(null)} className="p-1.5 hover:bg-brand-bg rounded-md text-brand-text-dim transition-colors"><X size={16} /></button>
                </div>
                <div className="space-y-6">
                  <div className="p-4 bg-brand-bg rounded-xl border border-brand-border relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-2 opacity-10 text-brand-success rotate-12"><ShieldCheck size={40} /></div>
                    <div className="flex items-center justify-between mb-3 text-[10px] font-black text-brand-text-dim uppercase">
                      <span>GLM VISION PAYLOAD</span> <span className="text-brand-success">Verified</span>
                    </div>
                    <div className="font-mono text-[11px] leading-relaxed text-brand-text-main bg-black/40 p-3 rounded border border-brand-border/50 max-h-96 overflow-y-auto custom-scrollbar whitespace-pre-wrap">
                       {viewingFile.extractedText || "// No extraction data available"}
                    </div>
                  </div>
                  <button className="w-full py-3 bg-brand-accent text-white text-[10px] font-black rounded-lg shadow-[0_0_20px_rgba(var(--brand-accent-rgb),0.3)] hover:shadow-[0_0_25px_rgba(var(--brand-accent-rgb),0.5)] transition-all uppercase tracking-[0.15em] active:scale-[0.98]">
                    Export Audit Trace
                  </button>
                </div>
              </motion.div>
            ) : (
              <div className="bg-brand-surface/30 rounded-xl border border-dashed border-brand-border p-12 text-center">
                <div className="w-12 h-12 bg-brand-bg border border-brand-border rounded-xl flex items-center justify-center mx-auto mb-4 text-brand-text-dim opacity-30"><Database size={24} /></div>
                <h4 className="text-[10px] font-black text-brand-text-dim uppercase tracking-[0.2em]">Select Document for Audit</h4>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* 5. FIXED BUTTON PLACEMENT (Floating Action Button) */}
      <div className="fixed bottom-8 right-8 flex flex-col gap-3 items-end z-50">
        {/* Secondary Fixed Button: Refresh/Sync */}
        <button 
          onClick={fetchLibrary}
          disabled={isSyncing}
          className="p-3 bg-brand-surface border border-brand-border rounded-full shadow-xl text-brand-text-main hover:text-brand-accent hover:border-brand-accent transition-all group"
          title="Refresh Library"
        >
          <RefreshCw size={20} className={cn("transition-transform", isSyncing && "animate-spin")} />
        </button>

        {/* Primary Fixed Button: Quick Action */}
        <button 
          onClick={() => fileInputRef.current?.click()}
          className="flex items-center gap-3 px-6 py-4 bg-brand-accent text-white rounded-full shadow-[0_8px_30px_rgba(var(--brand-accent-rgb),0.4)] hover:shadow-[0_12px_40px_rgba(var(--brand-accent-rgb),0.6)] transition-all transform hover:-translate-y-1 active:scale-95 group"
        >
          <span className="text-xs font-black uppercase tracking-widest hidden md:block">New Ingestion</span>
          <Plus size={24} className="group-hover:rotate-90 transition-transform duration-300" />
        </button>
      </div>
    </div>
  );
}