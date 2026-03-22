/**
 * Smart Memory Lite
 * Lightweight cognitive memory for AI agents
 */

const fs = require('fs');
const path = require('path');

class SmartMemory {
  constructor(options = {}) {
    this.userId = options.userId || 'default';
    this.storagePath = options.storagePath || './memories';
    this.autoSave = options.autoSave !== false;
    this.maxMemories = options.maxMemories || 1000;
    this.contextLimit = options.contextLimit || 5;
    this.minRelevance = options.minRelevance || 0.6;
    
    // Initialize storage
    this.userPath = path.join(this.storagePath, this.userId);
    this.conversationsPath = path.join(this.userPath, 'conversations');
    this.memoriesFile = path.join(this.userPath, 'memories.json');
    
    this.ensureDirs();
    this.loadMemories();
  }
  
  /**
   * Ensure directories exist
   */
  ensureDirs() {
    if (!fs.existsSync(this.userPath)) {
      fs.mkdirSync(this.userPath, { recursive: true });
    }
    if (!fs.existsSync(this.conversationsPath)) {
      fs.mkdirSync(this.conversationsPath, { recursive: true });
    }
  }
  
  /**
   * Load memories from file
   */
  loadMemories() {
    if (fs.existsSync(this.memoriesFile)) {
      const data = fs.readFileSync(this.memoriesFile, 'utf8');
      this.memories = JSON.parse(data);
    } else {
      this.memories = [];
    }
  }
  
  /**
   * Save memories to file
   */
  saveMemories() {
    fs.writeFileSync(
      this.memoriesFile,
      JSON.stringify(this.memories, null, 2),
      'utf8'
    );
  }
  
  /**
   * Save a conversation message
   */
  async save(message) {
    const memory = {
      id: `mem-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      role: message.role,
      content: message.content,
      timestamp: message.timestamp || new Date().toISOString(),
      tags: message.tags || [],
      topic: message.topic || null
    };
    
    // Add to memories
    this.memories.push(memory);
    
    // Limit max memories
    if (this.memories.length > this.maxMemories) {
      this.memories = this.memories.slice(-this.maxMemories);
    }
    
    // Auto-save to file
    if (this.autoSave) {
      this.saveMemories();
      
      // Also save to daily conversation file
      const date = new Date().toISOString().split('T')[0];
      const conversationFile = path.join(this.conversationsPath, `${date}.json`);
      
      let conversations = [];
      if (fs.existsSync(conversationFile)) {
        conversations = JSON.parse(fs.readFileSync(conversationFile, 'utf8'));
      }
      
      conversations.push(memory);
      fs.writeFileSync(conversationFile, JSON.stringify(conversations, null, 2), 'utf8');
    }
    
    return memory;
  }
  
  /**
   * Recall memories by query (simple keyword matching)
   */
  async recall(query, options = {}) {
    const limit = options.limit || this.contextLimit;
    const minRelevance = options.minRelevance || this.minRelevance;
    
    const queryLower = query.toLowerCase();
    const queryWords = queryLower.split(' ').filter(w => w.length > 2);
    
    // Score memories by keyword match
    const scored = this.memories.map(memory => {
      const contentLower = memory.content.toLowerCase();
      let score = 0;
      
      for (const word of queryWords) {
        if (contentLower.includes(word)) {
          score++;
        }
      }
      
      // Boost recent memories
      const daysOld = (Date.now() - new Date(memory.timestamp).getTime()) / (1000 * 60 * 60 * 24);
      const recencyBoost = Math.max(0, 1 - (daysOld / 30)); // Boost decreases over 30 days
      
      const finalScore = (score / queryWords.length) * 0.7 + recencyBoost * 0.3;
      
      return {
        ...memory,
        relevance: finalScore
      };
    });
    
    // Filter by min relevance and sort
    const results = scored
      .filter(m => m.relevance >= minRelevance)
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, limit);
    
    return results;
  }
  
  /**
   * Recall memories by tag
   */
  async recallByTag(tag) {
    return this.memories.filter(m => m.tags && m.tags.includes(tag));
  }
  
  /**
   * Recall memories by time range
   */
  async recallByTime(options = {}) {
    const days = options.days || 7;
    const topic = options.topic || null;
    
    const cutoff = Date.now() - (days * 24 * 60 * 60 * 1000);
    
    let results = this.memories.filter(m => {
      return new Date(m.timestamp).getTime() >= cutoff;
    });
    
    if (topic) {
      results = results.filter(m => m.topic === topic);
    }
    
    return results;
  }
  
  /**
   * Get session summary
   */
  async getSessionSummary() {
    const topics = {};
    
    for (const memory of this.memories) {
      if (memory.topic) {
        topics[memory.topic] = (topics[memory.topic] || 0) + 1;
      }
    }
    
    const lastActive = this.memories.length > 0
      ? this.memories[this.memories.length - 1].timestamp
      : null;
    
    return {
      totalConversations: this.memories.length,
      topics: Object.keys(topics),
      topicCounts: topics,
      lastActive,
      storagePath: this.userPath
    };
  }
  
  /**
   * Export all memories
   */
  async export() {
    return {
      userId: this.userId,
      exportedAt: new Date().toISOString(),
      memories: this.memories
    };
  }
  
  /**
   * Export to file
   */
  async exportToFile(filePath) {
    const data = await this.export();
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
  }
  
  /**
   * Import memories
   */
  async import(data) {
    if (data.memories && Array.isArray(data.memories)) {
      this.memories = [...this.memories, ...data.memories];
      this.saveMemories();
    }
  }
  
  /**
   * Import from file
   */
  async importFromFile(filePath) {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    await this.import(data);
  }
  
  /**
   * Clear all memories
   */
  async clear() {
    this.memories = [];
    this.saveMemories();
  }
}

module.exports = { SmartMemory };
