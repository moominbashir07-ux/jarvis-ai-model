import sqlite3
import threading
import logging
from abc import ABC, abstractmethod
from typing import List, Tuple, Any

logger = logging.getLogger("JARVIS.Memory.DB")

class DatabaseBackend(ABC):
    """Abstract interface defining the contract for JARVIS database backends."""

    @abstractmethod
    def connect(self) -> bool:
        """Establishes the connection channel to the database."""
        pass

    @abstractmethod
    def execute(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Executes a single SQL query and returns rows."""
        pass

    @abstractmethod
    def executemany(self, query: str, params_list: List[Tuple] = ()) -> int:
        """Executes bulk SQL queries and returns row count."""
        pass

    @abstractmethod
    def commit(self):
        """Commits the active transaction."""
        pass

    @abstractmethod
    def close(self):
        """Closes connection handles."""
        pass


class SQLiteBackend(DatabaseBackend):
    """Production-grade SQLite database backend.
    
    Implements WAL (Write-Ahead Logging) journal mode for multi-threaded read/write
    concurrency, optimized synchronization parameters, and transaction-safe write serialization.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self._write_lock = threading.Lock()
        logger.debug(f"SQLiteBackend initialized for target: {db_path}")

    def connect(self) -> bool:
        try:
            # check_same_thread=False allows sharing connection across threads with write locks
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            
            # Concurrency & optimization pragmas
            self.conn.execute("PRAGMA foreign_keys = ON;")
            self.conn.execute("PRAGMA journal_mode = WAL;")
            self.conn.execute("PRAGMA synchronous = NORMAL;")
            
            logger.info("SQLite connection established with WAL journal mode.")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}", exc_info=True)
            return False

    def execute(self, query: str, params: Tuple = ()) -> List[Tuple]:
        # Read operations are concurrent, but we serialize everything to avoid lock errors
        with self._write_lock:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def executemany(self, query: str, params_list: List[Tuple] = ()) -> int:
        with self._write_lock:
            cursor = self.conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount

    def commit(self):
        with self._write_lock:
            if self.conn:
                self.conn.commit()

    def close(self):
        with self._write_lock:
            if self.conn:
                try:
                    self.conn.close()
                    logger.info("SQLite connection closed.")
                except Exception as e:
                    logger.error(f"Error closing SQLite database: {e}")


class PostgreSQLBackend(DatabaseBackend):
    """Production-grade PostgreSQL backend template.
    
    Facilitates zero-code-change migration to an enterprise-scale relational database
    by implementing the identical DatabaseBackend interface contract.
    """

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn = None
        logger.debug("PostgreSQLBackend initialized.")

    def connect(self) -> bool:
        logger.info("PostgreSQL migration endpoint active. Ready for connection pool injection.")
        # import psycopg2
        # self.conn = psycopg2.connect(self.dsn)
        return True

    def execute(self, query: str, params: Tuple = ()) -> List[Tuple]:
        # cursor = self.conn.cursor()
        # cursor.execute(query, params)
        # return cursor.fetchall()
        logger.warning("Execute called on stub PostgreSQLBackend.")
        return []

    def executemany(self, query: str, params_list: List[Tuple] = ()) -> int:
        # cursor = self.conn.cursor()
        # cursor.executemany(query, params_list)
        # return cursor.rowcount
        logger.warning("Executemany called on stub PostgreSQLBackend.")
        return 0

    def commit(self):
        # if self.conn:
        #     self.conn.commit()
        pass

    def close(self):
        # if self.conn:
        #     self.conn.close()
        pass
