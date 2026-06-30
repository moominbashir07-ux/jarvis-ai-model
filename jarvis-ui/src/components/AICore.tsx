import React from 'react';
import { motion } from 'framer-motion';

type JarvisState = 'Sleeping' | 'Listening' | 'Thinking' | 'Speaking' | 'Processing';

interface AICoreProps {
  state: JarvisState;
}

export const AICore: React.FC<AICoreProps> = ({ state }) => {
  // Define colors and animation parameters based on state
  const getConfig = () => {
    switch (state) {
      case 'Sleeping':
        return {
          glowColor: 'rgba(0, 240, 255, 0.2)',
          ringColor: 'border-jarvis-blue/30',
          innerRingColor: 'border-jarvis-blue/20',
          coreColor: 'bg-jarvis-blue/20',
          speed: 25,
          scale: 0.95,
          glowIntensity: 'glow-blue',
          textColor: 'text-jarvis-blue/40',
        };
      case 'Listening':
        return {
          glowColor: 'rgba(0, 240, 255, 0.6)',
          ringColor: 'border-jarvis-blue/70',
          innerRingColor: 'border-jarvis-blue/40',
          coreColor: 'bg-jarvis-blue/50 shadow-[0_0_25px_rgba(0,240,255,0.7)]',
          speed: 10,
          scale: 1.05,
          glowIntensity: 'glow-blue',
          textColor: 'text-jarvis-blue',
        };
      case 'Thinking':
        return {
          glowColor: 'rgba(255, 170, 0, 0.6)',
          ringColor: 'border-jarvis-gold/75',
          innerRingColor: 'border-jarvis-gold/45',
          coreColor: 'bg-jarvis-gold/50 shadow-[0_0_25px_rgba(255,170,0,0.7)]',
          speed: 3,
          scale: 1.08,
          glowIntensity: 'glow-gold',
          textColor: 'text-jarvis-gold',
        };
      case 'Speaking':
        return {
          glowColor: 'rgba(0, 240, 255, 0.5)',
          ringColor: 'border-jarvis-blue/80',
          innerRingColor: 'border-jarvis-blue/50',
          coreColor: 'bg-jarvis-blue/40 shadow-[0_0_30px_rgba(0,240,255,0.6)]',
          speed: 15,
          scale: 1.12,
          glowIntensity: 'glow-blue',
          textColor: 'text-jarvis-blue',
        };
      case 'Processing':
        return {
          glowColor: 'rgba(255, 59, 48, 0.7)',
          ringColor: 'border-jarvis-red/80',
          innerRingColor: 'border-jarvis-red/50',
          coreColor: 'bg-jarvis-red/60 shadow-[0_0_35px_rgba(255,59,48,0.8)]',
          speed: 1.5,
          scale: 1.15,
          glowIntensity: 'glow-red',
          textColor: 'text-jarvis-red',
        };
    }
  };

  const config = getConfig();

  // Generate particle swarms
  const particles = Array.from({ length: 16 });

  return (
    <div className="relative flex items-center justify-center w-64 h-64 no-drag">
      {/* Outer Glow Halo */}
      <motion.div
        animate={{
          scale: [config.scale, config.scale * 1.08, config.scale],
          opacity: state === 'Sleeping' ? 0.3 : [0.5, 0.85, 0.5],
        }}
        transition={{
          repeat: Infinity,
          duration: state === 'Thinking' ? 1.5 : 2.5,
          ease: 'easeInOut',
        }}
        style={{ boxShadow: `0 0 60px ${config.glowColor}` }}
        className="absolute w-44 h-44 rounded-full pointer-events-none"
      />

      {/* Orbiting Particle Swarm */}
      {state !== 'Sleeping' && particles.map((_, i) => {
        const angle = (i * 360) / particles.length;
        const radius = 95 + Math.sin(i) * 15;
        const delay = i * 0.12;
        return (
          <motion.div
            key={i}
            className={`absolute w-1 h-1 rounded-full ${
              state === 'Thinking' ? 'bg-jarvis-gold' : state === 'Processing' ? 'bg-jarvis-red' : 'bg-jarvis-blue'
            }`}
            animate={{
              x: [
                Math.cos((angle * Math.PI) / 180) * radius,
                Math.cos(((angle + 360) * Math.PI) / 180) * radius,
              ],
              y: [
                Math.sin((angle * Math.PI) / 180) * radius,
                Math.sin(((angle + 360) * Math.PI) / 180) * radius,
              ],
              opacity: [0.2, 0.9, 0.2],
              scale: [0.6, 1.2, 0.6],
            }}
            transition={{
              duration: config.speed * 2,
              repeat: Infinity,
              ease: 'linear',
              delay: delay,
            }}
          />
        );
      })}

      {/* Outer Concentric Rotating Ring */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{
          repeat: Infinity,
          duration: config.speed,
          ease: 'linear',
        }}
        className={`absolute w-48 h-48 rounded-full border-2 border-dashed ${config.ringColor} flex items-center justify-center`}
      />

      {/* Inner Concentric Counter-Rotating Ring */}
      <motion.div
        animate={{ rotate: -360 }}
        transition={{
          repeat: Infinity,
          duration: config.speed * 1.5,
          ease: 'linear',
        }}
        className={`absolute w-40 h-40 rounded-full border border-double ${config.innerRingColor}`}
      />

      {/* Center Core Pulsing Orb */}
      <motion.div
        animate={
          state === 'Speaking'
            ? {
                scale: [config.scale, config.scale * 1.15, config.scale * 0.9, config.scale],
              }
            : state === 'Thinking'
            ? {
                scale: [config.scale, config.scale * 0.95, config.scale],
              }
            : {
                scale: [config.scale, config.scale * 1.05, config.scale],
              }
        }
        transition={{
          repeat: Infinity,
          duration: state === 'Speaking' ? 0.4 : state === 'Thinking' ? 0.8 : 2.0,
          ease: 'easeInOut',
        }}
        className={`absolute w-28 h-28 rounded-full ${config.coreColor} flex items-center justify-center z-10`}
      >
        {/* Core Detail Rings */}
        <div className="w-20 h-20 rounded-full border border-white/10 flex items-center justify-center">
          <div className="w-12 h-12 rounded-full border border-white/5 bg-black/30 flex items-center justify-center font-orbitron font-extrabold text-[8px] tracking-[0.1em]">
            <motion.span
              animate={state === 'Thinking' ? { opacity: [0.3, 1, 0.3] } : {}}
              transition={{ repeat: Infinity, duration: 1 }}
              className={`${config.textColor} uppercase`}
            >
              {state === 'Sleeping' ? 'IDLE' :
               state === 'Listening' ? 'LSTN' :
               state === 'Thinking' ? 'THNK' :
               state === 'Speaking' ? 'TALK' :
               state === 'Processing' ? 'EXEC' : 'IDLE'}
            </motion.span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
