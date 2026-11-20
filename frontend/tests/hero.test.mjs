import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdir, writeFile, rm, stat } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { build } from 'esbuild';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import i18next from 'i18next';
import { I18nextProvider } from 'react-i18next';
import { resources } from '../src/locales.js';
import {
  HERO_MEDIA,
  CHECKIN_TARGET,
  chapterOpacity,
  scrollProgress,
} from '../src/heroConfig.js';
import { connectHeroScroll } from '../src/heroScroll.js';

// Compile JSX with Vite's existing esbuild dependency; no browser-test package added.
const compiled = resolve('node_modules/.cache', `hero-test-${process.pid}.mjs`);
await mkdir(resolve('node_modules/.cache'), { recursive: true });
const result = await build({
  stdin: {
    contents:
      "export {HeroJourneyView, default as HeroJourney} from './src/HeroJourney.jsx'; export {Checkin} from './src/Checkin.jsx';",
    resolveDir: resolve('.'),
  },
  bundle: true,
  platform: 'node',
  format: 'esm',
  packages: 'external',
  loader: { '.css': 'empty' },
  write: false,
});
await writeFile(compiled, result.outputFiles[0].text);
const { HeroJourneyView, HeroJourney, Checkin } = await import(
  pathToFileURL(compiled).href
);
await rm(compiled);
const t = (key) => resources.en.translation[key];
const view = (mode, mobile = false) =>
  React.createElement(HeroJourneyView, {
    t,
    mode,
    mobile,
    loadVideo: true,
    onStart() {},
  });

test('hero renders four semantic chapters, silent hidden media and the existing check-in target', () => {
  const html = renderToStaticMarkup(view('ready'));
  assert.equal((html.match(/<article/g) || []).length, 4);
  assert.ok(html.includes(HERO_MEDIA.desktop));
  assert.match(html, /muted=""/);
  assert.match(html, /playsInline=""/);
  assert.match(html, /aria-hidden="true"/);
  assert.doesNotMatch(html, /controls=|autoPlay=/);
  assert.equal(
    (html.match(new RegExp(`href="#${CHECKIN_TARGET}"`, 'g')) || []).length,
    2,
  );
  assert.ok(html.includes(t('hero_caption')));
});

test('reduced-motion/error presentation is stacked with all chapters and no video', () => {
  const html = renderToStaticMarkup(view('static'));
  assert.match(html, /hero-journey--static/);
  assert.doesNotMatch(html, /<video|chapter-opacity/);
  assert.ok(html.includes(HERO_MEDIA.finalPoster));
  for (const chapter of ['notice', 'support', 'consent', 'people'])
    assert.ok(html.includes(t(`hero_${chapter}_title`)));
});

test('both CTA and skip link call the existing start action; Checkin supplies the target', async () => {
  let starts = 0;
  const previousRaf = globalThis.requestAnimationFrame;
  const previousDocument = globalThis.document;
  let focused = false;
  globalThis.requestAnimationFrame = (fn) => fn();
  globalThis.document = {
    getElementById: (id) => {
      assert.equal(id, CHECKIN_TARGET);
      return {
        focus() {
          focused = true;
        },
      };
    },
  };
  try {
    const tree = HeroJourneyView({ t, mode: 'static', onStart: () => starts++ });
    function links(node) {
      if (!node || typeof node !== 'object') return [];
      return [
        ...(node.type === 'a' ? [node] : []),
        ...React.Children.toArray(node.props?.children).flatMap(links),
      ];
    }
    for (const link of links(tree)) {
      assert.equal(link.props.href, '#check-in');
      link.props.onClick();
    }
    assert.equal(starts, 2);
    assert.equal(focused, true);
  } finally {
    globalThis.requestAnimationFrame = previousRaf;
    globalThis.document = previousDocument;
  }
  const i18n = i18next.createInstance();
  await i18n.init({ lng: 'en', resources });
  const html = renderToStaticMarkup(
    React.createElement(
      I18nextProvider,
      { i18n },
      React.createElement(Checkin, { urgent() {}, onResult() {} }),
    ),
  );
  assert.match(html, /id="check-in"/);
  assert.ok(html.indexOf('hero-journey') < html.indexOf(t('welcome')));
});

test('mobile selects only its small source; shipped video files remain inside budgets', async () => {
  const html = renderToStaticMarkup(view('ready', true));
  assert.ok(html.includes(HERO_MEDIA.mobile));
  assert.ok(!html.includes(HERO_MEDIA.desktop));
  assert.ok((await stat('public' + HERO_MEDIA.desktop)).size < 15_000_000);
  assert.ok((await stat('public' + HERO_MEDIA.mobile)).size < 8_000_000);
});

test('progress clamps to the section; chapter fades preserve the first and last endpoints', () => {
  assert.equal(scrollProgress(100, 4000, 1000), 0);
  assert.equal(scrollProgress(-1500, 4000, 1000), 0.5);
  assert.equal(scrollProgress(-5000, 4000, 1000), 1);
  assert.equal(chapterOpacity(0, 0), 1);
  assert.equal(chapterOpacity(1, 3), 1);
  assert.equal(chapterOpacity(0.4, 0), 0);
  assert.equal(chapterOpacity(0.4, 1), 1);
});

