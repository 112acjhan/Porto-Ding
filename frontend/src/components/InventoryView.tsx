import React, { useState, useEffect } from 'react';
import { 
  Package, Search, AlertTriangle, TrendingUp, 
  Box, Plus, ArrowUpDown, Loader2, Trash2, Edit2, X 
} from 'lucide-react';
import { cn } from '../lib/utils';

// --- Types to match your FastAPI Pydantic models ---
interface InventoryItem {
  item_id: string;
  item_name: string;
  stock_level: number;
  reorder_point: number;
  unit_price: number;
}

export default function InventoryBaseView() {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentItem, setCurrentItem] = useState<InventoryItem>({
    item_id: '',
    item_name: '',
    stock_level: 0,
    reorder_point: 0,
    unit_price: 0
  });

  const API_URL = 'http://localhost:5000/api/inventory';

  // 1. FETCH ALL
  const fetchInventory = async () => {
    try {
      setLoading(true);
      const response = await fetch(API_URL);
      const data = await response.json();
      setInventory(data);
    } catch (error) {
      console.error("Fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchInventory(); }, []);

  // 2. DELETE
  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this item?")) return;
    try {
      const response = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
      if (response.ok) fetchInventory();
    } catch (error) {
      console.error("Delete error:", error);
    }
  };

  // 3. ADD / UPDATE SUBMIT
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const method = isEditing ? 'PUT' : 'POST';
    const url = isEditing ? `${API_URL}/${currentItem.item_id}` : API_URL;

    try {
      const response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentItem),
      });

      if (response.ok) {
        setIsModalOpen(false);
        fetchInventory();
        resetForm();
      } else {
        const err = await response.json();
        alert(`Error: ${err.detail}`);
      }
    } catch (error) {
      console.error("Submit error:", error);
    }
  };

  const resetForm = () => {
    setCurrentItem({ item_id: '', item_name: '', stock_level: 0, reorder_point: 0, unit_price: 0 });
    setIsEditing(false);
  };

  const openEditModal = (item: InventoryItem) => {
    setCurrentItem(item);
    setIsEditing(true);
    setIsModalOpen(true);
  };

  const filteredItems = inventory.filter(item => 
    item.item_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.item_id.toString().includes(searchTerm)
  );

  return (
    <div className="space-y-6 pb-20 animate-in fade-in duration-500">
      {/* Header */}
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold">Live Inventory Ledger</h2>
          <p className="text-brand-text-dim text-sm mt-0.5">Connected to Google Sheets API</p>
        </div>
        <button 
          onClick={() => { resetForm(); setIsModalOpen(true); }}
          className="flex items-center gap-2 px-4 py-2 bg-brand-accent text-white rounded-lg text-sm font-bold transition-all shadow-lg hover:brightness-110"
        >
          <Plus size={18} /> Add New Item
        </button>
      </header>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard label="Total SKUs" value={inventory.length} icon={Box} color="text-brand-accent" />
        <StatCard 
          label="Low Stock Alerts" 
          value={inventory.filter(i => i.stock_level < i.reorder_point).length} 
          icon={AlertTriangle} 
          color="text-rose-500" 
        />
        <StatCard label="Total Value" value={`$${inventory.reduce((acc, curr) => acc + (curr.stock_level * curr.unit_price), 0).toFixed(2)}`} icon={TrendingUp} color="text-brand-success" />
      </div>

      {/* Main Table */}
      <div className="bg-brand-surface border border-brand-border rounded-xl overflow-hidden">
        <div className="p-4 border-b border-brand-border bg-brand-bg/50">
          <div className="relative w-full md:w-96">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-text-dim" />
            <input 
              type="text" 
              placeholder="Search by name or ID..." 
              className="w-full bg-brand-bg border border-brand-border rounded-lg pl-10 pr-4 py-2 text-xs outline-none focus:border-brand-accent"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-brand-bg/30 text-[10px] uppercase tracking-widest text-brand-text-dim font-bold">
                <th className="px-6 py-4 border-b border-brand-border">Item ID</th>
                <th className="px-6 py-4 border-b border-brand-border">Product Name</th>
                <th className="px-6 py-4 border-b border-brand-border">Stock Level</th>
                <th className="px-6 py-4 border-b border-brand-border">Price</th>
                <th className="px-6 py-4 border-b border-brand-border">Status</th>
                <th className="px-6 py-4 border-b border-brand-border text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="text-xs">
              {loading ? (
                <tr><td colSpan={6} className="text-center py-10"><Loader2 className="animate-spin mx-auto" /></td></tr>
              ) : filteredItems.map((item) => (
                <tr key={item.item_id} className="hover:bg-brand-bg/20 transition-colors group">
                  <td className="px-6 py-4 border-b border-brand-border font-mono text-brand-text-dim">{item.item_id}</td>
                  <td className="px-6 py-4 border-b border-brand-border font-bold">{item.item_name}</td>
                  <td className="px-6 py-4 border-b border-brand-border font-black">{item.stock_level}</td>
                  <td className="px-6 py-4 border-b border-brand-border text-brand-text-dim">${item.unit_price}</td>
                  <td className="px-6 py-4 border-b border-brand-border">
                    {item.stock_level < item.reorder_point ? (
                      <span className="px-2 py-1 bg-rose-500/10 text-rose-500 text-[9px] font-black rounded">LOW STOCK</span>
                    ) : (
                      <span className="px-2 py-1 bg-brand-success/10 text-brand-success text-[9px] font-black rounded">OPTIMAL</span>
                    )}
                  </td>
                  <td className="px-6 py-4 border-b border-brand-border text-right">
                    <div className="flex justify-end gap-2">
                      <button onClick={() => openEditModal(item)} className="p-2 hover:bg-brand-bg rounded text-brand-text-dim hover:text-brand-accent transition-colors"><Edit2 size={14} /></button>
                      <button onClick={() => handleDelete(item.item_id)} className="p-2 hover:bg-brand-bg rounded text-brand-text-dim hover:text-rose-500 transition-colors"><Trash2 size={14} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ADD/EDIT MODAL */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-brand-surface border border-brand-border rounded-2xl w-full max-w-md shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between p-6 border-b border-brand-border">
              <h3 className="text-lg font-bold">{isEditing ? 'Edit Item' : 'Add New Item'}</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-brand-text-dim hover:text-white"><X size={20} /></button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="text-[10px] uppercase font-bold text-brand-text-dim">Item ID (Unique)</label>
                <input 
                  disabled={isEditing}
                  required
                  className="w-full bg-brand-bg border border-brand-border rounded-lg px-4 py-2 mt-1 outline-none focus:border-brand-accent disabled:opacity-50"
                  value={currentItem.item_id}
                  onChange={e => setCurrentItem({...currentItem, item_id: e.target.value})}
                />
              </div>
              <div>
                <label className="text-[10px] uppercase font-bold text-brand-text-dim">Product Name</label>
                <input 
                  required
                  className="w-full bg-brand-bg border border-brand-border rounded-lg px-4 py-2 mt-1 outline-none focus:border-brand-accent"
                  value={currentItem.item_name}
                  onChange={e => setCurrentItem({...currentItem, item_name: e.target.value})}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] uppercase font-bold text-brand-text-dim">Stock Level</label>
                  <input 
                    type="number" required
                    className="w-full bg-brand-bg border border-brand-border rounded-lg px-4 py-2 mt-1 outline-none focus:border-brand-accent"
                    value={currentItem.stock_level}
                    onChange={e => setCurrentItem({...currentItem, stock_level: Number(e.target.value)})}
                  />
                </div>
                <div>
                  <label className="text-[10px] uppercase font-bold text-brand-text-dim">Unit Price</label>
                  <input 
                    type="number" step="0.01" required
                    className="w-full bg-brand-bg border border-brand-border rounded-lg px-4 py-2 mt-1 outline-none focus:border-brand-accent"
                    value={currentItem.unit_price}
                    onChange={e => setCurrentItem({...currentItem, unit_price: Number(e.target.value)})}
                  />
                </div>
              </div>
              <div>
                <label className="text-[10px] uppercase font-bold text-brand-text-dim">Reorder Point</label>
                <input 
                  type="number" required
                  className="w-full bg-brand-bg border border-brand-border rounded-lg px-4 py-2 mt-1 outline-none focus:border-brand-accent"
                  value={currentItem.reorder_point}
                  onChange={e => setCurrentItem({...currentItem, reorder_point: Number(e.target.value)})}
                />
              </div>
              <button type="submit" className="w-full py-3 bg-brand-accent text-white rounded-lg font-bold mt-4 hover:brightness-110 transition-all">
                {isEditing ? 'Update Item' : 'Create Item'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

// Simple Helper Component for Stats
function StatCard({ label, value, icon: Icon, color }: any) {
  return (
    <div className="bg-brand-surface p-5 rounded-xl border border-brand-border flex items-center gap-4">
      <div className={cn("p-3 rounded-xl bg-brand-bg", color)}><Icon size={24} /></div>
      <div>
        <p className="text-[10px] font-bold text-brand-text-dim uppercase tracking-widest leading-none mb-1">{label}</p>
        <p className="text-xl font-bold text-brand-text-main">{value}</p>
      </div>
    </div>
  );
}