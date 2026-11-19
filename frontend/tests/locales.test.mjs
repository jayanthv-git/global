import test from 'node:test';
import assert from 'node:assert/strict';
import {resources} from '../src/locales.js';
test('English and Arabic cover the same UI and safety labels',()=>{
 const en=resources.en.translation,ar=resources.ar.translation;
 assert.deepEqual(Object.keys(en).sort(),Object.keys(ar).sort());
 for(const [key,value] of Object.entries(ar))assert.ok(typeof value==='string'&&value.trim(),key);
 for(const key of ['urgent_guidance','needs_verification','placeholder','simulated','synthetic','access_denied'])assert.notEqual(en[key],ar[key]);
});
