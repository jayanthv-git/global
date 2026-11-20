# Landing hero: implementation and verification

## Scope and assumptions

The existing frontend is React 19/Vite 7 with plain CSS and i18next. App navigation uses page state, not a URL router. The default Checkin view owns the existing `started` state. HeroJourney appears above the original welcome content only while `started` is false; its skip link and CTA use that same start action and focus the `#check-in` wrapper. No backend, data models, scoring, crisis behavior, dependency manifests or existing tests changed.

All four requested English chapters are preserved. Because the actual demo uses placeholder questionnaires and simulated clinicians, a persistent prototype notice and an additional caption qualify the requested “validated” and “licensed professionals” copy. This film is illustrative AI-generated Google Veo media supplied by the user, not a product screen or evidence of a clinical outcome. Arabic strings use the existing translation resources and **require native-speaker review**.

## Assets and swapping

Change only `HERO_MEDIA` in `frontend/src/heroConfig.js` to point to another prepared set of assets. All media requests are same-origin. No new runtime libraries, storage, tracking or third-party calls were added.

The 12,999,555-byte 4K source is local authoring input at `assets-source/hero-original.mp4`, ignored by Git and excluded from Vite public assets. Its SHA-256 is `14e7666756f91165d9905bc443180b40ad2d82e63e8ef23fe277e7944b884bc9`. The source file was not modified.

Run `scripts/prepare-hero-video.sh [source.mp4]` with FFmpeg on PATH, or set `FFMPEG` to its absolute executable path. This machine did not have FFmpeg on PATH; a temporary `imageio-ffmpeg` PyPI installation under `/tmp/saha-hero-tools` supplied the authoring executable. It is not an application dependency.

| Asset | Exact bytes | Preparation |
| --- | ---: | --- |
| hero_scrub_1280.mp4 | 3,077,474 | 1280×720, H.264, CRF 24, GOP 1 |
| hero_scrub_854.mp4 | 1,718,561 | 854×480, H.264, CRF 24, GOP 1 |
| hero_poster.jpg | 24,144 | Approximately 1 second, 1280×720 JPEG |
| hero_poster_final.jpg | 41,579 | Last decoded frame, 1280×720 JPEG |

FFmpeg decoding confirmed **186 source frames and 186 I-frames in each web copy**, 24 fps, yuv420p, no audio stream, and a `moov` atom before `mdat` (faststart). The source container is 7.91 seconds including audio/timestamp offsets; normalizing the video timestamps produces a 7.75-second silent track without dropping or trimming video frames. The script converts full-range input to video range, scales to even dimensions, and does not crop, alter playback speed, remove marks or edit the depicted content. CSS uses `object-fit: contain`, preserving the complete frame. No CRF increase or GOP 2 compromise was needed. The script tries those options only if a future replacement exceeds the budgets.

## Motion and accessible presentation

- A 400svh track contains a 100svh sticky stage. Native scroll measurements map progress to media duration, with an 85 ms time-based smoothing constant and small seek deadband.
- Only the matching source is mounted: 854px below 768 viewport pixels; 1280px otherwise. Loading begins when the landing section approaches the viewport. The poster reserves its space before decoding; the video has no audio, autoplay or controls and is hidden from assistive technology.
- Four real HTML articles remain in DOM order. Visual opacity changes do not remove screen-reader content or trap keyboard focus. Text uses a near-opaque dark backing with light text, logical CSS placement, and RTL mirroring. The video itself is never mirrored.
- Reduced-motion preferences, viewport height at or below 480px, missing IntersectionObserver, media errors, invalid duration, or a 4-second metadata/first-frame timeout switch to the final poster and normal stacked chapters. The CSS also independently removes pinning for reduced motion.
- rAF and seek watchdog work pause when the section is offscreen or the document is hidden. Scroll listeners attach only after valid metadata. Cleanup removes listeners, observers, timers and animation work.
- Seeking is capped at 30 updates/second on desktop and 12 on mobile, with no concurrent seeks. A blocked seek, 1.2-second stalled seek, or three consecutive seeks longer than 250 ms requests the static fallback. These are engineering usability limits, not clinical thresholds.
- Ordinary chapter changes reserve a stable grid area and do not change layout. Switching to the explicitly requested stacked fallback intentionally changes the page height. Browser UI height changes, font/zoom extremes, and fallback during a scroll can still move the viewport; no measured CLS score is claimed.

