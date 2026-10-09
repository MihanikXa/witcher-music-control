// Browser-only design QA. No game launch, resource patching or deployment.
const path = require('path');
const fs = require('fs');
const {pathToFileURL} = require('url');
const { chromium } = require('playwright');
(async () => {
  const root = path.resolve(__dirname, '..');
  const out = path.join(root, 'build', 'comparison');
  fs.mkdirSync(out, {recursive:true});
  const browser = await chromium.launch({headless:true, channel:'msedge'});
  try {
    const page = await browser.newPage({viewport:{width:1920,height:1200},deviceScaleFactor:1});
    await page.goto(pathToFileURL(path.join(root,'design','comparison.html')).href);
    await page.waitForFunction(() => document.body.dataset.fontsLoaded === 'true');
    const results = [];
    for (const scene of ['daylight','snow','cave','bright','fire']) {
      await page.selectOption('#scene', scene);
      await page.screenshot({path:path.join(out,scene+'.png'),fullPage:true});
      results.push({scene, fontsLoaded:true, mockup:true});
    }
    await page.selectOption('#scene','snow');
    await page.selectOption('#treatment','backing');
    await page.selectOption('#target','hostile');
    await page.screenshot({path:path.join(out,'snow-backing-hostile.png'),fullPage:true});
    await page.setViewportSize({width:1080,height:1080});
    await page.screenshot({path:path.join(out,'1080-preview.png'),fullPage:true});
    fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({results,gameTest:false},null,2));
    console.log('Rendered five backgrounds, backing/hostility stress test and narrow preview. Fonts loaded.');
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
