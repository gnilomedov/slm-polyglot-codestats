# Polyglot CodeStats

Polyglot CodeStats is a cross-language project that demonstrates interaction between Python, C++, and Kotlin to analyze code statistics across multiple source directories.

## Building and Running

0. Setup venv and activate:
```bash
[[ ! -d venv ]] && mkdir venv
cd venv
venvname=polyg-$(date +"%Y%m%b%d" | awk '{print tolower($1)}')
virtualenv $venvname
source $venvname/bin/activate
```

1. Install Env:
```bash
pip install -r requirements.txt
```

2. Build:
```bash
make
```

3. Run:
```bash
python build-out/pycache/polyglot_codestats.pyc 'src-*' 'bin'
```

Instead of `src-*` use your favorite source dir.

4. Cleanup:
```bash
make clean
```

Or run script to execute all end to end (except for env setup):
```bash
./bin/polyglot-codestats-e2e.sh
```

## Project Purpose

The purpose of this project is to demonstrate cross-programming language interaction by creating a code statistics tool. It uses Python as the main driver, Kotlin for folder scanning, and C++ for file analysis. The project showcases how different languages can work together to perform a complex task efficiently.
