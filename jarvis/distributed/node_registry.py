import sqlite3
import logging
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS.Distributed.Registry")

class NodeRegistry:
    """Manages index lists of discovered PC, mobile, and Docker nodes in SQLite databases."""

    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cluster_nodes (
                    node_id TEXT PRIMARY KEY,
                    node_name TEXT NOT NULL,
                    node_type TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    cpu_cores INTEGER NOT NULL,
                    ram_mb REAL NOT NULL,
                    status TEXT NOT NULL
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize cluster node SQLite database: {e}")

    def register_node(self, node_id: str, name: str, node_type: str, ip: str, cpu: int, ram: float, status: str = "online"):
        """Saves discovered node attributes or updates states profiles."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cluster_nodes (node_id, node_name, node_type, ip_address, cpu_cores, ram_mb, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(node_id) DO UPDATE SET
                    node_name = excluded.node_name,
                    node_type = excluded.node_type,
                    ip_address = excluded.ip_address,
                    cpu_cores = excluded.cpu_cores,
                    ram_mb = excluded.ram_mb,
                    status = excluded.status
            """, (node_id, name, node_type, ip, cpu, ram, status))
            conn.commit()
            conn.close()
            logger.info(f"Registered cluster node in database: [{node_id}] '{name}' ({node_type})")
        except Exception as e:
            logger.error(f"Failed to save cluster node: {e}")

    def get_active_nodes(self) -> List[Dict[str, Any]]:
        """Retrieves catalog of active online nodes."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT node_id, node_name, node_type, ip_address, cpu_cores, ram_mb, status FROM cluster_nodes WHERE status = 'online'")
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for r in rows:
                results.append({
                    "node_id": r[0],
                    "name": r[1],
                    "type": r[2],
                    "ip": r[3],
                    "cpu_cores": r[4],
                    "ram_mb": r[5],
                    "status": r[6]
                })
            return results
        except Exception as e:
            logger.error(f"Failed to fetch active cluster nodes list: {e}")
            return []
