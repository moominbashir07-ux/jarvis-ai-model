import React, { useEffect, useRef } from 'react';

type JarvisState = 'Sleeping' | 'Listening' | 'Thinking' | 'Speaking' | 'Processing';

interface WaveformProps {
  state: JarvisState;
}

export const Waveform: React.FC<WaveformProps> = ({ state }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let phase = 0;

    // Responsive sizing
    const resizeCanvas = () => {
      canvas.width = canvas.parentElement?.clientWidth || 360;
      canvas.height = 64;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Wave drawing loop
    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const width = canvas.width;
      const height = canvas.height;
      const centerY = height / 2;

      phase += 0.08; // wave speed modifier

      let waveCount = 3;
      let colors = ['rgba(0, 240, 255, 0.4)', 'rgba(0, 240, 255, 0.2)', 'rgba(0, 240, 255, 0.6)'];
      let baseAmplitude = 15;
      let frequency = 0.015;

      if (state === 'Sleeping') {
        baseAmplitude = 2; // almost flat
        waveCount = 1;
        colors = ['rgba(0, 240, 255, 0.15)'];
        frequency = 0.008;
      } else if (state === 'Thinking') {
        baseAmplitude = 6;
        waveCount = 2;
        colors = ['rgba(255, 170, 0, 0.3)', 'rgba(255, 170, 0, 0.5)'];
        frequency = 0.04; // rapid frequency ripples
      } else if (state === 'Speaking') {
        // High modulating spikes
        baseAmplitude = 25;
        waveCount = 3;
        colors = ['rgba(0, 240, 255, 0.3)', 'rgba(0, 240, 255, 0.15)', 'rgba(0, 240, 255, 0.65)'];
        frequency = 0.02;
      } else if (state === 'Processing') {
        baseAmplitude = 4;
        waveCount = 2;
        colors = ['rgba(255, 59, 48, 0.3)', 'rgba(255, 59, 48, 0.6)'];
        frequency = 0.03;
      }

      // Draw waves
      for (let w = 0; w < waveCount; w++) {
        ctx.beginPath();
        ctx.strokeStyle = colors[w];
        ctx.lineWidth = w === 2 ? 2.5 : 1;

        const wavePhase = phase + w * (Math.PI / 2);
        
        for (let x = 0; x < width; x++) {
          // Fade wave out at the edges (using sine window function)
          const edgeMask = Math.sin((x / width) * Math.PI);
          
          // Compute wave height
          const noise = state === 'Speaking' ? Math.sin(phase * 2.5) * 6 : 0;
          const currentAmplitude = (baseAmplitude + noise) * edgeMask;
          
          const y = centerY + Math.sin(x * frequency + wavePhase) * currentAmplitude;

          if (x === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        ctx.stroke();
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', resizeCanvas);
    };
  }, [state]);

  return (
    <div className="w-[320px] h-[64px] flex items-center justify-center pointer-events-none no-drag">
      <canvas ref={canvasRef} className="opacity-90" />
    </div>
  );
};
