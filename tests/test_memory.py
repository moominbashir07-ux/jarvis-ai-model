import time
import logging
from jarvis.core.logger import setup_logger
from jarvis.memory.memory_manager import MemoryManager

# Setup basic logging to console
setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestMemory")

def test_memory_lifecycle():
    logger.info("--- Starting Memory Lifecycle Verification ---")
    memory = MemoryManager()
    
    # Force use of a temporary database to avoid dirtying developer logs
    memory.db_path = "jarvis_test_memory.db"
    
    initialized = memory.initialize()
    logger.info(f"Memory DB initialized: {initialized}")
    if not initialized:
        return False

    # 1. Test fact seeding and upserts
    logger.info("Writing memories to SQLite...")
    memory.set_memory(key="user_hobby", value="flying iron suits", category="profile", importance=4)
    memory.set_memory(key="fav_os", value="Windows 11", category="preference", importance=2)
    
    # 2. Test rule-based fact learning from dialogue
    logger.info("Testing dynamic conversation fact parser...")
    memory.save_interaction(role="user", content="remember that my codename is Iron Man")
    
    # Verify it saved key "codename"
    codename_val = ""
    cursor = memory.conn.cursor()
    cursor.execute("SELECT mem_value FROM memories WHERE mem_key='codename'")
    row = cursor.fetchone()
    if row:
        codename_val = row[0]
    logger.info(f"Dynamically parsed codename: '{codename_val}' (Expected: 'iron man')")

    # 3. Test memory linking (Graph Relationships)
    logger.info("Linking memory nodes in semantic graph...")
    memory.link_memories(source_key="user_name", target_key="codename", relation_type="alias_of")
    
    # 4. Test tasks queue
    logger.info("Adding automated system tasks...")
    memory.add_task(description="Clean up Windows desktop screenshot logs", due_date="2026-06-25", importance=3)
    
    # 5. Test ranking algorithms and context prompt construction
    logger.info("Simulating context search lookup for user query...")
    # Retrieve top match for hobby
    results = memory.retrieve_contextual_memories("Iron Man hobby", limit=3)
    logger.info(f"Context matches retrieved: {len(results)}")
    for r in results:
        logger.info(f" - Match: [{r['key']}]={r['value']} (Rank Score: {r['score']:.4f})")
        
    # Compile prompt
    prompt = memory.compile_context_prompt("Iron Man hobby")
    logger.info("Compiled System context prompt:")
    print(f"\n{prompt}\n")
    
    memory.cleanup()
    logger.info("Memory System Verification Complete.\n")
    return True

if __name__ == "__main__":
    logger.info("==========================================")
    logger.info("  JARVIS Memory Engine Integration Tests  ")
    logger.info("==========================================")
    
    test_memory_lifecycle()
