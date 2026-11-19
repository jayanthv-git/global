import test from 'node:test';
import assert from 'node:assert/strict';
import { matchesCrisis } from '../src/safety.js';
const keywords = {
  en: ['suicide', 'kill myself', 'self-harm'],
  ar: ['انتحار', 'الانتحار', 'إيذاء نفسي'],
};
test('deterministic match supports case, Arabic diacritics and boundaries', () => {
  for (const text of [
    'I want to KILL MYSELF',
    'SUICIDE',
    'أفكر في الانتحار',
    'إيذَاء نفسي',
    'self-harm',
  ])
    assert.equal(matchesCrisis(text, keywords), true);
  for (const text of ['ordinary demo note', 'suicidewatchword', ''])
    assert.equal(matchesCrisis(text, keywords), false);
});
test('negation is deliberately not inferred by the exact keyword matcher', () => {
  assert.equal(matchesCrisis('not considering suicide', keywords), true);
});
