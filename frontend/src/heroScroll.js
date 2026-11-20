import { clamp, scrollProgress } from './heroConfig.js';

// Media lifecycle and scrubbing are isolated from every care/safety workflow.
export function connectHeroScroll({
  root,
  stage,
  video,
  mobile,
  onProgress,
  onReady,
  onFallback,
  env = window,
}) {
  let disposed = false;
  let metadata = false;
  let frameReady = false;
  let visible = false;
  let frame = 0;
  let progress = 0;
  let target = 0;
  let lastFrame = 0;
  let lastSeek = -Infinity;
  let seekStarted = null;
  let seekTimer;
  let slowSeeks = 0;
  const minInterval = mobile ? 1000 / 12 : 1000 / 30;
  const minChange = mobile ? 1 / 24 : 1 / 48;
  const clock = () => env.performance.now();
  const active = () => visible && !env.document.hidden && !disposed;

  function fail(reason) {
    if (disposed) return;
    cleanup();
    onFallback(reason);
  }
  const loadTimer = env.setTimeout(() => {
    if (!metadata || !frameReady) fail('media-timeout');
  }, 4000);

  function measure() {
    const bounds = root.getBoundingClientRect();
    target = scrollProgress(
      bounds.top,
      bounds.height,
      stage.getBoundingClientRect().height,
    );
  }
  function schedule() {
    if (active() && metadata && !frame) frame = env.requestAnimationFrame(tick);
  }
  function scroll() {
    measure();
    schedule();
  }
  function stopFrames() {
    env.cancelAnimationFrame(frame);
    frame = 0;
    lastFrame = 0;
    env.clearTimeout(seekTimer);
    seekStarted = null;
  }
  function visibility() {
    if (active()) scroll();
    else stopFrames();
  }
  function tick(time) {
    frame = 0;
    if (!active()) return;
    const elapsed = lastFrame ? Math.min(time - lastFrame, 100) : 16;
    lastFrame = time;
    const difference = target - progress;
    progress =
      Math.abs(difference) < 0.001
        ? target
        : progress + difference * (1 - Math.exp(-elapsed / 85));
    onProgress(clamp(progress));
    // Avoid seeking exactly beyond the last frame or queueing concurrent seeks.
    const desiredTime = Math.min(
      progress * video.duration,
      Math.max(0, video.duration - 0.001),
    );
    const needsSeek = Math.abs(video.currentTime - desiredTime) >= minChange;
    if (!video.seeking && needsSeek && time - lastSeek >= minInterval) {
      try {
        seekStarted = clock();
        lastSeek = time;
        seekTimer = env.setTimeout(() => fail('seek-stalled'), 1200);
        video.currentTime = desiredTime;
      } catch {
        fail('seek-blocked');
        return;
      }
    }
    // Sleep when settled; seeked/scroll/visibility events resume work as needed.
    if (Math.abs(target - progress) >= 0.001 || (!video.seeking && needsSeek)) schedule();
  }
  function seeked() {
    env.clearTimeout(seekTimer);
    if (seekStarted !== null && active()) {
      slowSeeks = clock() - seekStarted > 250 ? slowSeeks + 1 : 0;
      if (slowSeeks >= 3) {
        fail('slow-seeking');
        return;
      }
    }
    seekStarted = null;
    schedule();
  }
  function loadedMetadata() {
    if (metadata) return;
    if (!Number.isFinite(video.duration) || video.duration <= 0)
      return fail('invalid-duration');
    metadata = true;
    // No scroll or animation handlers are bound before valid metadata arrives.
    env.addEventListener('scroll', scroll, { passive: true });
    env.addEventListener('resize', scroll, { passive: true });
    env.document.addEventListener('visibilitychange', visibility);
    scroll();
  }
  function loadedData() {
    frameReady = true;
    if (metadata) env.clearTimeout(loadTimer);
    onReady();
  }
  function mediaError() {
    fail('media-error');
  }
  const observer = new env.IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    visibility();
  });
  observer.observe(root);
  video.addEventListener('loadedmetadata', loadedMetadata);
  video.addEventListener('loadeddata', loadedData);
  video.addEventListener('seeked', seeked);
  video.addEventListener('error', mediaError);
  if (video.readyState >= 1) loadedMetadata();
  if (video.readyState >= 2) loadedData();

  function cleanup() {
    disposed = true;
    stopFrames();
    env.clearTimeout(loadTimer);
    observer.disconnect();
    env.removeEventListener('scroll', scroll);
    env.removeEventListener('resize', scroll);
    env.document.removeEventListener('visibilitychange', visibility);
    video.removeEventListener('loadedmetadata', loadedMetadata);
    video.removeEventListener('loadeddata', loadedData);
    video.removeEventListener('seeked', seeked);
    video.removeEventListener('error', mediaError);
  }
  return cleanup;
}
