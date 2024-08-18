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

## Setting Up Dependencies

### 1. **Install C++ Libs**
(E.g. for Ubuntu/Debian):

#### Install glog, gtest:
```bash
sudo apt update
sudo apt install libgtest-dev
sudo apt install libgoogle-glog-dev
```

`gtest` needs to be built manually:

```bash
sudo apt install cmake
cd /usr/src/gtest
sudo cmake CMakeLists.txt
sudo make
sudo cp *.a /usr/lib
```

### 2. **Setup Gradle**
(E.g. for Ubuntu/Debian):
```bash
sudo apt update
sudo apt install openjdk-11-jdk
sudo apt install gradle
```

### 3. **Setup venv and activate**:
```bash
[[ ! -d venv ]] && mkdir venv
cd venv
venvname=polyg-$(date +"%Y%m%b%d" | awk '{print tolower($1)}')
virtualenv $venvname
source $venvname/bin/activate
```

### 4. **Install Python Dependencies**:
```bash
pip install -r requirements.txt
```

## Building and Running

### 5. **Build**:
```bash
gradle build
```
or
```bash
make
```

### 6. **Run**:
```bash
python build-out/pycache/polyglot_codestats.pyc 'src-*' 'bin'
```

Replace `'src-*'` with your preferred source directory.

### 7. **Cleanup**:
```bash
make clean
```

## Or (instead 5. .. 7.) run the script to execute all end-to-end:
```bash
./bin/polyglot-codestats-e2e.sh
```

## Project Purpose

The purpose of this project is to demonstrate cross-programming language interaction and integration
with multiple Language Model APIs by creating a code statistics tool. It uses Python as the main
driver, Kotlin for folder scanning, and C++ for file analysis. The project showcases how different
languages and APIs can work together to perform a complex task efficiently.
