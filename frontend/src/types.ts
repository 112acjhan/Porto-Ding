/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export type SystemStatus = 'Document Processing' | 'RAG Status' | 'GLM Status';
export type StatusLevel = 'Healthy' | 'Busy' | 'Slow' | 'Error';

export interface Activity {
  id: string;
  type: 'upload' | 'processing' | 'action' | 'search';
  title: string;
  timestamp: string;
  status: 'success' | 'failed' | 'pending';
  details?: string;
}

export interface FileData {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadDate: string;
  extractedText?: string;
  classification?: string;
  status: 'uploading' | 'completed' | 'processing';
  progress: number;
}

export interface PipelineStep {
  id: string;
  label: string;
  status: 'waiting' | 'active' | 'completed' | 'error';
  description: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  content: string;
  timestamp: string;
  isThinking?: boolean;
  type?: 'text' | 'action';
  actionDetails?: {
    tool: string;
    result: string;
    status: 'success' | 'failed';
  };
}

export interface KnowledgeBaseItem {
  id: string;
  title: string;
  summary: string;
  sourceFiles: string[];
  embeddingsCount: number;
  lastUpdated: string;
}

export interface Ticket {
  id: string;
  source: string; // e.g., "WhatsApp Image", "PDF Invoice"
  evidenceUrl: string;
  task: string;
  state: 'Processing' | 'Pending Manager Approval' | 'Ready to Ship' | 'Action Required';
  priority: 'High' | 'Medium' | 'Low';
  timestamp: string;
  extractionSummary: {
    intent: string;
    confidence: number;
    entities: Record<string, any>;
  };
}

export interface InventoryItem {
  id: string;
  name: string;
  sku: string;
  quantity: number;
  minThreshold: number;
  category: string;
  lastUpdated: string;
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  intent?: string;
  confidence?: number;
  target?: string;
  details?: string;
}

export type UserRole = 'manager' | 'staff' | 'accountant';

export interface User {
  id: string;
  name: string;
  role: UserRole;
  email: string;
  avatar?: string;
}