function harness() {
  let now = 0,
    id = 0,
    bounds = { top: 0, height: 4000 },
    intersection;
  const frames = new Map(),
    timers = new Map();
  function target() {
    const listeners = new Map();
    return {
      listeners,
      addEventListener(type, fn) {
        listeners.set(type, fn);
      },
      removeEventListener(type) {
        listeners.delete(type);
      },
      emit(type) {
        listeners.get(type)?.();
      },
    };
  }
  const env = {
    ...target(),
    document: { ...target(), hidden: false },
    performance: { now: () => now },
    requestAnimationFrame(fn) {
      frames.set(++id, fn);
      return id;
    },
    cancelAnimationFrame(id) {
      frames.delete(id);
    },
    setTimeout(fn, delay) {
      timers.set(++id, { fn, due: now + delay });
      return id;
    },
    clearTimeout(id) {
      timers.delete(id);
    },
    IntersectionObserver: class {
      constructor(fn) {
        intersection = fn;
      }
      observe() {}
      disconnect() {}
    },
  };
  let currentTime = 0;
  const video = {
    ...target(),
    duration: 8,
    readyState: 0,
    seeking: false,
    get currentTime() {
      return currentTime;
    },
    set currentTime(value) {
      currentTime = value;
      this.seeking = true;
    },
  };
  const fallback = [],
    progress = [];
  let ready = 0;
  const cleanup = connectHeroScroll({
    env,
    video,
    mobile: false,
    root: { getBoundingClientRect: () => bounds },
    stage: { getBoundingClientRect: () => ({ height: 1000 }) },
    onProgress: (p) => progress.push(p),
    onReady: () => ready++,
    onFallback: (reason) => fallback.push(reason),
  });
  function advance(ms = 34) {
    now += ms;
    for (const [key, timer] of [...timers])
      if (timer.due <= now) {
        timers.delete(key);
        timer.fn();
      }
    const pending = [...frames.values()];
    frames.clear();
    pending.forEach((fn) => fn(now));
  }
  return {
    env,
    video,
    frames,
    fallback,
    progress,
    cleanup,
    advance,
    get ready() {
      return ready;
    },
    enter() {
      intersection([{ isIntersecting: true }]);
    },
    leave() {
      intersection([{ isIntersecting: false }]);
    },
    metadata() {
      video.readyState = 2;
      video.emit('loadedmetadata');
      video.emit('loadeddata');
    },
    scroll(top) {
      bounds = { ...bounds, top };
      env.emit('scroll');
    },
    seeked() {
      video.seeking = false;
      video.emit('seeked');
    },
  };
}

test('scrubbing waits for metadata, maps scroll to time and stops offscreen', () => {
  const h = harness();
  h.enter();
  assert.equal(h.env.listeners.has('scroll'), false);
  h.metadata();
  assert.equal(h.ready, 1);
  h.scroll(-1500);
  for (let i = 0; i < 35; i++) {
    h.advance();
    h.seeked();
  }
  assert.ok(Math.abs(h.video.currentTime - 4) < 0.05);
  h.leave();
  assert.equal(h.frames.size, 0);
  const paused = h.video.currentTime;
  h.scroll(-2800);
  h.advance();
  assert.equal(h.video.currentTime, paused);
  h.cleanup();
  assert.equal(h.env.listeners.has('scroll'), false);
});

test('missing metadata and media errors request the stacked fallback', () => {
  const timeout = harness();
  timeout.advance(4001);
  assert.deepEqual(timeout.fallback, ['media-timeout']);
  const error = harness();
  error.video.emit('error');
  assert.deepEqual(error.fallback, ['media-error']);
});

test('blocked seeking falls back and hidden documents do not animate', () => {
  const h = harness();
  h.enter();
  h.metadata();
  h.scroll(-2000);
  h.advance();
  h.advance(1201);
  assert.deepEqual(h.fallback, ['seek-stalled']);
  const hidden = harness();
  hidden.enter();
  hidden.metadata();
  hidden.env.document.hidden = true;
  hidden.env.document.emit('visibilitychange');
  assert.equal(hidden.frames.size, 0);
  hidden.cleanup();
});

test('the real component honors prefers-reduced-motion on its initial render', async () => {
  const previousWindow = globalThis.window;
  globalThis.window = {
    matchMedia: (query) => ({ matches: query.includes('prefers-reduced-motion') }),
  };
  try {
    const i18n = i18next.createInstance();
    await i18n.init({ lng: 'en', resources });
    const html = renderToStaticMarkup(
      React.createElement(
        I18nextProvider,
        { i18n },
        React.createElement(HeroJourney, { onStart() {} }),
      ),
    );
    assert.match(html, /hero-journey--static/);
    assert.equal((html.match(/<article/g) || []).length, 4);
    assert.doesNotMatch(html, /<video/);
  } finally {
    globalThis.window = previousWindow;
  }
});
