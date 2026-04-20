import React, { useState } from 'react';
import { 
  Package, 
  Search, 
  AlertTriangle, 
  TrendingUp, 
  Box, 
  History,
  Filter,
  Download,
  Plus,
  ArrowUpDown,
  ArrowUp,
  ArrowDown
} from 'lucide-react';
import { cn } from '../lib/utils';
import { InventoryItem } from '../types';

const mockInventory: InventoryItem[] = [
  { id: '1', name: 'Premium Arabica Beans', sku: 'ARB-001', quantity: 450, minThreshold: 500, category: 'Coffee', lastUpdated: '2024-03-21' },
  { id: '2', name: 'Paper Cups 12oz', sku: 'CUP-12', quantity: 1200, minThreshold: 200, category: 'Packaging', lastUpdated: '2024-03-20' },
  { id: '3', name: 'Organic Soy Milk', sku: 'MLK-SOY', quantity: 42, minThreshold: 50, category: 'Dairy', lastUpdated: '2024-03-21' },
  { id: '4', name: 'Brown Sugar Packets', sku: 'SGR-B', quantity: 5000, minThreshold: 1000, category: 'Condiments', lastUpdated: '2024-03-15' },
  { id: '5', name: 'Coffee Grinder Blades', sku: 'MNT-BLD', quantity: 15, minThreshold: 20, category: 'Maintenance', lastUpdated: '2024-03-10' },
];

type SortField = 'name' | 'sku' | 'quantity' | 'status' | 'lastUpdated';
type SortOrder = 'asc' | 'desc';

