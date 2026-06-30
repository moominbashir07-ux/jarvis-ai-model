import React, { useState, useEffect, useRef } from 'react';
import { AICore } from './components/AICore';
import { Waveform } from './components/Waveform';
import { HackingBackground } from './components/HackingBackground';
import { motion } from 'framer-motion';
import { 
  Volume2, 
  VolumeX, 
  Shield, 
  Moon, 
  Eye, 
  EyeOff, 
  Activity, 
  Cpu, 
  HardDrive, 
  Wifi, 
  Sparkles, 
  Terminal, 
  BookOpen, 
  Search,
  CheckSquare
} from 'lucide-react';

type JarvisState = 'Sleeping' | 'Listening' | 'Thinking' | 'Speaking' | 'Processing';

interface MemoryItem {
  id: string;
  content: string;
}

interface ThoughtLogItem {
  timestamp: string;
  message: string;
}

interface DialogItem {
  id: string;
  role: 'user' | 'jarvis';
  content: string;
}

interface TaskItem {
  id: string;
  name: string;
  status: 'Running' | 'Completed' | 'Failed' | 'Idle';
}

interface ResearchItem {
  id: string;
  query: string;
  finding: string;
}

const App: React.FC = () => {
  const [state, setState] = useState<JarvisState>('Sleeping');
  const [chatLog, setChatLog] = useState<string>('Standby mode. Awaiting wake keyword or manual activation...');
  const [promptInput, setPromptInput] = useState<string>('');

  useEffect(() => {
    (window as any).setJarvisState = setState;
    (window as any).setJarvisChatLog = setChatLog;
  }, []);
  
  // Settings toggles
  const [voiceFeedback, setVoiceFeedback] = useState<boolean>(true);
  const [autoSleep, setAutoSleep] = useState<boolean>(true);
  const [vfxEnabled, setVfxEnabled] = useState<boolean>(true);

  // Dynamic system metrics simulation
  const [cpuLoad, setCpuLoad] = useState<number>(24);
  const [ramLoad, setRamLoad] = useState<number>(56);
  const [diskLoad, setDiskLoad] = useState<number>(42);
  const [netStatus, setNetStatus] = useState<'CONNECTED' | 'DISCONNECTED'>('CONNECTED');

  // AI Providers Health Status
  const [providerHealths, setProviderHealths] = useState<Record<string, string>>({
    ollama: 'ONLINE',
    openai: 'ONLINE',
    gemini: 'ONLINE',
    vision: 'ONLINE',
    memory: 'ONLINE',
    automation: 'ONLINE',
  });

  // Diagnostics Self-Test report
  const [diagnostics, setDiagnostics] = useState<{
    overall: string;
    details: Record<string, string>;
  }>({
    overall: 'PASS',
    details: {
      microphone: 'PASS',
      speaker: 'PASS',
      tts: 'PASS',
      stt: 'PASS',
      ipc: 'PASS',
      event_bus: 'PASS',
      ai_providers: 'PASS',
      automation: 'PASS',
    }
  });

  // Active Memories list
  const [memories] = useState<MemoryItem[]>([
    { id: 'm1', content: 'Target user identity: Tony Stark / Chief Architect' },
    { id: 'm2', content: 'Host OS: Windows 11 (64-bit Directives)' },
    { id: 'm3', content: 'Ollama local models routed via Llama3' },
    { id: 'm4', content: 'Primary Web routing: Gemini-1.5-Pro / OpenAI API' },
  ]);

  // Progressive Thought log
  const [thoughtLogs, setThoughtLogs] = useState<ThoughtLogItem[]>([
    { timestamp: '23:13:47', message: 'System self-diagnostic check completed: Status PASS' },
    { timestamp: '23:13:48', message: 'WebSocket IPC interface connected successfully on Port 8765' },
    { timestamp: '23:13:48', message: 'Wake-word monitor active. Standing by, Tony.' }
  ]);

  // Dialog bubble context log
  const [contextLogs, setContextLogs] = useState<DialogItem[]>([
    { id: 'c1', role: 'jarvis', content: 'Systems stabilized. Core temperature normal. Ready for command input.' }
  ]);

  // Background running tasks
  const [runningTasks, setRunningTasks] = useState<TaskItem[]>([
    { id: 't1', name: 'Continuous Wake Listen', status: 'Running' },
    { id: 't2', name: 'Memory Vector DB Indexing', status: 'Idle' },
    { id: 't3', name: 'Background Self Diagnostics', status: 'Running' }
  ]);

  // Researcher web queries / findings
  const [researchFindings] = useState<ResearchItem[]>([
    { id: 'r1', query: 'Diagnostics check', finding: 'PyAudio buffers and SAPI5 TTS bindings initialized.' }
  ]);

  // Terminal debug overrides log
  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    '[SYSTEM] J.A.R.V.I.S. Core boot complete.',
    '[SYSTEM] Listening on wake word: "JARVIS" / "HEY JARVIS"',
    '[IPC] WS Server authentication handshake accepted.'
  ]);

  // Active reasoning stats
  const [cognitiveStatus, setCognitiveStatus] = useState<{
    model: string;
    provider: string;
    latency: string;
  }>({
    model: 'Gemini 1.5 Pro',
    provider: 'Gemini',
    latency: '0.00s'
  });

  const thoughtEndRef = useRef<HTMLDivElement>(null);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  // Auto-sleep idle timeout handler
  useEffect(() => {
    if (state === 'Sleeping' && autoSleep) {
      const timer = setTimeout(() => {
        if (window.electronAPI) {
          window.electronAPI.sendState('Sleeping');
        }
      }, 15000); // 15s idle auto sleep overlay hide
      return () => clearTimeout(timer);
    }
  }, [state, autoSleep]);

  // Simulate hardware fluctuation logs
  useEffect(() => {
    const interval = setInterval(() => {
      setCpuLoad(Math.floor(15 + Math.random() * 22));
      setRamLoad((prev) => {
        const offset = Math.floor(Math.random() * 3) - 1;
        const target = prev + offset;
        return target > 80 ? 80 : target < 40 ? 40 : target;
      });
      setDiskLoad((prev) => {
        if (Math.random() < 0.05) {
          const offset = Math.floor(Math.random() * 3) - 1;
          return prev + offset;
        }
        return prev;
      });
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  // Format timestamp helper
  const getFormattedTime = () => {
    const now = new Date();
    return now.toTimeString().split(' ')[0];
  };

  // Push log helper
  const addThought = (msg: string) => {
    setThoughtLogs((prev) => [...prev.slice(-15), { timestamp: getFormattedTime(), message: msg }]);
  };

  const addTerminalLog = (msg: string) => {
    setTerminalLogs((prev) => [...prev.slice(-30), `[${getFormattedTime()}] ${msg}`]);
  };

  // Bind Electron IPC handlers
  useEffect(() => {
    if (window.electronAPI) {
      // General Event Subscriber
      window.electronAPI.onIpcEvent((_event: any, packet: { event: string; payload: any }) => {
        const { event, payload } = packet;
        console.log('IPC general event packet:', event, payload);
        
        // Log to terminal
        addTerminalLog(`Event Received: ${event} -> ${JSON.stringify(payload || {})}`);

        switch (event) {
          case 'SelfTestReport':
            if (payload) {
              setDiagnostics({
                overall: payload.overall || 'PASS',
                details: payload.details || {}
              });
              addThought(`Diagnostics run complete: overall status [${payload.overall}]`);
            }
            break;
            
          case 'AIRouteSelected':
            if (payload) {
              setCognitiveStatus({
                model: payload.model || 'Unknown',
                provider: payload.provider || 'Unknown',
                latency: `${payload.latency_sec?.toFixed(2) || '0.00'}s`
              });
              addThought(`Router selecting provider [${payload.provider}] for task: ${payload.task_type || 'generic'}`);
            }
            break;

          case 'SpeakingStarted':
            setState('Speaking');
            addThought('Synthesizing speech response...');
            if (payload && payload.response) {
              setChatLog(payload.response);
              setContextLogs((prev) => [
                ...prev.slice(-4),
                { id: Date.now().toString(), role: 'jarvis', content: payload.response }
              ]);
            }
            break;

          case 'SpeakingStopped':
            setState('Sleeping');
            addThought('Speech output completed. Returning to standby.');
            break;

          case 'ThinkingStarted':
            setState('Thinking');
            addThought('Evaluating cognitive pipeline logic paths...');
            break;

          case 'ThinkingStopped':
            addThought('Cognitive evaluation processed.');
            break;

          case 'ListeningStarted':
            setState('Listening');
            setChatLog('Listening, sir...');
            addThought('Microphone active. Awaiting voice stream input.');
            break;

          case 'ListeningStopped':
            setState('Thinking');
            if (payload && payload.query) {
              addThought(`Speech-to-Text matched query: "${payload.query}"`);
              setContextLogs((prev) => [
                ...prev.slice(-4),
                { id: Date.now().toString(), role: 'user', content: payload.query }
              ]);
            }
            break;

          case 'WakeDetected':
            setState('Listening');
            addThought('Acoustic wake keyword detected. Prompt initiated.');
            break;

          case 'AutomationStarted':
            setState('Processing');
            addThought(`Automation task launched: ${payload.action} -> ${payload.target}`);
            setRunningTasks((prev) => [
              ...prev,
              { id: Date.now().toString(), name: `${payload.action}: ${payload.target}`, status: 'Running' }
            ]);
            break;

          case 'AutomationFinished':
            addThought(`Automation task complete. Status: ${payload.success ? 'SUCCESS' : 'FAILED'}`);
            setRunningTasks((prev) =>
              prev.map((t) =>
                t.status === 'Running'
                  ? { ...t, status: payload.success ? 'Completed' : 'Failed' }
                  : t
              )
            );
            break;

          case 'SystemReady':
            setState('Sleeping');
            addThought('All services initialized. System active.');
            break;

          case 'Heartbeat':
            // Verify link status
            setNetStatus('CONNECTED');
            break;

          case 'TokenChunk':
            if (payload && payload.chunk) {
              setChatLog((prev) => {
                // If previous log is a placeholder status, overwrite it
                if (
                  prev.startsWith('Thinking') || 
                  prev.startsWith('Listening') || 
                  prev.startsWith('Standby') || 
                  prev.startsWith('Awaiting') ||
                  prev.startsWith('Executing')
                ) {
                  return payload.chunk;
                }
                return prev + payload.chunk;
              });
            }
            break;

          case 'ResponseComplete':
            if (payload && payload.response) {
              setChatLog(payload.response);
            }
            break;
            
          default:
            break;
        }
      });

      // Status updates
      window.electronAPI.onCoreStatusUpdate((_event: any, data: any) => {
        console.log('Status update event:', data);
        if (data && data.payload) {
          const { provider, new_status } = data.payload;
          if (provider && new_status) {
            setProviderHealths((prev) => ({
              ...prev,
              [provider.toLowerCase()]: new_status
            }));
            addThought(`Provider [${provider}] status transitioned to ${new_status}`);
          }
        }
      });
    }
  }, []);

  // Autoscroll panels
  useEffect(() => {
    thoughtEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [thoughtLogs]);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [terminalLogs]);

  const handleStateChange = (newState: JarvisState) => {
    setState(newState);
    if (window.electronAPI) {
      window.electronAPI.sendState(newState);
    }
    
    switch (newState) {
      case 'Sleeping':
        setChatLog('Standby mode. Awaiting wake keyword or manual activation...');
        addThought('Standing by.');
        break;
      case 'Listening':
        setChatLog('Awaiting command...');
        addThought('Manual prompt request. Voice capture active.');
        break;
      case 'Thinking':
        setChatLog('Analyzing neural net decision routes...');
        break;
      case 'Speaking':
        setChatLog('Synthesizing speech response...');
        break;
      case 'Processing':
        setChatLog('Executing automated system routines...');
        break;
    }
  };

  const handleCoreClick = () => {
    if (state === 'Sleeping') {
      handleStateChange('Listening');
    } else {
      handleStateChange('Sleeping');
    }
  };

  const handlePromptSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!promptInput.trim()) return;
    
    const query = promptInput;
    setPromptInput('');
    handleCommandSubmit(query);
  };

  const handleCommandSubmit = (text: string) => {
    // Add user interaction to logs
    setContextLogs((prev) => [
      ...prev.slice(-4),
      { id: Date.now().toString(), role: 'user', content: text }
    ]);
    addThought(`Routing input override: "${text}"`);
    addTerminalLog(`User command: "${text}"`);

    if (window.electronAPI && window.electronAPI.triggerCommand) {
      setChatLog(`Routing command: "${text}"`);
      window.electronAPI.triggerCommand(text);
    } else {
      // Mock execution if outside Electron
      setChatLog(`Executing local: "${text}"`);
      handleStateChange('Thinking');
      setTimeout(() => {
        handleStateChange('Processing');
        setTimeout(() => {
          handleStateChange('Speaking');
          setChatLog('Command executed successfully via web developer fallback environment.');
          setContextLogs((prev) => [
            ...prev.slice(-4),
            { id: Date.now().toString(), role: 'jarvis', content: 'Command executed successfully via web developer fallback environment.' }
          ]);
          setTimeout(() => {
            handleStateChange('Sleeping');
          }, 3000);
        }, 1500);
      }, 1500);
    }
  };

  const getDiagnosticsColor = (val: string) => {
    if (val === 'PASS') return 'text-emerald-400';
    if (val === 'WARNING') return 'text-amber-400 animate-pulse';
    return 'text-rose-400 animate-pulse';
  };

  const getHealthBadgeClass = (val: string) => {
    if (val === 'ONLINE' || val === 'PASS') return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/35';
    if (val === 'DEGRADED' || val === 'WARNING') return 'bg-amber-500/20 text-amber-400 border-amber-500/35 animate-pulse';
    return 'bg-rose-500/20 text-rose-400 border-rose-500/35 animate-pulse';
  };

  const getTaskStatusClass = (status: string) => {
    switch (status) {
      case 'Running':
        return 'text-jarvis-blue border-jarvis-blue/30 bg-jarvis-blue/10 animate-pulse';
      case 'Completed':
        return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
      case 'Failed':
        return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
      default:
        return 'text-white/40 border-white/10 bg-white/5';
    }
  };

  return (
    <div className="w-screen h-screen flex flex-col justify-between bg-transparent select-none overflow-hidden font-inter text-white p-4 relative">
      {/* 3D Hacking Canvas Background */}
      {vfxEnabled && <HackingBackground />}

      {/* TOP STATUS BAR */}
      <div className="w-full h-11 flex items-center justify-between border border-jarvis-blue/15 px-5 font-orbitron text-[10px] text-jarvis-blue/80 bg-jarvis-dark/85 backdrop-blur-md rounded-lg shadow-lg no-drag">
        {/* Left Ticker Status */}
        <div className="flex items-center gap-3">
          <Shield className="w-4.5 h-4.5 text-jarvis-blue animate-pulse" />
          <span className="font-extrabold tracking-widest text-glow-blue uppercase">JARVIS AI OS v2.5</span>
          <span className="text-white/20">|</span>
          <div className="flex items-center gap-1.5 overflow-hidden w-64 h-4 relative">
            <motion.div
              animate={{ x: ['100%', '-100%'] }}
              transition={{ repeat: Infinity, duration: 15, ease: 'linear' }}
              className="absolute whitespace-nowrap text-[9px] tracking-wider text-white/50"
            >
              [SECURITY: SECURE] [IPC BRIDGE: PORT 8765] [SQLITE: WAL ACTIVE] [SELF_TEST: ALL {diagnostics.overall}]
            </motion.div>
          </div>
        </div>

        {/* Center Date & Time */}
        <div className="text-center font-bold tracking-[0.18em] text-[11px] text-glow-blue">
          {new Date().toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' }).toUpperCase()} // {getFormattedTime()}
        </div>

        {/* Right Settings & Mode Selectors */}
        <div className="flex items-center gap-4">
          {/* Diagnostic Ticker Overall */}
          <div className="flex items-center gap-1">
            <span>DIAGNOSTICS:</span>
            <span className={`font-black ${getDiagnosticsColor(diagnostics.overall)}`}>{diagnostics.overall}</span>
          </div>

          <span className="text-white/20">|</span>

          {/* voice setting toggle */}
          <button 
            onClick={() => setVoiceFeedback(!voiceFeedback)} 
            className="hover:text-jarvis-blue transition-colors flex items-center gap-1 cursor-pointer"
            title="Toggle Voice Feedback"
          >
            {voiceFeedback ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5 text-rose-400" />}
            <span className="hidden md:inline">{voiceFeedback ? "VOICE: ON" : "VOICE: OFF"}</span>
          </button>

          {/* auto sleep setting toggle */}
          <button 
            onClick={() => setAutoSleep(!autoSleep)} 
            className="hover:text-jarvis-blue transition-colors flex items-center gap-1 cursor-pointer"
            title="Toggle Auto-sleep Mode"
          >
            <Moon className="w-3.5 h-3.5 text-jarvis-blue" />
            <span className="hidden md:inline">{autoSleep ? "SLEEP: ON" : "SLEEP: OFF"}</span>
          </button>

          {/* Matrix backdrop toggler */}
          <button 
            onClick={() => setVfxEnabled(!vfxEnabled)} 
            className="hover:text-jarvis-blue transition-colors flex items-center gap-1 cursor-pointer"
            title="Toggle VFX canvas matrix backdrops"
          >
            {vfxEnabled ? <Eye className="w-3.5 h-3.5 text-jarvis-blue" /> : <EyeOff className="w-3.5 h-3.5 text-rose-400" />}
            <span className="hidden md:inline">{vfxEnabled ? "VFX: ON" : "VFX: OFF"}</span>
          </button>
        </div>
      </div>

      {/* MAIN CONTAINER LAYOUT */}
      <div className="flex-1 flex gap-4 my-3 h-[calc(100%-11.5rem)] min-h-[300px]">
        
        {/* LEFT COLUMN: MEMORY, COGNITIVE, CONTEXT LOGS */}
        <div className="w-[310px] flex flex-col gap-3 h-full no-drag">
          
          {/* Panel 1: Memory & Cognitive Metrics */}
          <div className="flex-[1.2] p-4 glass-panel rounded-lg flex flex-col justify-between border border-jarvis-blue/10 overflow-hidden relative">
            <div className="absolute top-0 right-0 p-1 font-mono text-[6px] text-white/10 uppercase">COGNITIVE_GRID</div>
            <h3 className="font-orbitron font-extrabold text-[10px] text-jarvis-blue tracking-wider border-b border-jarvis-blue/15 pb-1 flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5" /> MEMORY & COGNITION
            </h3>
            
            {/* Active memories preview */}
            <div className="flex-1 overflow-y-auto my-2 text-[9px] font-mono flex flex-col gap-1.5 pr-1">
              <div className="text-white/40 text-[8px] uppercase tracking-widest flex justify-between">
                <span>Memory Database</span>
                <span>Active Link</span>
              </div>
              {memories.map((mem) => (
                <div key={mem.id} className="p-1.5 rounded bg-black/30 border border-white/5 text-white/80 hover:border-jarvis-blue/20 transition-colors flex gap-1 items-start">
                  <span className="text-jarvis-blue select-none">›</span>
                  <span className="line-clamp-2 leading-relaxed">{mem.content}</span>
                </div>
              ))}
            </div>

            {/* Cognitive parameters */}
            <div className="border-t border-jarvis-blue/15 pt-2 flex justify-between items-center text-[9px] font-orbitron">
              <div className="flex flex-col">
                <span className="text-white/40 text-[8px]">ACTIVE PROVIDER / ROUTER</span>
                <span className="text-jarvis-blue font-bold flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-jarvis-blue animate-pulse" /> {cognitiveStatus.model}
                </span>
              </div>
              <div className="text-right">
                <span className="text-white/40 text-[8px]">LATENCY</span>
                <div className="text-glow-blue font-black text-jarvis-blue">{cognitiveStatus.latency}</div>
              </div>
            </div>
          </div>

          {/* Panel 2: Thought logs & Context transcripts */}
          <div className="flex-[2] p-4 glass-panel rounded-lg flex flex-col justify-between border border-jarvis-blue/10 overflow-hidden">
            <h3 className="font-orbitron font-extrabold text-[10px] text-jarvis-blue tracking-wider border-b border-jarvis-blue/15 pb-1 flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5" /> THOUGHT & CONTEXT STREAM
            </h3>

            {/* Step-by-step thinking processes */}
            <div className="flex-1 overflow-y-auto my-2 font-mono text-[9px] text-white/70 flex flex-col gap-1.5 pr-1 border-b border-white/5 pb-2">
              <div className="text-white/40 text-[8px] uppercase tracking-widest mb-0.5">PROGRESSIVE THOUGHT LOGS</div>
              {thoughtLogs.map((log, index) => (
                <div key={index} className="flex gap-1.5 leading-relaxed items-start">
                  <span className="text-jarvis-blue font-bold">[{log.timestamp}]</span>
                  <span className="text-white/80 flex-1">{log.message}</span>
                </div>
              ))}
              <div ref={thoughtEndRef} />
            </div>

            {/* Context dialogue logs */}
            <div className="h-28 overflow-y-auto flex flex-col gap-1.5 pr-1">
              <div className="text-white/40 text-[8px] uppercase tracking-widest mb-0.5">DIALOGUE CONTEXT</div>
              {contextLogs.length === 0 ? (
                <span className="text-white/30 text-[9px] font-mono">No active dialog history.</span>
              ) : (
                contextLogs.map((chat) => (
                  <div key={chat.id} className={`p-1.5 rounded font-mono text-[9px] leading-relaxed ${
                    chat.role === 'user' 
                      ? 'bg-jarvis-blue/5 border border-jarvis-blue/10 text-right ml-4' 
                      : 'bg-black/35 border border-white/5 mr-4'
                  }`}>
                    <div className="text-[7px] text-white/30 uppercase mb-0.5 font-orbitron tracking-widest">
                      {chat.role === 'user' ? 'USER' : 'JARVIS AI'}
                    </div>
                    <div>{chat.content}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* CENTER INTERACTIVE CORE COLUMN */}
        <div className="flex-1 flex flex-col justify-between items-center relative">
          
          {/* Top Diagnostics Self Test overlay indicators */}
          <div className="w-[400px] p-2 glass-panel rounded border border-jarvis-blue/10 text-[8px] font-mono flex flex-col gap-1 no-drag shadow-md z-10">
            <div className="flex justify-between items-center text-white/50 border-b border-white/5 pb-1">
              <span className="font-orbitron font-extrabold tracking-widest text-[8px] text-jarvis-blue">HARDWARE DIAGNOSTIC REPORT</span>
              <span className="flex items-center gap-1"><Wifi className="w-2.5 h-2.5" /> SYSTEM OK</span>
            </div>
            <div className="grid grid-cols-4 gap-1.5 mt-0.5">
              {Object.entries(diagnostics.details).map(([key, val]) => (
                <div key={key} className="flex flex-col border border-white/5 bg-black/25 rounded p-1 text-center font-semibold">
                  <span className="text-white/30 uppercase text-[7px] select-none truncate">{key}</span>
                  <span className={getDiagnosticsColor(val)}>{val}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Central Holographic Orb Core with Siri Waveforms */}
          <div className="flex-1 flex flex-col items-center justify-center relative">
            {/* Holographic glowing lines backdrop */}
            <div className="absolute w-[360px] h-[360px] rounded-full border border-jarvis-blue/5 animate-spin-slow pointer-events-none" />
            <div className="absolute w-[340px] h-[340px] rounded-full border border-dashed border-jarvis-blue/10 animate-spin-reverse-slow pointer-events-none" />
            
            {/* Ring Target Grid Crosshair */}
            <div className="absolute w-[400px] h-[400px] pointer-events-none flex items-center justify-center opacity-30">
              <div className="absolute w-full h-[1px] bg-gradient-to-r from-transparent via-jarvis-blue to-transparent" />
              <div className="absolute h-full w-[1px] bg-gradient-to-b from-transparent via-jarvis-blue to-transparent" />
            </div>

            {/* Clickable AI Core Toggle */}
            <div 
              onClick={handleCoreClick} 
              className="cursor-pointer hover:scale-105 active:scale-95 transition-all duration-300 z-10 no-drag"
              title="Click to toggle Standby/Active listening modes"
            >
              <AICore state={state} />
            </div>

            {/* Core Label Identity */}
            <div className="text-center mt-3 z-10 no-drag pointer-events-none select-none">
              <h2 className="font-orbitron font-black tracking-[0.25em] text-[18px] text-jarvis-blue text-glow-blue uppercase">J.A.R.V.I.S.</h2>
              <div className="font-orbitron text-[9px] text-white/40 tracking-widest mt-1 uppercase flex items-center justify-center gap-1.5">
                <span>SYSTEM STATE // </span>
                <span className="text-jarvis-blue font-bold text-glow-blue">{state}</span>
              </div>
            </div>

            {/* Voice Modulator Waveform */}
            <div className="mt-4 z-10">
              <Waveform state={state} />
            </div>
          </div>

          {/* Central Dialog Bubble Ticker */}
          <div className="w-[85%] max-w-[620px] mb-2 p-3 glass-panel rounded-lg border border-jarvis-blue/20 text-center font-mono text-[11px] leading-relaxed text-jarvis-blue min-h-[48px] flex items-center justify-center shadow-lg relative no-drag">
            <div className="absolute -top-1.5 left-4 px-1.5 bg-jarvis-dark border border-jarvis-blue/20 text-[7px] font-orbitron uppercase text-white/50 tracking-wider">
              AI Speech Modulator Output
            </div>
            {chatLog}
          </div>
        </div>

        {/* RIGHT COLUMN: HARDWARE STATUS, PROVIDERS, WEB RESEARCH */}
        <div className="w-[310px] flex flex-col gap-3 h-full no-drag">
          
          {/* Panel 1: Provider Status Dashboard & Metrics */}
          <div className="flex-[1.8] p-4 glass-panel rounded-lg flex flex-col justify-between border border-jarvis-blue/10 overflow-hidden">
            <h3 className="font-orbitron font-extrabold text-[10px] text-jarvis-blue tracking-wider border-b border-jarvis-blue/15 pb-1 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5" /> SYSTEM PROVIDERS & STATUS
            </h3>

            {/* Provider Grid Health Checks */}
            <div className="my-2 grid grid-cols-2 gap-2">
              {Object.entries(providerHealths).map(([name, status]) => (
                <div key={name} className={`flex items-center justify-between px-2.5 py-1.5 rounded border font-mono text-[9px] uppercase bg-black/25 ${getHealthBadgeClass(status)}`}>
                  <span>{name}</span>
                  <div className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
                    <span className="text-[8px] font-bold">{status}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Simulated Live Hardware Monitor Bars */}
            <div className="border-t border-jarvis-blue/10 pt-3 flex flex-col gap-2">
              <div className="text-white/40 font-orbitron text-[8px] uppercase tracking-widest">LIVE HARDWARE UTILIZATION</div>
              
              {/* CPU */}
              <div className="flex flex-col gap-0.5 text-[9px] font-mono">
                <div className="flex justify-between text-white/70">
                  <span className="flex items-center gap-1"><Cpu className="w-3 h-3 text-jarvis-blue" /> CPU LOADING</span>
                  <span>{cpuLoad}%</span>
                </div>
                <div className="w-full h-1.5 bg-white/5 border border-white/10 rounded overflow-hidden">
                  <motion.div 
                    animate={{ width: `${cpuLoad}%` }} 
                    transition={{ duration: 1 }}
                    className="h-full bg-gradient-to-r from-jarvis-blue/50 to-jarvis-blue" 
                  />
                </div>
              </div>

              {/* MEM */}
              <div className="flex flex-col gap-0.5 text-[9px] font-mono">
                <div className="flex justify-between text-white/70">
                  <span className="flex items-center gap-1"><HardDrive className="w-3 h-3 text-jarvis-blue" /> RAM USAGE</span>
                  <span>{ramLoad}%</span>
                </div>
                <div className="w-full h-1.5 bg-white/5 border border-white/10 rounded overflow-hidden">
                  <motion.div 
                    animate={{ width: `${ramLoad}%` }} 
                    transition={{ duration: 1 }}
                    className="h-full bg-gradient-to-r from-jarvis-blue/50 to-jarvis-blue" 
                  />
                </div>
              </div>

              {/* STORAGE */}
              <div className="flex flex-col gap-0.5 text-[9px] font-mono">
                <div className="flex justify-between text-white/70">
                  <span className="flex items-center gap-1"><HardDrive className="w-3 h-3 text-jarvis-blue" /> DISK STORAGE</span>
                  <span>{diskLoad}%</span>
                </div>
                <div className="w-full h-1.5 bg-white/5 border border-white/10 rounded overflow-hidden">
                  <motion.div 
                    animate={{ width: `${diskLoad}%` }} 
                    className="h-full bg-gradient-to-r from-jarvis-blue/50 to-jarvis-blue" 
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Panel 2: Agent manager console & Researcher log */}
          <div className="flex-[1.2] p-4 glass-panel rounded-lg flex flex-col justify-between border border-jarvis-blue/10 overflow-hidden">
            <h3 className="font-orbitron font-extrabold text-[10px] text-jarvis-blue tracking-wider border-b border-jarvis-blue/15 pb-1 flex items-center gap-1.5">
              <Terminal className="w-3.5 h-3.5" /> AGENT MANAGER CONSOLE
            </h3>

            {/* Task Checklist progress */}
            <div className="flex-1 overflow-y-auto my-2 text-[9px] font-mono flex flex-col gap-1.5 pr-1 border-b border-white/5 pb-2">
              <div className="text-white/40 text-[8px] uppercase tracking-widest flex justify-between">
                <span>Active Subprocess</span>
                <span>Integrity</span>
              </div>
              {runningTasks.map((task) => (
                <div key={task.id} className="flex justify-between items-center py-1 border-b border-white/5">
                  <span className="text-white/80 text-[8px] flex items-center gap-1 truncate max-w-[200px]">
                    <CheckSquare className="w-3 h-3 text-jarvis-blue" /> {task.name}
                  </span>
                  <span className={`px-1 rounded text-[7px] border font-bold ${getTaskStatusClass(task.status)}`}>
                    {task.status}
                  </span>
                </div>
              ))}
            </div>

            {/* Researcher scraping findings */}
            <div className="h-20 overflow-y-auto flex flex-col gap-1.5 pr-1">
              <div className="text-white/40 text-[8px] uppercase tracking-widest flex justify-between">
                <span>Researcher Findings</span>
                <span>Scraper</span>
              </div>
              {researchFindings.length === 0 ? (
                <span className="text-white/30 text-[9px]">No active web scraper findings yet.</span>
              ) : (
                researchFindings.map((res) => (
                  <div key={res.id} className="p-1 rounded bg-black/20 border border-white/5 text-white/70">
                    <div className="text-[7px] text-jarvis-blue font-bold flex items-center gap-1">
                      <Search className="w-2.5 h-2.5" /> QUERY: {res.query}
                    </div>
                    <div className="text-[8px] truncate mt-0.5">{res.finding}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

      </div>

      {/* BOTTOM TERMINAL OVERRIDE */}
      <div className="w-full h-24 p-3 glass-panel rounded-lg flex flex-col justify-between border border-jarvis-blue/15 shadow-xl relative no-drag">
        {/* Terminal Header */}
        <div className="flex justify-between items-center text-[8px] font-mono text-white/30 border-b border-white/5 pb-1">
          <div className="flex items-center gap-1 text-jarvis-blue">
            <Terminal className="w-3.5 h-3.5 animate-pulse" />
            <span className="font-orbitron font-extrabold tracking-widest text-[8.5px]">COMMAND TERMINAL OVERRIDE CONSOLE</span>
          </div>
          <span className="font-mono text-[7px]">COM_LINK: {netStatus} // PACKETS_OK</span>
        </div>

        {/* Real-time terminal scroll logs */}
        <div className="flex-1 my-1.5 overflow-y-auto font-mono text-[9px] text-white/55 flex flex-col gap-0.5 pr-2 select-text max-h-[36px]">
          {terminalLogs.map((log, index) => (
            <div key={index} className="leading-tight">
              <span className="text-emerald-500/80">root@jarvis-hud:~$</span> {log}
            </div>
          ))}
          <div ref={terminalEndRef} />
        </div>

        {/* Command terminal input */}
        <form onSubmit={handlePromptSubmit} className="w-full flex items-center gap-2 bg-black/60 border border-jarvis-blue/20 rounded-full px-4 py-1 focus-within:border-jarvis-blue/60 transition-all duration-300">
          <span className="text-jarvis-blue font-mono text-xs select-none">{`SYSTEM@JARVIS:~$`}</span>
          <input
            type="text"
            value={promptInput}
            onChange={(e) => setPromptInput(e.target.value)}
            placeholder="Type direct keyboard command prompt override... (e.g. 'open settings', 'search google for cookies')"
            className="bg-transparent border-none outline-none text-xs font-mono text-jarvis-blue flex-1 placeholder-jarvis-blue/30"
          />
          <button type="submit" className="hidden" />
        </form>
      </div>
    </div>
  );
};

export default App;
