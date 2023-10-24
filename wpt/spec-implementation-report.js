/* -*- Mode: Java; tab-width: 4; indent-tabs-mode:nil; c-basic-offset: 4 -*- */
/* vim: set ts=4 et sw=4 tw=80: */

/*
  Get the latest aligned run data from WPT,
  massage it into a nice indexed
  result set (testPath:result) for quick reference
*/
let wptDataPromise = async function () {
    let f = await fetch('https://wpt.fyi/api/runs?aligned');
    let data = await f.json();
    let ids = data.map(rec => rec.id).join();

    // Note: this may get a bit "too much", but it doesn't matter to results
    f = await fetch(`https://wpt.fyi/api/search?label=master&label=experimental&q=math&run_ids=${ids}`);
    data = await f.json();

    return data.runs.map((run, i) => {
        let retVal = {
            engine: run.browser_name,
            results: {}
        };

        data.results.forEach((item) => {
            retVal.results[item.test] = (
                item.legacy_status[i].passes
                ==
                item.legacy_status[i].total
                )
                ?
                "PASS"
                :
                "FAIL";

       })
       return retVal;
    });
}();

/*
  Before we start, re-attach
  data-tests meta-information in a convenient
  array form where we can
  refer to it later because respec will
  remove it...
*/
async function initReport() {
    // respec uses data-tests attributes but that's not very convenient
    // to update. Spec authors should not use them inside the spec content.
    // Instead, the data-tests attributes are expected to be loaded from
    // the data-tests.js file, which is automatically generated from the
    // actuall WPT test metadata.
    // FIXME: Should respec's id for header be generated here?
    if (document.querySelector('[data-tests]'))
        throw "Element with data-tests attribute found!";
    for (var section in dataTests) {
        var sectionElement = document.getElementById(section);
        var div;
        if (!sectionElement)
            throw `Cannot find section of id '${section}'.`
        if (section == 'implementation-report') {
            div = sectionElement;
        } else {
            div = document.createElement("div");
            var header = sectionElement.firstElementChild;
            if (!header)
                throw `Cannot find header for section ${section}`;
            header.parentNode.insertBefore(div, header.nextElementSibling);
        }
        div.dataset.tests = dataTests[section];
        div.__tests = dataTests[section].split(',');
    }
}

// this is using the technique and styles adapted from annotation.js
async function loadWebPlaformTestsResults() {
    let wptData = await wptDataPromise;
    let ENGINE_LOGOS = {
        'firefox': "https://test.csswg.org/harness/img/gecko.svg",
        'safari': "https://test.csswg.org/harness/img/webkit.svg",
        'edge': "https://test.csswg.org/harness/img/edge.svg",
        'chrome': "https://test.csswg.org/harness/img/blink.svg",
    };

    document.querySelectorAll('.respec-tests-details').forEach(el => {
        let summary = {};
        let annotationEl = el.parentElement;
        annotationEl.classList.add('annotation');
        annotationEl.classList.add('removeOnSave');

        annotationEl.__tests.forEach(key => {
            wptData.forEach(rec => {
                summary[rec.engine] = summary[rec.engine] || { pass: 0, fail: 0, untested: 0 };
                // respec refers uses path with respect to the mathml/ folder
                // while WPT uses the full path. So we need to tweak the key.
                var path;
                if (key.substring(0, 2) == "..") {
                    // Tests outside the /mathml/ folder (e.g. CSS ones)
                    path = key.substring(2);
                } else {
                    // Tests inside the /mathml/ folder.
                    path = `/mathml/${key}`;
                }
                if (!rec.results.hasOwnProperty(path)) {
                    summary[rec.engine].untested++;
                } else if (rec.results[path] === "PASS") {
                    summary[rec.engine].pass++;
                } else {
                    summary[rec.engine].fail++;
                }
            })
        })

        let source = `
            <div class="engines">
              ${wptData.map(engineData => {
                let engine = engineData.engine;
                let passing = summary[engine].pass;
                let failing = summary[engine].fail;
                let untested = summary[engine].untested;
                let total = passing + failing + untested;
                let status = '';

                switch (Math.round((passing / total) * 10.0)) {
                  case 10:
                  case 9: status = 'almost-pass';  break;
                  case 8: status = 'slightly-buggy'; break;
                  case 7: status = 'buggy'; break;
                  case 6: status = 'very-buggy'; break;
                  case 5: status = 'fail'; break;
                  default: status = 'epic-fail'; break;
                }
                // this also had data-needcount but...
                return `<span title="${passing} pass, ${failing} fail, ${untested} untested" tabindex="0" data-enginename="_${engine}" data-passcount="${passing}" data-failcount="${failing}" data-untestedcount="${untested}" class="${engine} ${status} active major"><img src="${ENGINE_LOGOS[engine]}" alt="${engine}"></span>`
              })}
            </div>`;

        let frag = document.createRange().createContextualFragment(source);
        annotationEl.appendChild(frag);


    });
    document.getElementById("implementation-report").insertAdjacentHTML("beforeend", `<div style="margin-left: 2em; margin-right: 2em"><a href="${respecConfig.implementationReportURI}">Implementation Report</a></div>`);
}
