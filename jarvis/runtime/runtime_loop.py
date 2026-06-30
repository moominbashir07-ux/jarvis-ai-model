import logging
from typing import Dict, Any
from jarvis.runtime.runtime import UnifiedRuntime

logger = logging.getLogger("JARVIS.Runtime.Loop")

class RuntimeMasterLoop:
    """Orchestrates the E2E unified master execution cycle (input -> plan -> execute -> reflect -> respond)."""

    def __init__(self, runtime: UnifiedRuntime):
        self.runtime = runtime

    def execute_single_cycle(self, input_bytes: bytes) -> Dict[str, Any]:
        """Runs one iteration of the primary execution loop."""
        logger.info("Executing master runtime iteration loop...")
        
        transcription = self.runtime.conversation.process_voice_input(input_bytes)
        
        context = self.runtime.context.extract_unified_context()
        
        route = self.runtime.router.route_request(transcription, complexity="LOW")
        
        workflow_payload = {"task_name": transcription, "context": context, "route": route}
        exec_res = self.runtime.execution.execute_workflow(workflow_payload)
        
        tts_audio = self.runtime.conversation.generate_voice_response(exec_res["reflection"])
        
        logger.info("Master iteration loop cycle finished successfully.")
        return {
            "transcription": transcription,
            "verification_status": exec_res["verification_status"],
            "reflection": exec_res["reflection"],
            "tts_audio_bytes_length": len(tts_audio)
        }