export default function InventoryBaseView() {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<SortField>('lastUpdated');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const filteredItems = mockInventory
    .filter(item => 
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.category.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      let comparison = 0;
      
      switch (sortField) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'sku':
          comparison = a.sku.localeCompare(b.sku);
          break;
        case 'quantity':
          comparison = a.quantity - b.quantity;
          break;
        case 'lastUpdated':
          comparison = new Date(a.lastUpdated).getTime() - new Date(b.lastUpdated).getTime();
          break;
        case 'status':
          const aLow = a.quantity < a.minThreshold;
          const bLow = b.quantity < b.minThreshold;
          comparison = aLow === bLow ? 0 : aLow ? -1 : 1;
          break;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <ArrowUpDown size={12} className="opacity-30" />;
    return sortOrder === 'asc' ? <ArrowUp size={12} className="text-brand-accent" /> : <ArrowDown size={12} className="text-brand-accent" />;
  };

  return (
    <div className="space-y-6 pb-20 animate-in fade-in duration-500">
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold">Live Inventory Ledger</h2>
          <p className="text-brand-text-dim text-sm mt-0.5">Adaptive inventory tracking synced with operational extraction.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-3 py-2 bg-brand-surface border border-brand-border rounded-lg text-xs font-bold text-brand-text-main hover:bg-brand-bg transition-all">
            <Download size={14} /> Export CSV
          </button>
          <button className="flex items-center gap-2 px-3 py-2 bg-brand-accent text-white rounded-lg text-xs font-bold transition-all shadow-lg shadow-brand-accent/20">
            <Plus size={14} /> Add Item
          </button>
        </div>
      </header>

      {/* Global Inventory Health */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'Total SKU count', value: '42 Active', icon: Box, color: 'text-brand-accent' },
          { label: 'Inventory Turnover', value: '14.2%', icon: TrendingUp, color: 'text-brand-success' },
          { label: 'Stock Alerts', value: '3 Critical', icon: AlertTriangle, color: 'text-rose-500' },
        ].map((stat) => (
          <div key={stat.label} className="bg-brand-surface p-5 rounded-xl border border-brand-border flex items-center gap-4">
            <div className={cn("p-3 rounded-xl bg-brand-bg", stat.color)}>
              <stat.icon size={24} />
            </div>
            <div>
              <p className="text-[10px] font-bold text-brand-text-dim uppercase tracking-widest leading-none mb-1">{stat.label}</p>
              <p className="text-xl font-bold text-brand-text-main">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Inventory Table */}
      <div className="bg-brand-surface border border-brand-border rounded-xl overflow-hidden shadow-2xl">
        <div className="p-4 border-b border-brand-border bg-brand-bg/50 flex flex-col md:flex-row gap-4 items-center justify-between">
           <div className="relative w-full md:w-96">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-text-dim" />
              <input 
                type="text" 
                placeholder="Product name or SKU..." 
                className="w-full bg-brand-bg border border-brand-border rounded-lg pl-10 pr-4 py-2 text-xs focus:border-brand-accent transition-all outline-none"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
           </div>
           <div className="flex items-center gap-2">
              <button className="p-2 hover:bg-brand-bg rounded-lg text-brand-text-dim"><Filter size={16} /></button>
           </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-brand-bg/30 text-[10px] uppercase tracking-widest text-brand-text-dim font-bold">
                <th className="px-6 py-4 border-b border-brand-border cursor-pointer hover:text-brand-accent transition-colors group" onClick={() => handleSort('name')}>
                  <div className="flex items-center gap-2">
                    Product <SortIcon field="name" />
                  </div>
                </th>
                <th className="px-6 py-4 border-b border-brand-border cursor-pointer hover:text-brand-accent transition-colors group" onClick={() => handleSort('sku')}>
                  <div className="flex items-center gap-2">
                    SKU <SortIcon field="sku" />
                  </div>
                </th>
                <th className="px-6 py-4 border-b border-brand-border cursor-pointer hover:text-brand-accent transition-colors group" onClick={() => handleSort('quantity')}>
                  <div className="flex items-center gap-2">
                    Quantity <SortIcon field="quantity" />
                  </div>
                </th>
                <th className="px-6 py-4 border-b border-brand-border cursor-pointer hover:text-brand-accent transition-colors group" onClick={() => handleSort('status')}>
                  <div className="flex items-center gap-2">
                    Status <SortIcon field="status" />
                  </div>
                </th>
                <th className="px-6 py-4 border-b border-brand-border cursor-pointer hover:text-brand-accent transition-colors group" onClick={() => handleSort('lastUpdated')}>
                  <div className="flex items-center gap-2">
                    Last Updated <SortIcon field="lastUpdated" />
                  </div>
                </th>
                <th className="px-6 py-4 border-b border-brand-border">Action</th>
              </tr>
            </thead>
            <tbody className="text-xs">
              {filteredItems.map((item) => {
                const isLowStock = item.quantity < item.minThreshold;
                return (
                  <tr key={item.id} className="hover:bg-brand-bg/20 transition-colors group">
                    <td className="px-6 py-4 border-b border-brand-border">
                       <div className="flex items-center gap-3">
                          <div className="p-2 bg-brand-bg rounded-lg text-brand-text-dim group-hover:text-brand-accent transition-colors">
                            <Package size={16} />
                          </div>
                          <div>
                            <p className="font-bold text-brand-text-main">{item.name}</p>
                            <p className="text-[10px] text-brand-text-dim opacity-50">{item.category}</p>
                          </div>
                       </div>
                    </td>
                    <td className="px-6 py-4 border-b border-brand-border font-mono text-brand-text-dim">{item.sku}</td>
                    <td className="px-6 py-4 border-b border-brand-border">
                      <span className={cn("font-black tabular-nums", isLowStock ? "text-rose-500" : "text-brand-text-main")}>
                        {item.quantity.toLocaleString()}
                      </span>
                    </td>
                    <td className="px-6 py-4 border-b border-brand-border">
                      {isLowStock ? (
                        <div className="inline-flex items-center gap-1.5 px-2 py-1 bg-rose-500/10 text-rose-500 border border-rose-500/20 rounded text-[9px] font-black uppercase tracking-tighter">
                          <AlertTriangle size={10} /> LOW STOCK
                        </div>
                      ) : (
                        <div className="inline-flex items-center gap-1.5 px-2 py-1 bg-brand-success/10 text-brand-success border border-brand-success/20 rounded text-[9px] font-black uppercase tracking-tighter">
                          <div className="w-1.5 h-1.5 rounded-full bg-brand-success" /> OPTIMAL
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 border-b border-brand-border text-brand-text-dim">{item.lastUpdated}</td>
                    <td className="px-6 py-4 border-b border-brand-border">
                      <button className="text-brand-accent font-bold hover:underline transition-all">Details</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
