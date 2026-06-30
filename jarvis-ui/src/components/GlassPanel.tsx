import React from 'react';
import { motion } from 'framer-motion';

interface GlassPanelProps {
  children: React.ReactNode;
  isActive: boolean;
  statusText: string;
}

export const GlassPanel: React.FC<GlassPanelProps> = ({ children, isActive, statusText }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: 20 }}
      transition={{ type: 'spring', stiffness: 100, damping: 15 }}
      className={`relative w-[480px] h-[480px] rounded-full p-8 flex flex-col items-center justify-center transition-all duration-500 glass-panel ${
        isActive ? 'glass-panel-active' : ''
      }`}
    >
      {/* Outer Holographic Grid Overlay Lines */}
      <div className="absolute inset-0 rounded-full border border-jarvis-blue/10 pointer-events-none animate-pulse" />
      
      {/* Top Left Crosshair */}
      <div className="absolute top-10 left-10 w-4 h-4 border-t-2 border-l-2 border-jarvis-blue/40 pointer-events-none" />
      {/* Top Right Crosshair */}
      <div className="absolute top-10 right-10 w-4 h-4 border-t-2 border-r-2 border-jarvis-blue/40 pointer-events-none" />
      {/* Bottom Left Crosshair */}
      <div className="absolute bottom-10 left-10 w-4 h-4 border-b-2 border-l-2 border-jarvis-blue/40 pointer-events-none" />
      {/* Bottom Right Crosshair */}
      <div className="absolute bottom-10 right-10 w-4 h-4 border-b-2 border-r-2 border-jarvis-blue/40 pointer-events-none" />

      {/* Holographic scanning horizontal line */}
      <div className="absolute inset-x-12 top-0 h-[1px] bg-gradient-to-r from-transparent via-jarvis-blue/20 to-transparent pointer-events-none animate-[bounce_6s_infinite_linear]" />

      {/* Header Holographic Diagnostics */}
      <div className="absolute top-12 font-orbitron text-[9px] tracking-[0.25em] text-jarvis-blue/50 flex flex-col items-center uppercase pointer-events-none">
        <span>JARVIS AI OS // PERCEPTION MODULE</span>
        <span className="mt-1 text-jarvis-blue/30 text-[7px]">CORE TEMP: 37°C | MEMORY LINK: SECURE</span>
      </div>

      {/* Core Interface Children */}
      <div className="flex-1 flex flex-col items-center justify-center z-10">
        {children}
      </div>

      {/* Footer Diagnostic Panel */}
      <div className="absolute bottom-12 font-orbitron text-[10px] text-center tracking-[0.15em] pointer-events-none z-10">
        <span className="text-jarvis-blue/40">SYS_STATUS: </span>
        <span className="text-jarvis-blue font-semibold uppercase text-glow-blue">{statusText}</span>
      </div>
    </motion.div>
  );
};
