(() => {
  const canvas = document.getElementById('stars');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let w, h, stars;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
    // mai multe stele & mai vizibile
    const count = Math.min(400, Math.floor((w * h) / 6000));
    stars = Array.from({ length: count }, () => ({
      x: Math.random() * w,
      y: Math.random() * h,
      z: Math.random() * 1.1 + 0.25,      // viteză
      r: Math.random() * 1.5 + 0.3,       // rază
      tw: Math.random() * 0.5 + 0.5       // factor twinkle
    }));
  }

  function draw() {
    ctx.clearRect(0, 0, w, h);
    for (const s of stars) {
      // mișcare ușor diagonală
      s.x -= s.z * 0.55;
      s.y += s.z * 0.20;

      // reintrodu în colțul dreapta-sus
      if (s.x < -2 || s.y > h + 2) {
        s.x = w + Math.random() * 40;
        s.y = -10 + Math.random() * 40;
        s.z = Math.random() * 1.1 + 0.25;
        s.r = Math.random() * 1.5 + 0.3;
        s.tw = Math.random() * 0.5 + 0.5;
      }

      // twinkle + culoare verde neon
      const alpha = 0.5 + Math.sin((s.x + s.y) * 0.02) * 0.25 * s.tw;
      ctx.fillStyle = `rgba(36, 255, 135, ${0.6 + alpha})`;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();
    }
    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', resize);
  resize();
  draw();
})();
