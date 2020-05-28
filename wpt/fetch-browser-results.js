/* -*- Mode: Java; tab-width: 4; indent-tabs-mode:nil; c-basic-offset: 4 -*- */
/* vim: set ts=4 et sw=4 tw=80: */
async function fetchWPTFYITestResults(browser) {
  let response = await fetch(`https://wpt.fyi/api/runs?product=${browser}&label=experimental&label=master`)
  let result = await response.json()
  response = await fetch(result[0].raw_results_url)
  return await response.json()
}

async function fetchIgaliaBuildWebPlatformTestResults(browser) {
    let response = await fetch(`https://build-chromium.igalia.com/mathml/wpt/blink-latest.json`);
    return await response.json();
}

async function fetchWebPlatformTestResults(browser) {
	let fn = (browser==='blink') ? fetchIgaliaBuildWebPlatformTestResults : fetchWPTFYITestResults;
	return await fn(browser)
}

function escapeHTML(source) {
    return source.replace(/[&<>"'/]/g, c => {
        return `&#x${c.charCodeAt(0).toString(16)};`;
    });
}
