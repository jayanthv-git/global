import React, { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  HERO_MEDIA,
  HERO_CHAPTERS,
  CHECKIN_TARGET,
  chapterOpacity,
} from './heroConfig.js';
import { connectHeroScroll } from './heroScroll.js';
import './HeroJourney.css';

export function HeroJourneyView({
  t,
  mode,
  mobile,
  loadVideo,
  onStart,
  rootRef,
  stageRef,
  videoRef,
  chaptersRef,
}) {
  const stacked = mode === 'static';
  function start() {
    onStart();
    // The target is an existing check-in view, not a new router or app state.
    requestAnimationFrame(() => document.getElementById(CHECKIN_TARGET)?.focus());
  }
  return (
    <section
      className={`hero-journey ${stacked ? 'hero-journey--static' : 'hero-journey--scroll'}`}
      aria-label={t('hero_label')}
      data-hero-mode={mode}
    >
      <a className="hero-skip" href={`#${CHECKIN_TARGET}`} onClick={start}>
        {t('hero_skip')}
      </a>
      <div className="hero-journey__track" ref={rootRef}>
        <div className="hero-journey__stage" ref={stageRef}>
          <div className="hero-journey__media">
            <img
              className="hero-journey__poster"
              src={stacked ? HERO_MEDIA.finalPoster : HERO_MEDIA.poster}
              width="1280"
              height="720"
              alt=""
              decoding="async"
            />
            {!stacked && loadVideo && (
              <video
                key={mobile ? 'mobile' : 'desktop'}
                ref={videoRef}
                className={mode === 'ready' ? 'is-ready' : ''}
                src={mobile ? HERO_MEDIA.mobile : HERO_MEDIA.desktop}
                muted
                playsInline
                preload="auto"
                aria-hidden="true"
                tabIndex={-1}
                poster={HERO_MEDIA.poster}
              />
            )}
            {!stacked && mode !== 'ready' && (
              <span className="hero-journey__loading" aria-hidden="true" />
            )}
          </div>
          <div className="hero-journey__chapters" ref={chaptersRef}>
            {HERO_CHAPTERS.map((chapter, index) => (
              <article
                key={chapter}
                className="hero-journey__chapter"
                style={
                  !stacked ? { '--chapter-opacity': index === 0 ? 1 : 0 } : undefined
                }
              >
                <h2>{t(`hero_${chapter}_title`)}</h2>
                <p>{t(`hero_${chapter}_body`)}</p>
              </article>
            ))}
          </div>
          <p className="hero-journey__prototype-note">{t('hero_demo_short')}</p>
          {!stacked && (
            <p className="hero-journey__scroll-hint" aria-hidden="true">
              {t('hero_scroll')}
            </p>
          )}
        </div>
      </div>
      <div className="hero-journey__after">
        <a className="hero-journey__cta" href={`#${CHECKIN_TARGET}`} onClick={start}>
          {t('hero_start')}
        </a>
        <p className="hero-journey__caption">{t('hero_caption')}</p>
        <p className="hero-journey__disclaimer">{t('hero_demo_note')}</p>
      </div>
    </section>
  );
}

export default function HeroJourney({ onStart }) {
  const { t } = useTranslation();
  const [reduced, setReduced] = useState(
    () =>
      typeof window === 'undefined' ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  );
  const [mobile, setMobile] = useState(
    () =>
      typeof window !== 'undefined' && window.matchMedia('(max-width: 767px)').matches,
  );
  const [shortView, setShortView] = useState(
    () =>
      typeof window !== 'undefined' && window.matchMedia('(max-height: 480px)').matches,
  );
  const [failure, setFailure] = useState(false);
  const [loadVideo, setLoadVideo] = useState(false);
  const [ready, setReady] = useState(false);
  const rootRef = useRef(null);
  const stageRef = useRef(null);
  const videoRef = useRef(null);
  const chaptersRef = useRef(null);
  const stacked = reduced || failure || shortView;

  useEffect(() => {
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const size = window.matchMedia('(max-width: 767px)');
    const height = window.matchMedia('(max-height: 480px)');
    const updateHeight = () => setShortView(height.matches);
    const updateMotion = () => setReduced(motion.matches);
    const updateSize = () => {
      setMobile(size.matches);
      setReady(false);
    };
    motion.addEventListener('change', updateMotion);
    size.addEventListener('change', updateSize);
    height.addEventListener('change', updateHeight);
    return () => {
      motion.removeEventListener('change', updateMotion);
      size.removeEventListener('change', updateSize);
      height.removeEventListener('change', updateHeight);
    };
  }, []);

  useEffect(() => {
    if (stacked) return;
    if (!('IntersectionObserver' in window)) {
      setFailure(true);
      return;
    }
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setLoadVideo(true);
          observer.disconnect();
        }
      },
      { rootMargin: '150px' },
    );
    observer.observe(rootRef.current);
    return () => observer.disconnect();
  }, [stacked]);

  useEffect(() => {
    if (stacked || !loadVideo || !videoRef.current) return;
    return connectHeroScroll({
      root: rootRef.current,
      stage: stageRef.current,
      video: videoRef.current,
      mobile,
      onReady: () => setReady(true),
      onFallback: () => setFailure(true),
      onProgress: (progress) => {
        Array.from(chaptersRef.current?.children || []).forEach((chapter, index) => {
          chapter.style.setProperty('--chapter-opacity', chapterOpacity(progress, index));
        });
      },
    });
  }, [stacked, loadVideo, mobile]);

  return (
    <HeroJourneyView
      t={t}
      mode={stacked ? 'static' : ready ? 'ready' : 'loading'}
      mobile={mobile}
      loadVideo={loadVideo}
      onStart={onStart}
      rootRef={rootRef}
      stageRef={stageRef}
      videoRef={videoRef}
      chaptersRef={chaptersRef}
    />
  );
}
