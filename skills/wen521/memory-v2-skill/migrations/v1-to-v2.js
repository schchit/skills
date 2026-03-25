#!/usr/bin/env node
/**
 * Memory V1 to V2 Migration Script
 * Migrates data from old memory format to V2 schema
 */

const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');

class MemoryMigration {
    constructor(sourceDbPath, targetDbPath = './memory-v2.db') {
        this.sourceDbPath = sourceDbPath;
        this.targetDbPath = targetDbPath;
        this.sourceDb = null;
        this.targetDb = null;
    }

    async init() {
        // Check if source exists
        if (!fs.existsSync(this.sourceDbPath)) {
            throw new Error(`Source database not found: ${this.sourceDbPath}`);
        }

        // Open source database
        this.sourceDb = new sqlite3.Database(this.sourceDbPath, sqlite3.OPEN_READONLY);
        
        // Open/create target database
        this.targetDb = new sqlite3.Database(this.targetDbPath);
        
        console.log('✅ Connected to source and target databases');
    }

    async runSchema() {
        const schemaPath = path.join(__dirname, '..', 'database', 'schema.sql');
        
        if (!fs.existsSync(schemaPath)) {
            throw new Error(`Schema file not found: ${schemaPath}`);
        }

        const schema = fs.readFileSync(schemaPath, 'utf8');
        const statements = schema
            .split(';')
            .map(s => s.trim())
            .filter(s => s.length > 0);

        for (const statement of statements) {
            await this.runTarget(statement);
        }
        
        console.log('✅ Target database schema initialized');
    }

    async migratePriorities() {
        console.log('🔄 Migrating priorities...');
        
        try {
            const rows = await this.allSource(
                "SELECT * FROM memory_priorities WHERE created_at >= datetime('now', '-90 days')"
            );

            for (const row of rows) {
                await this.runTarget(
                    `INSERT INTO memory_priorities 
                     (msg_id, conv_id, priority_level, reasoning, category, created_at)
                     VALUES (?, ?, ?, ?, ?, ?)`,
                    [row.msg_id, row.conv_id, row.priority_level, row.reasoning, row.category, row.created_at]
                );
            }

            console.log(`✅ Migrated ${rows.length} priority records`);
        } catch (err) {
            console.log('ℹ️ No priorities to migrate or table does not exist');
        }
    }

    async migrateLearning() {
        console.log('🔄 Migrating learning records...');
        
        try {
            const rows = await this.allSource(
                "SELECT * FROM memory_learning WHERE status != 'abandoned'"
            );

            for (const row of rows) {
                await this.runTarget(
                    `INSERT INTO memory_learning 
                     (msg_id, conv_id, topic, description, status, progress, started_at, updated_at, completed_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                    [row.msg_id, row.conv_id, row.topic, row.description, row.status, 
                     row.progress, row.started_at, row.updated_at, row.completed_at]
                );
            }

            console.log(`✅ Migrated ${rows.length} learning records`);
        } catch (err) {
            console.log('ℹ️ No learning records to migrate or table does not exist');
        }
    }

    async migrateDecisions() {
        console.log('🔄 Migrating decisions...');
        
        try {
            const rows = await this.allSource(
                "SELECT * FROM memory_decisions WHERE status IN ('pending', 'implemented')"
            );

            for (const row of rows) {
                await this.runTarget(
                    `INSERT INTO memory_decisions 
                     (msg_id, conv_id, summary, context, expected_outcome, actual_outcome, 
                      status, review_scheduled_at, reviewed_at, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                    [row.msg_id, row.conv_id, row.summary, row.context, row.expected_outcome,
                     row.actual_outcome, row.status, row.review_scheduled_at, row.reviewed_at, row.created_at]
                );
            }

            console.log(`✅ Migrated ${rows.length} decision records`);
        } catch (err) {
            console.log('ℹ️ No decisions to migrate or table does not exist');
        }
    }

    async migrateEvolution() {
        console.log('🔄 Migrating skill evolution...');
        
        try {
            const rows = await this.allSource(
                "SELECT * FROM memory_evolution WHERE usage_count > 0"
            );

            for (const row of rows) {
                await this.runTarget(
                    `INSERT INTO memory_evolution 
                     (skill_name, category, usage_count, success_count, last_used_at, first_used_at)
                     VALUES (?, ?, ?, ?, ?, ?)`,
                    [row.skill_name, row.category, row.usage_count, row.success_count, 
                     row.last_used_at, row.first_used_at]
                );
            }

            console.log(`✅ Migrated ${rows.length} skill evolution records`);
        } catch (err) {
            console.log('ℹ️ No evolution records to migrate or table does not exist');
        }
    }

    async runTarget(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.targetDb.run(sql, params, function(err) {
                if (err) reject(err);
                else resolve({ id: this.lastID, changes: this.changes });
            });
        });
    }

    async allSource(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.sourceDb.all(sql, params, (err, rows) => {
                if (err) reject(err);
                else resolve(rows);
            });
        });
    }

    async close() {
        if (this.sourceDb) {
            await new Promise((resolve) => this.sourceDb.close(resolve));
        }
        if (this.targetDb) {
            await new Promise((resolve) => this.targetDb.close(resolve));
        }
        console.log('✅ Database connections closed');
    }

    async migrate() {
        try {
            await this.init();
            await this.runSchema();
            await this.migratePriorities();
            await this.migrateLearning();
            await this.migrateDecisions();
            await this.migrateEvolution();
            
            console.log('\n🎉 Migration completed successfully!');
            console.log(`📁 New database: ${path.resolve(this.targetDbPath)}`);
        } catch (err) {
            console.error('\n❌ Migration failed:', err.message);
            process.exit(1);
        } finally {
            await this.close();
        }
    }
}

// CLI usage
if (require.main === module) {
    const sourceDb = process.argv[2];
    const targetDb = process.argv[3] || './memory-v2.db';

    if (!sourceDb) {
        console.log('Usage: node migrations/v1-to-v2.js <source-v1.db> [target-v2.db]');
        console.log('Example: node migrations/v1-to-v2.js ./memory-v1.db ./memory-v2.db');
        process.exit(1);
    }

    const migration = new MemoryMigration(sourceDb, targetDb);
    migration.migrate();
}

module.exports = MemoryMigration;
