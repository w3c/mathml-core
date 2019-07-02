#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "usage: $0 /path/to/web-platform-tests"
    exit
fi

MATHML_CORE_URL=https://mathml-refresh.github.io/mathml-core
WPT_DIR=$1
WPT_SUBDIRS="mathml css/css-fonts/math-script-level-and-math-style" # css/css-text/text-transform/math
PYTHON_SCRIPT=wpt-tests-generator.py
EXTRACTED_TESTS=wpt-tests.txt

echo "
#!/usr/bin/python
# This file was automatically generatd from extract.sh. Do not edit.

from __future__ import print_function

tests = {}
def add_test(section, path):
    if not section in tests:
        tests[section] = []
    tests[section].append(path)

def format_tests():
    for section in sorted(tests):
        print('$MATHML_CORE_URL/#%s' % section)
        print('data-tests=\"%s\"\n' % ','.join(sorted(tests[section])))

" > $PYTHON_SCRIPT

for subdir in $WPT_SUBDIRS; do
    echo -n "Extracting tests from $WPT_DIR/$subdir... "
    find $WPT_DIR/$subdir -type f -name '*.html' | xargs grep '<link' | grep 'rel="help"' | grep $MATHML_CORE_URL | sed "s|$WPT_DIR/$subdir/\([^:]\+\):.\+$MATHML_CORE_URL/#\([^\"]\+\)\".\+|add_test('\2','\1')|" >> $PYTHON_SCRIPT
    echo "done"
done

echo "format_tests()" >> $PYTHON_SCRIPT

echo -n "Generating $EXTRACTED_TESTS... "
python $PYTHON_SCRIPT > $EXTRACTED_TESTS
echo "done"
