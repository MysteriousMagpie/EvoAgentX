import path from 'path';
import { fileURLToPath } from 'url';
import { initDatabase, insertStateLog } from '../db.ts';

// Initialize the database and tables
initDatabase();

// Insert a test state_log entry
insertStateLog({
  mood: 'lethargic',
  focus_level: 2,
  active_goal: 'procrastinate productively',
  last_input: 'thinking about sandwiches',
});

console.log('Inserted test state_log entry.');

// Print the absolute path to the DB file
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
console.log('DB absolute path:', path.resolve(__dirname, 'evoagentx.db'));
