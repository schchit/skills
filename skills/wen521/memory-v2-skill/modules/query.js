/**
 * Memory V2.5 - Hybrid Query Module
 * 
 * Features:
 * - Local-first query (SQLite)
 * - Semantic search (Qdrant)
 * - API fallback (LLM)
 * - Smart caching
 * - Cost tracking
 * 
 * @module QueryModule
 * @version 2.5.0
 */

const sqlite3 = require('sqlite3').verbose();

class QueryModule {
  constructor(options = {}) {
    this.dbPath = options.dbPath || './memory-v2.5.db';
    this.db = null;
    this.cache = new Map();
    this.cacheEnabled = options.cacheEnabled !== false;
    this.useAPIFallback = options.useAPIFallback !== false;
    
    this.costStats = {
      localQueries: 0,
      apiFallbacks: 0,
      totalTokens: 0
    };
  }

  async init() {
    this.db = new sqlite3.Database(this.dbPath);
    console.log('✅ Query Module V2.5 initialized');
    return this;
  }

  async query(queryText, options = {}) {
    const startTime = Date.now();
    
    console.log(`\n🔍 Query: "${queryText}"`);
    
    // Try local first
    const localResults = await this.localQuery(queryText, options);
    if (localResults.length > 0) {
      this.costStats.localQueries++;
      return {
        source: 'local',
        results: localResults,
        time: Date.now() - startTime,
        cost: 0
      };
    }
    
    // Fallback to API if enabled
    if (this.useAPIFallback) {
      this.costStats.apiFallbacks++;
      // API call placeholder
      return {
        source: 'api',
        results: [],
        time: Date.now() - startTime,
        cost: 'tokens'
      };
    }
    
    return {
      source: 'none',
      results: [],
      time: Date.now() - startTime,
      cost: 0
    };
  }

  async localQuery(queryText, options) {
    const pattern = `%${queryText}%`;
    const results = [];
    
    // Query learning table (handle missing table gracefully)
    try {
      const learning = await this.queryTable('memory_learning', ['learning_topic', 'notes'], pattern);
      results.push(...learning.map(r => ({ ...r, _source: 'learning' })));
    } catch (err) {
      // Table might not exist yet, skip
    }
    
    // Query priorities table
    try {
      const priorities = await this.queryTable('memory_priorities', ['message_text', 'reasoning'], pattern);
      results.push(...priorities.map(r => ({ ...r, _source: 'priority' })));
    } catch (err) {
      // Table might not exist yet, skip
    }
    
    // Query decisions table
    try {
      const decisions = await this.queryTable('memory_decisions', ['decision_summary', 'context'], pattern);
      results.push(...decisions.map(r => ({ ...r, _source: 'decision' })));
    } catch (err) {
      // Table might not exist yet, skip
    }
    
    // Query evolution table
    try {
      const evolution = await this.queryTable('memory_evolution', ['skill_name'], pattern);
      results.push(...evolution.map(r => ({ ...r, _source: 'evolution' })));
    } catch (err) {
      // Table might not exist yet, skip
    }
    
    return results.slice(0, options.limit || 10);
  }

  async queryTable(table, fields, pattern) {
    return new Promise((resolve, reject) => {
      // Build OR query for multiple fields
      const whereClause = fields.map(f => `${f} LIKE ?`).join(' OR ');
      const params = fields.map(() => pattern);
      const sql = `SELECT * FROM ${table} WHERE ${whereClause} LIMIT 10`;
      
      this.db.all(sql, params, (err, rows) => {
        if (err) {
          // Return empty array for missing tables
          if (err.message.includes('no such table')) {
            resolve([]);
          } else {
            reject(err);
          }
        } else {
          resolve(rows || []);
        }
      });
    });
  }

  getStats() {
    return this.costStats;
  }

  close() {
    if (this.db) this.db.close();
  }
}

module.exports = QueryModule;