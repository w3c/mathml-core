function loadJSON(browser, callback) {
    let xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");
    var json = `https://build-chromium.igalia.com/mathml/wpt/${browser}-latest.json`;
    xobj.open('GET', json, true);
    xobj.onreadystatechange = function () {
        if (xobj.readyState == 4)
            alert(xobj.status)
        if (xobj.readyState == 4 && xobj.status == "200")
            callback(browser, JSON.parse(xobj.responseText));
    };
    xobj.send(null);
}

function setResults(browser, json) {
    for (let i in json.results)
        wptResults[json.results[i].test][browser] =
        (json.results[i].status === "PASS");

    console.log(wptResults);
}

loadJSON("blink", setResults);
loadJSON("gecko", setResults);
loadJSON("webkit", setResults);
