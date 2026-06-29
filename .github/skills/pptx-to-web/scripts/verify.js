#!/usr/bin/env node
// Headless empty-slide check. Usage: node verify.js [url]
const url = process.argv[2] || 'http://localhost:8765/';
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.setViewportSize({ width: 1366, height: 768 });
  await p.goto(url); await p.waitForTimeout(800);
  const s = await p.$$('section'); const empty = [];
  for (let i = 0; i < s.length; i++) {
    await s[i].scrollIntoViewIfNeeded(); await p.waitForTimeout(120);
    if ((await s[i].innerText()).replace(/\s/g, '').length < 8) empty.push(i + 1);
  }
  console.log('sections:', s.length, 'empty:', JSON.stringify(empty));
  await b.close(); process.exit(empty.length ? 1 : 0);
})();
