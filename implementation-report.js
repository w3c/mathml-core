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
