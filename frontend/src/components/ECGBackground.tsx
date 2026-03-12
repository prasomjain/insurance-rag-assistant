import { useEffect, useRef } from "react";

export const ECGBackground = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let time = 0;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    window.addEventListener("resize", resize);
    resize();

    // Perspective projection helper
    const project = (x: number, y: number, z: number) => {
      const scale = 1000 / (1000 + z);
      const x2d = (x - canvas.width / 2) * scale + canvas.width / 2;
      const y2d = (y - canvas.height / 2) * scale + canvas.height / 2;
      return { x: x2d, y: y2d, scale };
    };

    const render = () => {
      time += 1;

      // Clear
      ctx.fillStyle = "#020617";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw Grid (Floor)
      // drawGrid(time);

      // Draw 3D-ish Sine Wave / ECG
      // Let's draw multiple lines for depth

      for (let z = 200; z > -200; z -= 50) {
        ctx.beginPath();
        const opacity = 1 - Math.abs(z) / 300;
        ctx.strokeStyle = `rgba(6, 182, 212, ${opacity})`;
        ctx.lineWidth = z === 0 ? 3 : 1;
        if (z === 0) {
          ctx.shadowBlur = 20;
          ctx.shadowColor = "#06b6d4";
        } else {
          ctx.shadowBlur = 0;
        }

        for (let x = 0; x < canvas.width; x += 10) {
          // Wave logic
          const waveSpeed = 5;
          const freq = 0.01;

          let y = Math.sin(x * freq + time * 0.05) * 30;

          // Heartbeat spike
          const spikeFreq = 300; // pixels between spikes
          const spikePos = (x - time * waveSpeed) % spikeFreq;

          if (Math.abs(spikePos) < 30) {
            y -=
              150 *
              Math.cos(((spikePos / 30) * Math.PI) / 2) *
              (1 - Math.abs(z) / 300);
          }

          // Project to 3D
          // x is screen x, y is height, z is depth
          const p = project(x, canvas.height / 2 + y + 100, z);

          if (x === 0) ctx.moveTo(p.x, p.y);
          else ctx.lineTo(p.x, p.y);
        }
        ctx.stroke();
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas ref={canvasRef} className="fixed inset-0 z-0 pointer-events-none" />
  );
};
