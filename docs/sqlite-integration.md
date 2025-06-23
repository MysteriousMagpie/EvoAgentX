# SQLite Integration for EvoAgentX

## What This Is
This integration provides a simple TypeScript module (`db.ts`) for initializing and interacting with a local SQLite database using the `better-sqlite3` package. It is designed to store logs and state for EvoAgentX agents, with the following tables:

- `memory_logs`: Stores memory log entries.
- `tasks`: Stores task descriptions and statuses.
- `chat_history`: Stores chat messages and sender info.
- `state_logs`: Stores agent state snapshots (mood, focus, goal, last input, etc).

A helper function is provided to insert new entries into `state_logs` with optional fields.

## What Has Been Done
- `db.ts` module created with table initialization and insert helper.
- `testInsert.ts` script demonstrates inserting a sample state log and prints the absolute path to the database file.
- TypeScript and ESM compatibility configured (see `tsconfig.json`).
- `better-sqlite3` and `@types/better-sqlite3` installed for type safety and SQLite access.
- Confirmed that the insert function works and writes to the correct database file.

## What Still Needs To Be Done
- **Expand Table Schemas:** Add more fields to tables as needed for your application.
- **Add More Helpers:** Create helper functions for reading, updating, and deleting records.
- **Error Handling:** Add robust error handling and logging to the database functions.
- **Testing:** Write automated tests for all database helpers.
- **Integrate with Main App:** Use these helpers in your main agent logic.
- **Documentation:** Add usage examples and API docs for each helper function.
- **(Optional) Migrations:** Consider using a migration tool or scripts for future schema changes.

## Usage Example
```ts
import { initDatabase, insertStateLog } from './db.js';

initDatabase();
insertStateLog({
  mood: 'lethargic',
  focus_level: 2,
  active_goal: 'procrastinate productively',
  last_input: 'thinking about sandwiches',
});
```

## Troubleshooting
- If you do not see your data, check the absolute path to the database file printed by `testInsert.ts` and ensure you are opening the same file in SQLite.
- Make sure to run `npm install` to get all dependencies.
- For ESM/TypeScript compatibility, see the `tsconfig.json` settings (`allowImportingTsExtensions`).

---
**Last updated:** June 23, 2025
