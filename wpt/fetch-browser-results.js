/* -*- Mode: Java; tab-width: 4; indent-tabs-mode:nil; c-basic-offset: 4 -*- */
/* vim: set ts=4 et sw=4 tw=80: */
async function fetchWebPlatformTestResults(browser) {
    let response = await fetch(`https://build-chromium.igalia.com/mathml/wpt/${browser}-latest.json`);
    return await response.json();
}

function escapeHTML(source) {
    return source.replace(/[&<>"'/]/g, c => {
        return `&#x${c.charCodeAt(0).toString(16)};`;
    });
}
