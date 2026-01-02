import React, { useEffect, useRef } from 'react';

interface WaveAnimationProps {
  isActive: boolean;
  volume: number;
}

export const WaveAnimation: React.FC<WaveAnimationProps> = ({ isActive, volume }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    let frame = 0;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (isActive) {
        const numWaves = 5;
        const maxRadius = 200;

        for (let i = 0; i < numWaves; i++) {
          const progress = (frame + i * 20) % 100;
          const radius = (progress / 100) * maxRadius;
          const opacity = 1 - progress / 100;
          const adjustedOpacity = opacity * (volume / 100);

          ctx.beginPath();
          ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
          ctx.strokeStyle = `rgba(0, 150, 255, ${adjustedOpacity * 0.6})`;
          ctx.lineWidth = 3;
          ctx.stroke();
        }

        frame += 2;
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive, volume]);

  return (
    <canvas
      ref={canvasRef}
      width={500}
      height={500}
      style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        pointerEvents: 'none',
        zIndex: 1,
      }}
    />
  );
};
