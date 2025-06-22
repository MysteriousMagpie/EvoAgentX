// db.ts
// Requires: npm install better-sqlite3
import Database from 'better-sqlite3';

const DB_PATH = 'evoagentx.db';
const db = new Database(DB_PATH);

// Initialize tables
function initDatabase() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS memory_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      content TEXT
    );
    CREATE TABLE IF NOT EXISTS tasks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      description TEXT,
      status TEXT
    );
    CREATE TABLE IF NOT EXISTS chat_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      sender TEXT,
      message TEXT
    );
    CREATE TABLE IF NOT EXISTS state_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      mood TEXT,
      focus_level INTEGER,
      active_goal TEXT,
      last_input TEXT
    );
  `);
}

// Helper to insert into state_logs
interface StateLog {
  mood?: string;
  focus_level?: number;
  active_goal?: string;
  last_input?: string;
}

function insertStateLog(entry: StateLog) {
  const stmt = db.prepare(`
    INSERT INTO state_logs (mood, focus_level, active_goal, last_input)
    VALUES (@mood, @focus_level, @active_goal, @last_input)
  `);
  stmt.run({
    mood: entry.mood ?? null,
    focus_level: entry.focus_level ?? null,
    active_goal: entry.active_goal ?? null,
    last_input: entry.last_input ?? null,
  });
}

export { db, initDatabase, insertStateLog };
