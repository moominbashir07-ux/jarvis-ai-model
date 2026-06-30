# DATABASE_SCHEMA.md - SQLite Schema Specification

This document details the personalization tables, fields, indexes, and schemas saved inside `jarvis_memory.db`.

---

## 🗄️ Database Table Definitions

### 1. `user_profile`
Persists long-term key-value user configurations (such as model preferences, IDE choices).
* `key` (TEXT PRIMARY KEY)
* `value` (TEXT NOT NULL) - JSON formatted string.
* `updated_at` (REAL NOT NULL)

### 2. `preferences`
Stores scoring multipliers per suggestion category.
* `category` (TEXT PRIMARY KEY)
* `multiplier` (REAL NOT NULL)
* `updated_at` (REAL NOT NULL)

### 3. `habits`
Logs application transition frequency counters.
* `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
* `habit_name` (TEXT UNIQUE NOT NULL)
* `count` (INTEGER NOT NULL)
* `last_observed` (REAL NOT NULL)

### 4. `routines`
Holds identified sequence templates.
* `name` (TEXT PRIMARY KEY)
* `sequence_json` (TEXT NOT NULL)
* `confidence` (REAL NOT NULL)
* `created_at` (REAL NOT NULL)

### 5. `predictions`
Persists predicted likelihood percentages.
* `action` (TEXT PRIMARY KEY)
* `probability` (REAL NOT NULL)
* `updated_at` (REAL NOT NULL)

### 6. `recommendations`
Stores generated context-aware suggestions.
* `id` (TEXT PRIMARY KEY)
* `category` (TEXT NOT NULL)
* `title` (TEXT NOT NULL)
* `confidence` (REAL NOT NULL)
* `payload_json` (TEXT NOT NULL)

### 7. `workspace_memory`
Preserves layout state parameters across reboots.
* `key` (TEXT PRIMARY KEY) - Project folder path.
* `state_json` (TEXT NOT NULL)
* `updated_at` (REAL NOT NULL)

---

## ⚡ Index Definitions
* `idx_habits_name` ON `habits (habit_name)`
* `idx_feedback_sug` ON `feedback_history (suggestion_id)`
* `idx_learning_ts` ON `learning_events (timestamp)`
