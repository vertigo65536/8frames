#!/bin/bash

pip install fuzzywuzzy --user || pip3 install fuzzywuzzy --user
pip install python-Levenshtein --user || pip3 install python-Levenshtein --user
pip install numpy --user || pip3 install numpy --user
pip install tabulate --user || pip3 install tabulate --user
pip install word2number --user || pip3 install word2number --user
pip install google_trans_new --user || pip3 install google_trans_new --user

git clone https://github.com/D4RKONION/fatsfvframedatajson.git