## Verification

Commands executed:

```sh
.venv/bin/python -m pytest -q
npm --prefix frontend test
npm --prefix frontend run build
./frontend/node_modules/.bin/prettier --check frontend/src/HeroJourney.jsx frontend/src/HeroJourney.css frontend/src/heroConfig.js frontend/src/heroScroll.js frontend/src/Checkin.jsx frontend/src/locales.js frontend/tests/hero.test.mjs
npm --prefix frontend run lint
```

- Backend: **72 tests passed**; one existing upstream Starlette/httpx deprecation warning.
- Frontend: **12 tests passed** (3 unchanged existing tests plus 9 new hero tests). New checks cover semantic rendering, reduced-motion initial rendering and stacked presentation, both start links and focus, existing Checkin integration, source selection/budgets, progress mapping, metadata readiness, offscreen/hidden suspension, timeout/error fallback and a stalled seek. They are Node/SSR/controller tests, not real-device browser automation.
- Production build passed. Main JS: approximately **346.91 kB / 109.55 kB gzip**; CSS: approximately **19.94 kB / 5.11 kB gzip**. Media is copied separately into `dist/hero`, not base64-inlined into JavaScript. Before this change, JS was 338.17 kB / 106.53 kB gzip and CSS 15.69 kB / 4.16 kB gzip.
- Prettier check passed on changed JavaScript/CSS and the new test file. **`npm run lint` cannot run: this repository has no lint script or lint configuration.** No linter result is claimed and no new lint tool was installed.
- In-app browser: observed actual scroll-driven video time changes, decoded ready state, muted playback, mobile/desktop source selection, English and Arabic RTL, no horizontal overflow at tested 390px and 1440px widths, and a real stacked/no-video fallback at 844×390. Pressing Enter on the final CTA opened the existing questionnaire, removed the hero and focused `#check-in`. No warnings/errors appeared in the captured console log. A screenshot is saved in `docs/hero-preview.jpg`.

## Limits and demo risks

Real iOS Safari/Android devices, slow networks, low-power mode, native screen readers, OS-level reduced-motion preference switching and a formal accessibility audit were not tested. Reduced-motion behavior is covered by the real component's initial-render test and static CSS inspection, not an OS accessibility-settings session. Browser media-failure behavior is covered by controller tests; no production network failure was injected.

Safari can delay decoding or make paused-video seeks choppy. The smaller source, lower update rate and automatic static fallback reduce this risk but do not establish smoothness on a real phone. The fallback is deliberately readable without a functioning media element. The existing service worker was not modified to pre-cache several megabytes of video: keep the local server running for the complete demo; closing the backend does not guarantee video availability offline. No new features were cut or partially connected.

## Files added or changed

Changed:

- `.gitignore`
- `README.md`
- `frontend/src/Checkin.jsx`
- `frontend/src/locales.js`

Added:

- `scripts/prepare-hero-video.sh`
- `frontend/public/hero/hero_scrub_1280.mp4`
- `frontend/public/hero/hero_scrub_854.mp4`
- `frontend/public/hero/hero_poster.jpg`
- `frontend/public/hero/hero_poster_final.jpg`
- `frontend/src/HeroJourney.jsx`
- `frontend/src/HeroJourney.css`
- `frontend/src/heroConfig.js`
- `frontend/src/heroScroll.js`
- `frontend/tests/hero.test.mjs`
- `docs/HERO_JOURNEY.md`
- `docs/hero-preview.jpg`

The original source remains ignored and is not part of the commit or shipped bundle.
