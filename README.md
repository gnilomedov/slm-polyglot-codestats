# LLM Polyglot CodeStats

LLM Polyglot CodeStats is a cross-language project that demonstrates interaction between
Python, C++, and Kotlin to analyze code statistics across multiple source directories.
Here, "Polyglot" highlights both the support for various programming languages and the integration
with multiple Language Model APIs (LLMs).

## Getting the Code

0. Clone the repository:
```bash
git clone https://github.com/gnilomedov/llm-polyglot-codestats.git
cd llm-polyglot-codestats
```

## Building and Running

1. **Setup Gradle** (E.g. for Ubuntu/Debian):
```bash
sudo apt update
sudo apt install openjdk-11-jdk
sudo apt install gradle
```

2. **Setup venv and activate**:
```bash
[[ ! -d venv ]] && mkdir venv
cd venv
venvname=polyg-$(date +"%Y%m%b%d" | awk '{print tolower($1)}')
virtualenv $venvname
source $venvname/bin/activate
```

3. **Install Env**:
```bash
pip install -r requirements.txt
```

4. **Build**:
```bash
make
```

5. **Run**:
```bash
python build-out/pycache/polyglot_codestats.pyc 'src-*' 'bin'
```

Instead of `src-*`, use your preferred source directory.

6. **Cleanup**:
```bash
make clean
```

Or run the script to execute all end-to-end (except for env setup):
```bash
./bin/polyglot-codestats-e2e.sh
```

## Project Purpose

The purpose of this project is to demonstrate cross-programming language interaction and integration
with multiple Language Model APIs by creating a code statistics tool. It uses Python as the main
driver, Kotlin for folder scanning, and C++ for file analysis. The project showcases how different
languages and APIs can work together to perform a complex task efficiently.
