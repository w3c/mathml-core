function capitalize(string) {
    return `${string.charAt(0).toUpperCase()}${string.slice(1)}`;
}

function loadJSON(browser, callback) {
    let xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");
    var json = `https://build-chromium.igalia.com/mathml/wpt/${browser}-latest.json`;
    xobj.open('GET', json, true);
    xobj.onreadystatechange = function () {
        if (xobj.readyState == 4 && xobj.status == "200")
            callback(browser, JSON.parse(xobj.responseText));
    };
    xobj.send(null);
}

function uploadJSON(files, callback) {
    if (files.length !== 1)
        return;
    var reader = new FileReader();
    reader.onload = (e) => { callback(JSON.parse(e.target.result)); }
    reader.readAsText(files[0]);
}

function addTestCount(id, results) {
    var div = document.getElementById(id);
    var count = Object.keys(results).length;
    window.toggleImplementationResult = function() {
        div.lastElementChild.classList.toggle("folded");
    };
    div.insertAdjacentHTML("beforeend", `<h2><a href="javascript:toggleImplementationResult();">${count} tests</a></h2><div class="folded"><ul></ul><p>For complete list of tests (including subtests), see the <a href="${respecConfig.implementationReportURI}">implementation report</a>.</p></div>`);
}

function addBrowserResult(id, results, browser) {
    // We should probably do something like Bikeshed's test summary
    // (e.g. https://drafts.csswg.org/css-align)
    var passCount = 0, failCount = 0;
    for (let test in results) {
        if (results[test][browser] === "PASS")
            passCount++;
        else if (results[test][browser] === "FAIL")
            failCount++;
    }
    var untestedCount = Object.keys(results).length - (passCount + failCount);
    var ul = document.getElementById(id).getElementsByTagName("ul")[0];
    ul.insertAdjacentHTML("beforeend",
                           `<li><strong>${capitalize(browser)}</strong>: <p>${passCount} pass, ${failCount} fail, ${untestedCount} untested.</li>`
    );
}
