(function(){
  const keys = {};
  addEventListener('keydown', e=>{ keys[e.key]=true; });
  addEventListener('keyup', e=>{ keys[e.key]=false; });

  function clamp(v,min,max){ return Math.max(min, Math.min(max, v)); }
  function rand(min,max){ return Math.random()*(max-min)+min; }

  function loop(update, render){
    let last = performance.now();
    function frame(t){
      const dt = Math.min(0.033, (t-last)/1000); // cap dt
      last = t;
      update(dt);
      render();
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  window.Engine = { keys, clamp, rand, loop };
})();
