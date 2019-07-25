/* -*- Mode: Java; tab-width: 4; indent-tabs-mode:nil; c-basic-offset: 4 -*- */
/* vim: set ts=4 et sw=4 tw=80: */

async function fetchWebPlatformTestResults(browser) {
    let response = await fetch(`https://build-chromium.igalia.com/mathml/wpt/${browser}-latest.json`);
    return response.json();
}
