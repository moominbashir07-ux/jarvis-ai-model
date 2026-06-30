import React, { useEffect, useRef } from 'react';

export const HackingBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;

    // Resize handler
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Characters and code snippets to render
    const matrixChars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz{}[]<>;:!=+-*/&|%#$@".split("");
    const codeSnippets = [
      "import os", "class BrainManager", "def generate", "sys.stdout", "SQLite WAL", 
      "EventBus.publish", "CircuitBreaker.state", "ipcRenderer.send", "ELECTRON_READY",
      "0xDEADBEEF", "ACCESS_GRANTED", "SYSTEM_ONLINE", "NEURAL_NET_LOADED", "PORT_8765",
      "let x = 1;", "while True:", "self.router.route", "yarn dev", "npm run",
      "pyttsx3.init", "pythoncom.CoInit", "STATUS_OK", "DEGRADED", "OFFLINE"
    ];

    const fontSize = 10;
    const columns = Math.ceil(canvas.width / 20);

    // Setup streams with 3D depth variables (depth determines size, speed, and opacity)
    interface Stream {
      x: number;
      y: number;
      speed: number;
      depth: number; // 0.1 to 1.0
      chars: string[];
    }

    const streams: Stream[] = [];
    for (let i = 0; i < columns; i++) {
      const depth = 0.2 + Math.random() * 0.8; // Perspective depth
      streams.push({
        x: i * 20,
        y: Math.random() * -canvas.height,
        speed: (2 + Math.random() * 5) * depth,
        depth: depth,
        chars: []
      });
    }

    const draw = () => {
      // Semi-transparent black clear to create trailing glow effect
      ctx.fillStyle = 'rgba(10, 15, 25, 0.15)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      streams.forEach((stream) => {
        // Adjust stream character buffer
        if (stream.chars.length === 0 || Math.random() < 0.05) {
          // Occasionally insert standard code snippets instead of random characters
          if (Math.random() < 0.15) {
            const snippet = codeSnippets[Math.floor(Math.random() * codeSnippets.length)];
            stream.chars = snippet.split("");
          } else {
            stream.chars = Array.from({ length: 5 + Math.floor(Math.random() * 10) }, () => 
              matrixChars[Math.floor(Math.random() * matrixChars.length)]
            );
          }
        }

        // Draw character column
        const currentFontSize = fontSize * stream.depth;
        ctx.font = `bold ${currentFontSize}px monospace`;

        // Style based on depth (closer streams are brighter and larger)
        const opacity = stream.depth * 0.6;
        // Cyber cyan/teal/blue color palette for JARVIS hacker aesthetic
        ctx.fillStyle = `rgba(0, 220, 255, ${opacity})`;

        stream.chars.forEach((char, idx) => {
          const charY = stream.y + idx * (currentFontSize + 4);
          if (charY > 0 && charY < canvas.height) {
            // First character is highlighted white/bright cyan
            if (idx === 0) {
              ctx.fillStyle = `rgba(220, 250, 255, ${opacity * 1.5})`;
            } else {
              ctx.fillStyle = `rgba(0, 180, 240, ${opacity * (1 - idx / stream.chars.length)})`;
            }
            ctx.fillText(char, stream.x, charY);
          }
        });

        // Move down
        stream.y += stream.speed;

        // Reset when stream goes off screen
        if (stream.y > canvas.height) {
          stream.y = -100;
          stream.depth = 0.2 + Math.random() * 0.8;
          stream.speed = (2 + Math.random() * 5) * stream.depth;
          stream.chars = [];
        }
      });

      animationId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full -z-10 pointer-events-none opacity-40"
      style={{ mixBlendMode: 'screen' }}
    />
  );
};
