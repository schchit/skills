const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('../memory-v2/memory-v2.5.db');

// Check memory_decisions table structure
db.all("PRAGMA table_info(memory_decisions)", (err, rows) => {
  if (err) {
    console.error('Error:', err);
  } else {
    console.log('memory_decisions columns:');
    rows.forEach(r => console.log('- ' + r.name + ' (' + r.type + ')'));
  }
  db.close();
});
