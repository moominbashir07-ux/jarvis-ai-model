import logging
import time
import math
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from jarvis.config import settings
from jarvis.memory.db_backend import SQLiteBackend

logger = logging.getLogger("JARVIS.Memory")

class VectorStoreAdapter(ABC):
    """Abstract interface defining the contract for future Vector Database implementations (ChromaDB, Pinecone, FAISS)."""

    @abstractmethod
    def connect(self, connection_string: str) -> bool:
        pass

    @abstractmethod
    def upsert_embedding(self, memory_id: str, vector: List[float], metadata: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def query_similar(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete_vector(self, memory_id: str) -> bool:
        pass


class MemoryManager:
    """Production-grade relational and semantic Memory System for JARVIS AI OS.
    
    Decoupled from direct database implementation. Manages dialog logs, profile facts, 
    tasks, and semantic links. Implements recency/importance/frequency contextual ranking.
    """

    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        self.db_path = settings.memory_db_path
        self.db = SQLiteBackend(self.db_path)
        self.session_id = f"session_{int(time.time())}"
        self.vector_store: Optional[VectorStoreAdapter] = None  # Hook for future plug-in vector adapter
        # Maintain conn attribute for duck typing compatibility
        self.conn = None
        logger.debug(f"MemoryManager initialized. Local DB target: {self.db_path}")

    def initialize(self) -> bool:
        """Initializes SQLite connections and validates schema integrity."""
        logger.info("Initializing relational and semantic Memory layers...")
        try:
            success = self.db.connect()
            if not success:
                return False
            
            # Map conn for compatibility
            self.conn = self.db.conn
            self._create_schema()
            
            # Seed default profile parameters if tables are blank
            self._seed_default_profile()
            logger.info("Memory database initialized and checked successfully.")
            return True
        except Exception as e:
            logger.critical(f"Failed to load memory databases: {e}", exc_info=True)
            return False

    def _create_schema(self):
        """Creates tables for sessions, interactions, structured memories, tasks, and links."""
        # 1. Sessions table
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Conversation Interaction logs
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
            )
        """)

        # 3. Memories (User Profile, Preferences, Projects, Goals)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mem_key TEXT UNIQUE NOT NULL,
                mem_value TEXT NOT NULL,
                category TEXT NOT NULL, -- 'profile', 'preference', 'project', 'goal', 'general'
                importance INTEGER DEFAULT 1, -- 1 (low) to 5 (high)
                frequency INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. Memory Relationships (Graph Links)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS memory_relationships (
                source_id INTEGER,
                target_id INTEGER,
                relation_type TEXT NOT NULL, -- 'relates_to', 'blocks', 'part_of'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source_id, target_id),
                FOREIGN KEY(source_id) REFERENCES memories(id) ON DELETE CASCADE,
                FOREIGN KEY(target_id) REFERENCES memories(id) ON DELETE CASCADE
            )
        """)

        # 5. Tasks table
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'pending', -- 'pending', 'in_progress', 'completed'
                due_date TEXT,
                importance INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 6. Automation Audit Log Table
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS automation_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                agent_name TEXT,
                action_name TEXT NOT NULL,
                shell_command TEXT,
                execution_status TEXT NOT NULL, -- 'success', 'failed', 'blocked_security'
                error_message TEXT
            )
        """)

        # 7. Research Caching Table
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS research_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT UNIQUE NOT NULL,
                sources TEXT NOT NULL,
                summary TEXT NOT NULL,
                timestamp REAL NOT NULL,
                provider TEXT NOT NULL,
                confidence_score REAL NOT NULL
            )
        """)

        # 8. Index Optimizations for Context Retrieval Performance (Phase G)
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_memories_category ON memories (category);")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_memories_last_accessed ON memories (last_accessed DESC);")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_interactions_session_timestamp ON interactions (session_id, timestamp);")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_research_cache_query ON research_cache (query);")

        self.db.commit()

    def _seed_default_profile(self):
        """Seeds base user profile templates if table is new."""
        count_row = self.db.execute("SELECT COUNT(*) FROM memories WHERE category='profile'")
        if count_row and count_row[0][0] == 0:
            logger.info("Seeding system memories tables with default templates...")
            defaults = [
                ("user_name", "Sir", "profile", 3),
                ("assistant_name", "JARVIS", "profile", 5),
                ("theme_preference", "dark", "preference", 2),
                ("default_model", "gemini-3.5-flash", "preference", 4)
            ]
            self.db.executemany(
                "INSERT INTO memories (mem_key, mem_value, category, importance) VALUES (?, ?, ?, ?)",
                defaults
            )
            # Insert initial session
            self.db.execute("INSERT OR IGNORE INTO sessions (session_id) VALUES (?)", (self.session_id,))
            self.db.commit()

    def register_vector_store(self, adapter: VectorStoreAdapter):
        """Binds a vector database adapter (ChromaDB / Pinecone / FAISS) for semantic storage."""
        self.vector_store = adapter
        logger.info(f"Registered vector memory engine: {type(adapter).__name__}")

    # --- Interaction logging ---
    def save_interaction(self, role: str, content: str):
        """Logs chat interactions to session databases."""
        try:
            # Ensure session entry exists
            self.db.execute("INSERT OR IGNORE INTO sessions (session_id) VALUES (?)", (self.session_id,))
            self.db.execute(
                "INSERT INTO interactions (session_id, role, content) VALUES (?, ?, ?)",
                (self.session_id, role, content)
            )
            self.db.commit()
            
            # Dynamic Memory parsing (Extracts facts if user states 'remember that...')
            if role == "user":
                self._parse_and_store_facts(content)
        except Exception as e:
            logger.error(f"Failed to log dialog interaction: {e}")

    def get_recent_interactions(self, limit: int = 10) -> List[Dict[str, str]]:
        """Retrieves conversational sliding window logs."""
        try:
            rows = self.db.execute(
                "SELECT role, content FROM interactions ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
        except Exception as e:
            logger.error(f"Error fetching conversation log: {e}")
            return []

    # --- Facts & Memory Management ---
    def _parse_and_store_facts(self, text: str):
        """Analyzes speech patterns to dynamically remember/ignore/update facts."""
        text_lower = text.lower()
        
        # Ignorable conversational filler
        ignore_words = ["hum", "uh", "nevermind", "ignore that", "forget what i said"]
        for word in ignore_words:
            if word in text_lower:
                logger.debug(f"Ignore phrase match detected in text: '{text}'. Skipping database insertion.")
                return

        # Simple pattern rules: "remember that my [key] is [value]"
        if "remember that" in text_lower:
            try:
                parts = text_lower.split("remember that", 1)[1].strip()
                if " is " in parts:
                    key_part, val_part = parts.split(" is ", 1)
                    key = key_part.replace("my", "").strip().replace(" ", "_")
                    value = val_part.strip()
                    category = "preference" if "like" in key or "fav" in key else "general"
                    
                    self.set_memory(key=key, value=value, category=category, importance=3)
                    logger.info(f"Dynamically learned new fact: {key} -> {value}")
            except Exception as e:
                logger.debug(f"Rule fact extractor failed: {e}")

    def set_memory(self, key: str, value: str, category: str, importance: int = 1) -> bool:
        """Saves or updates a structured memory in SQLite."""
        try:
            # Upsert into database
            self.db.execute("""
                INSERT INTO memories (mem_key, mem_value, category, importance, last_accessed)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(mem_key) DO UPDATE SET
                    mem_value = excluded.mem_value,
                    importance = max(memories.importance, excluded.importance),
                    frequency = memories.frequency + 1,
                    last_accessed = CURRENT_TIMESTAMP
            """, (key, value, category, importance))
            self.db.commit()
            
            # Sync with vector store if available
            if self.vector_store:
                pass
            return True
        except Exception as e:
            logger.error(f"Failed to write structured memory: {e}")
            return False

    def delete_memory(self, key: str) -> bool:
        """Removes a structured memory."""
        try:
            self.db.execute("DELETE FROM memories WHERE mem_key = ?", (key,))
            self.db.commit()
            if self.vector_store:
                self.vector_store.delete_vector(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory '{key}': {e}")
            return False

    # --- Memory Relationships (Graph Links) ---
    def link_memories(self, source_key: str, target_key: str, relation_type: str) -> bool:
        """Links two memories together in the semantic graph."""
        try:
            # Fetch numeric IDs
            src_row = self.db.execute("SELECT id FROM memories WHERE mem_key = ?", (source_key,))
            tgt_row = self.db.execute("SELECT id FROM memories WHERE mem_key = ?", (target_key,))

            if src_row and tgt_row:
                self.db.execute("""
                    INSERT OR IGNORE INTO memory_relationships (source_id, target_id, relation_type)
                    VALUES (?, ?, ?)
                """, (src_row[0][0], tgt_row[0][0], relation_type))
                self.db.commit()
                logger.info(f"Graph Link Created: [{source_key}] --({relation_type})--> [{target_key}]")
                return True
            return False
        except Exception as e:
            logger.error(f"Error linking memories: {e}")
            return False

    # --- Tasks Management ---
    def add_task(self, description: str, due_date: Optional[str] = None, importance: int = 1) -> bool:
        """Saves automated execution tasks."""
        try:
            self.db.execute(
                "INSERT INTO tasks (description, due_date, importance) VALUES (?, ?, ?)",
                (description, due_date, importance)
            )
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return False

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Returns unfinished tasks."""
        try:
            rows = self.db.execute("SELECT id, description, status, due_date FROM tasks WHERE status != 'completed'")
            return [{"id": r[0], "description": r[1], "status": r[2], "due_date": r[3]} for r in rows]
        except Exception as e:
            logger.error(f"Error reading tasks: {e}")
            return []

    # --- Retrieval & Ranking Algorithms ---
    def retrieve_contextual_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Hybrid search algorithm querying relational SQLite and ranking results.
        
        Score: S = w_recency * S_recency + w_importance * S_importance + w_frequency * S_frequency
        """
        try:
            # Simple keyword lexical matching for retrieval candidate set
            keywords = [f"%{word}%" for word in query.lower().split() if len(word) > 2]
            
            if not keywords:
                # If no long keywords, retrieve recent memories globally
                rows = self.db.execute("""
                    SELECT id, mem_key, mem_value, category, importance, frequency, last_accessed 
                    FROM memories ORDER BY last_accessed DESC LIMIT 20
                """)
            else:
                # Lexical filter query
                query_clauses = " OR ".join(["(mem_key LIKE ? OR mem_value LIKE ?)" for _ in keywords])
                query_params = []
                for k in keywords:
                    query_params.extend([k, k])
                
                sql = f"""
                    SELECT id, mem_key, mem_value, category, importance, frequency, last_accessed 
                    FROM memories WHERE {query_clauses}
                """
                rows = self.db.execute(sql, tuple(query_params))

            if not rows:
                return []

            ranked_memories = []
            current_time = time.time()

            for row in rows:
                mem_id, key, value, category, importance, frequency, last_accessed = row
                
                # 1. Parse elapsed time to compute recency score
                try:
                    # Convert SQLite timestamp to struct time
                    struct_time = time.strptime(last_accessed, "%Y-%m-%d %H:%M:%S")
                    accessed_epoch = time.mktime(struct_time)
                except ValueError:
                    # Fallback if SQLite format differs
                    accessed_epoch = current_time

                delta_hours = max(0.0, (current_time - accessed_epoch) / 3600.0)
                
                # Recency score decreases logarithmically over time
                s_recency = 1.0 / (1.0 + delta_hours)
                
                # 2. Importance score normalized to 0-1 range
                s_importance = importance / 5.0
                
                # 3. Frequency score scaled logarithmically
                s_frequency = math.log1p(frequency) / math.log1p(100)

                # Composite score calculation
                w_recency, w_importance, w_frequency = 0.4, 0.4, 0.2
                score = (w_recency * s_recency) + (w_importance * s_importance) + (w_frequency * s_frequency)

                ranked_memories.append({
                    "id": mem_id,
                    "key": key,
                    "value": value,
                    "category": category,
                    "score": score
                })

            # Sort memories descending based on composite scores
            ranked_memories.sort(key=lambda x: x["score"], reverse=True)
            top_memories = ranked_memories[:limit]

            # Update accessed logs for retrieved memories asynchronously
            self._increment_access_metrics([m["id"] for m in top_memories])

            return top_memories

        except Exception as e:
            logger.error(f"Memory ranking algorithm failed: {e}", exc_info=True)
            return []

    def _increment_access_metrics(self, ids: List[int]):
        """Increments access count frequency and updates timestamp."""
        if not ids:
            return
        try:
            id_placeholder = ",".join(["?" for _ in ids])
            self.db.execute(f"""
                UPDATE memories 
                SET frequency = frequency + 1, last_accessed = CURRENT_TIMESTAMP
                WHERE id IN ({id_placeholder})
            """, tuple(ids))
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to increment memory metrics: {e}")

    def compile_context_prompt(self, user_query: str, max_chars: int = 1500) -> str:
        """Injects relevant facts, profile parameters, and tasks into prompt context strings.
        
        Guards against context window saturation by dynamically checking character lengths (Phase H).
        """
        # 1. Retrieve ranked memories
        memories = self.retrieve_contextual_memories(user_query, limit=5)
        
        # 2. Retrieve open tasks
        tasks = self.get_pending_tasks()[:3]
        
        # Format profile statements
        context_lines = ["[JARVIS MEMORY CONTEXT]"]
        char_count = len(context_lines[0])
        
        if memories:
            context_lines.append("Relevant Facts:")
            char_count += len("Relevant Facts:\n")
            for m in memories:
                line = f" - {m['key'].replace('_', ' ')}: {m['value']} (Confidence: {m['score']:.2f})"
                if char_count + len(line) + 1 > max_chars:
                    break
                context_lines.append(line)
                char_count += len(line) + 1
                
        if tasks:
            tasks_header = "\nActive Pending Tasks:"
            if char_count + len(tasks_header) + 1 <= max_chars:
                context_lines.append("Active Pending Tasks:")
                char_count += len(tasks_header) + 1
                for t in tasks:
                    line = f" - [Task #{t['id']}] {t['description']} (Due: {t['due_date'] or 'N/A'})"
                    if char_count + len(line) + 1 > max_chars:
                        break
                    context_lines.append(line)
                    char_count += len(line) + 1
                
        context_lines.append("[END CONTEXT]")
        return "\n".join(context_lines)

    # --- Decoupled Event Receivers (Phase J) ---
    def _on_automation_finished(self, event_type: str, payload: dict):
        """EventBus callback that receives automation audit events to log them to SQLite."""
        action_name = payload.get("action", "")
        status = payload.get("status", "")
        details = payload.get("details", "")

        # Update last automation memory keys
        self.set_memory(
            key=f"last_automation_{action_name}",
            value=f"Status: {status} | Details: {details}",
            category="general",
            importance=1
        )

        # Log details to SQLite audit tables
        try:
            self.db.execute("""
                INSERT INTO automation_logs (action_name, execution_status, error_message)
                VALUES (?, ?, ?)
            """, (action_name, status, details if status != "success" else None))
            self.db.commit()
            logger.debug(f"EventBus callback logged automation audit: '{action_name}' status: {status}")
        except Exception as e:
            logger.error(f"Failed to record event-driven automation log: {e}")

    def cleanup(self):
        """Closes SQLite database connection backend channels."""
        if self.db:
            try:
                self.db.close()
                logger.debug("Local memory database channel closed.")
            except Exception as e:
                logger.error(f"Error closing SQLite database: {e}")
