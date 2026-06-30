import asyncio
import datetime
import http
import json
import logging
import secrets
import threading
from urllib.parse import urlparse, parse_qs
import websockets
from jarvis.config import settings

logger = logging.getLogger("JARVIS.Core.IPC")

class IPCServer:
    """Production-grade WebSocket server for bidirectional local communication between Python and Electron.
    
    Provides cryptographic token verification, thread-safe event broadcasting, and 
    command relaying to the central Orchestrator.
    """

    def __init__(self, port: int = 8765, event_bus=None, orchestrator=None):
        self.port = port
        self.orchestrator = orchestrator
        self.event_bus = event_bus
        self.auth_token = secrets.token_hex(16)
        self.clients = set()
        
        self.loop = None
        self.server = None
        self.thread = None
        self.heartbeat_task = None
        self.is_running = False

        self._write_token_file()
        logger.info(f"IPCServer initialized. Auth Token generated: {self.auth_token}")
        
        if self.event_bus:
            self.event_bus.subscribe("*", self._on_event_bus_event)

    def _write_token_file(self):
        try:
            token_file = settings.root_dir / ".ipc_token"
            with open(token_file, "w", encoding="utf-8") as f:
                f.write(self.auth_token)
            logger.debug(f"Saved auth token to {token_file}")
        except Exception as e:
            logger.error(f"Failed to write auth token file: {e}")

    def start(self):
        """Starts the WebSocket server in a background daemon thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(
            target=self._run_server_loop,
            daemon=True,
            name="JARVIS-IPC-Server"
        )
        self.thread.start()
        logger.info(f"IPC WebSocket Server starting in background thread on ws://127.0.0.1:{self.port}...")

    def _run_server_loop(self):
        """Prepares asyncio loop and runs the socket server."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self._async_start_server())
            self.loop.run_forever()
        except Exception as e:
            logger.critical(f"IPC WebSocket Server loop encountered critical error: {e}", exc_info=True)
        finally:
            logger.debug("IPC WebSocket Server background thread finished.")

    async def _async_start_server(self):
        self.server = await websockets.serve(
            self._client_handler,
            "127.0.0.1",
            self.port,
            process_request=self._process_request
        )
        logger.info("IPC WebSocket Server successfully bound and listening.")
        # Start the background heartbeat loop
        if self.loop:
            self.heartbeat_task = self.loop.create_task(self._heartbeat_loop())

    async def _process_request(self, connection, request):
        """Validates auth token from connection path parameters before upgrading the connection."""
        try:
            parsed_url = urlparse(request.path)
            query_params = parse_qs(parsed_url.query)
            client_token = query_params.get("token", [""])[0]

            if not secrets.compare_digest(client_token, self.auth_token):
                logger.warning(f"Rejected connection attempt from {connection.remote_address} - Invalid token.")
                return connection.respond(http.HTTPStatus.FORBIDDEN, "Unauthorized: Token mismatch.\n")
        except Exception as e:
            logger.error(f"Error checking handshake: {e}")
            return connection.respond(http.HTTPStatus.BAD_REQUEST, "Invalid handshake.\n")
        return None

    async def _client_handler(self, websocket):
        """Handles post-handshake registered client input stream loops."""
        # Register Client
        self.clients.add(websocket)
        logger.info(f"Electron client connected successfully from {websocket.remote_address}")

        # Broadcast initial registration success following Phase D protocol
        await websocket.send(json.dumps({
            "version": "1.0",
            "event": "SystemReady",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "payload": {"message": "Authenticated handshake complete."}
        }))

        # Publish DebugPing to EventBus to verify end-to-end event routing
        self.broadcast_event("DebugPing", {"status": "success", "message": "IPC pipeline verified"})

        # Connection consumer loop
        try:
            async for message in websocket:
                await self._process_incoming_message(message, websocket)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Electron client disconnected: {websocket.remote_address}")
        except Exception as e:
            logger.error(f"Error processing client stream: {e}", exc_info=True)
        finally:
            self.clients.remove(websocket)

    async def _process_incoming_message(self, message_str: str, websocket):
        """Parses and acts on command payloads sent by the Electron GUI client."""
        logger.debug(f"Received raw message from client: '{message_str}'")
        try:
            data = json.loads(message_str)
            action = data.get("action")
            payload = data.get("payload", {})

            if action == "Heartbeat":
                # Respond immediately with HeartbeatAck event
                await websocket.send(json.dumps({
                    "version": "1.0",
                    "event": "HeartbeatAck",
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "payload": {"status": "alive"}
                }))
                return
            elif action == "HeartbeatAck":
                logger.debug("Received HeartbeatAck response from client.")
                return

            if action == "TriggerCommand":
                command_text = payload.get("command", "")
                logger.info(f"IPC Command Trigger: '{command_text}'")
                
                # Relay to Orchestrator in a safe callback
                if self.orchestrator:
                    # Run orchestrator input processing in a separate thread to avoid blocking socket loop
                    threading.Thread(
                        target=self.orchestrator.process_input,
                        args=(command_text, "ui"),
                        daemon=True
                    ).start()
            
            elif action == "ToggleWakeState":
                target_state = payload.get("state", "Sleeping")
                logger.info(f"IPC Wake Toggle state requested: '{target_state}'")
                if self.orchestrator:
                    if target_state == "Listening":
                        # If manual UI activation occurred, trigger the wake/listen process
                        threading.Thread(
                            target=self.orchestrator._handle_wake_word_trigger,
                            daemon=True
                        ).start()
                    elif self.orchestrator.listener:
                        self.orchestrator.listener.state = "sleeping"
            
            else:
                logger.warning(f"Unknown incoming action from client: {action}")
                
        except json.JSONDecodeError:
            logger.error("Failed to parse incoming IPC frame. Expected JSON format.")
        except Exception as e:
            logger.error(f"Error handling IPC action request: {e}", exc_info=True)

    def _on_event_bus_event(self, event_type: str, payload: dict):
        """Wildcard EventBus subscriber callback. Runs in publishing thread."""
        # Wrap the event payload in the versioned message protocol format
        message = {
            "version": "1.0",
            "event": event_type,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "payload": payload
        }
        self.broadcast_message(message)

    def broadcast_event(self, event_type: str, payload: dict = None):
        """Thread-safe method to publish events. Decoupled using the EventBus."""
        if self.event_bus:
            self.event_bus.publish(event_type, payload or {})
        else:
            # Direct backup formatting if no EventBus is active
            message = {
                "version": "1.0",
                "event": event_type,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "payload": payload or {}
            }
            self.broadcast_message(message)

    def broadcast_message(self, message: dict):
        """Thread-safe method to dispatch raw message dictionary to all active clients."""
        if not self.is_running or not self.loop or not self.loop.is_running():
            return

        message_str = json.dumps(message)
        # Run coroutine thread-safely inside the server's event loop
        asyncio.run_coroutine_threadsafe(
            self._async_broadcast(message_str),
            self.loop
        )

    async def _heartbeat_loop(self):
        """Periodically sends heartbeats to connected clients and checks for dead connections."""
        logger.debug("Heartbeat ping loop started.")
        while self.is_running:
            try:
                await asyncio.sleep(5.0)
                if self.clients:
                    # Publish Heartbeat event to the EventBus, which broadcasts it to clients
                    if self.event_bus:
                        self.event_bus.publish("Heartbeat", {"status": "ok"})
                    else:
                        self.broadcast_event("Heartbeat", {"status": "ok"})
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in IPC Heartbeat loop: {e}")

    async def _async_broadcast(self, message_str: str):
        """Asynchronous broadcast executor loop."""
        if not self.clients:
            return
        
        # Gather send futures across all active client sockets
        await asyncio.gather(
            *[client.send(message_str) for client in self.clients],
            return_exceptions=True
        )
        logger.debug(f"Broadcasted IPC frame to {len(self.clients)} clients.")

    async def _async_stop(self):
        """Asynchronous helper to stop the server."""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        try:
            if self.server:
                self.server.close()
                await self.server.wait_closed()
        except Exception as e:
            logger.error(f"Error during async server close: {e}")

    def stop(self):
        """Gracefully shuts down the socket server and joins execution threads."""
        if not self.is_running:
            return
        
        logger.info("Stopping IPC WebSocket Server...")
        self.is_running = False

        # Delete token file on stop
        try:
            token_file = settings.root_dir / ".ipc_token"
            if token_file.exists():
                token_file.unlink()
                logger.debug("Deleted auth token file.")
        except Exception as e:
            logger.error(f"Failed to delete auth token file: {e}")

        if self.server and self.loop and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self._async_stop(), self.loop)
            try:
                future.result(timeout=2.0)
            except Exception as e:
                logger.error(f"Error waiting for server shutdown in event loop: {e}", exc_info=True)
            
            # Stop the loop after the async close has finished and been signaled
            try:
                self.loop.call_soon_threadsafe(self.loop.stop)
            except Exception as e:
                logger.error(f"Error scheduling loop stop: {e}")
            
        if self.thread:
            self.thread.join(timeout=2.0)

        if self.loop:
            try:
                self.loop.close()
                logger.debug("IPC WebSocket Server event loop closed.")
            except Exception as e:
                logger.error(f"Error closing event loop: {e}")
            
        logger.info("IPC WebSocket Server stopped.")
