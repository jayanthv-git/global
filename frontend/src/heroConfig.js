// Swap all media here. These paths are same-origin, with no 4K authoring input.
export const HERO_MEDIA = Object.freeze({
  desktop: '/hero/hero_scrub_1280.mp4',
  mobile: '/hero/hero_scrub_854.mp4',
  poster: '/hero/hero_poster.jpg',
  finalPoster: '/hero/hero_poster_final.jpg',
});
export const CHECKIN_TARGET = 'check-in';
export const HERO_CHAPTERS = ['notice', 'support', 'consent', 'people'];
export const clamp = (value) => Math.max(0, Math.min(1, value));
export function chapterOpacity(progress, index) {
  const start = index / 4;
  const end = (index + 1) / 4;
  const enter = index === 0 ? 1 : clamp((progress - start) / 0.045);
  const leave = index === 3 ? 1 : clamp((end - progress) / 0.045);
  return Math.min(enter, leave);
}
export function scrollProgress(top, height, stageHeight) {
  return clamp(-top / Math.max(1, height - stageHeight));
}
