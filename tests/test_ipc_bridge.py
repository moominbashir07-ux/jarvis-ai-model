import asyncio
import json
import logging
import time
import unittest
import websockets
from jarvis.core.logger import setup_logger
from jarvis.core.ipc_server import IPCServer

# Setup console logger for test
setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestIPC")

class MockListener:
    def __init__(self):
        self.activity_triggered = False
        
    def trigger_activity(self):
        self.activity_triggered = True

class MockOrchestrator:
    def __init__(self):
        self.inputs = []
        self.listener = MockListener()

    def process_input(self, text: str, source: str) -> str:
        logger.info(f"[MockOrchestrator] Input: '{text}' | Source: '{source}'")
        self.inputs.append((text, source))
        return f"Mock reply to: {text}"


class TestIPCBridge(unittest.TestCase):
    
    def setUp(self):
        self.test_port = 9876
        self.orchestrator = MockOrchestrator()
        self.server = IPCServer(port=self.test_port, orchestrator=self.orchestrator)
        self.server.start()
        # Brief sleep to ensure socket binds
        time.sleep(0.5)

    def tearDown(self):
        self.server.stop()
        time.sleep(0.5)

    def test_unauthorized_connection_fails(self):
        async def run_test():
            uri = f"ws://127.0.0.1:{self.test_port}?token=bad_token"
            try:
                async with websockets.connect(uri) as _:
                    self.fail("Connection succeeded with an invalid token.")
            except websockets.exceptions.InvalidStatus as e:
                # Should close connection during handshake with status code 400+
                logger.info(f"Handshake correctly rejected invalid token. StatusCode: {e.response.status_code}")
                self.assertEqual(e.response.status_code, 403)
            except Exception as e:
                logger.info(f"Connection correctly failed: {e}")

        asyncio.run(run_test())

    def test_authorized_connection_success(self):
        async def run_test():
            token = self.server.auth_token
            uri = f"ws://127.0.0.1:{self.test_port}?token={token}"
            
            async with websockets.connect(uri) as websocket:
                # 1. Check SystemReady event sent by server on open
                resp = await websocket.recv()
                msg = json.loads(resp)
                logger.info(f"Client received welcome frame: {msg}")
                self.assertEqual(msg["event"], "SystemReady")

                # 2. Test event broadcast from Python server to Electron client
                self.server.broadcast_event("ThinkingStarted", {"task": "test"})
                
                # Scan incoming frames to skip asynchronous DebugPing / Heartbeat frames
                msg2 = {}
                for _ in range(5):
                    resp2 = await websocket.recv()
                    msg2 = json.loads(resp2)
                    logger.info(f"Client received broadcast event: {msg2}")
                    if msg2.get("event") == "ThinkingStarted":
                        break
                self.assertEqual(msg2.get("event"), "ThinkingStarted")
                self.assertEqual(msg2.get("payload", {}).get("task"), "test")

                # 3. Test sending command from Electron client to Python server
                cmd_payload = {
                    "action": "TriggerCommand",
                    "payload": {
                        "command": "run mock calculation"
                    }
                }
                await websocket.send(json.dumps(cmd_payload))
                
                # Brief sleep to let process thread consume the queue
                await asyncio.sleep(0.2)
                
                # Verify mock orchestrator received command
                self.assertEqual(len(self.orchestrator.inputs), 1)
                self.assertEqual(self.orchestrator.inputs[0][0], "run mock calculation")
                self.assertEqual(self.orchestrator.inputs[0][1], "ui")

        asyncio.run(run_test())


if __name__ == "__main__":
    logger.info("==========================================")
    logger.info("  JARVIS IPC WebSocket Connection Tests   ")
    logger.info("==========================================")
    
    unittest.main()
