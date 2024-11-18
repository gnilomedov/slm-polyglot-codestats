# SLM Polyglot CodeStats

The **SLM Polyglot CodeStats** project demonstrates cross-language interaction and integration with
multiple Language Model APIs (LLMs) to analyze code statistics across various source directories.
It uses Python as the main driver, Kotlin for folder scanning, and C++ for file analysis,
showcasing how different programming languages and APIs can collaborate to efficiently perform
complex tasks.

In addition to generating code statistics, the project also trains and fine-tunes code generation
models:

- **Pico Code Composer**: A basic LSTM model trained from scratch on the provided codebase,
simulating the intelligence of a honeybee 💻🐝. This model serves as an introduction to training
simple neural networks for code generation.

- **Nano Code Composer**: A fine-tuned version of the pre-trained `microsoft/CodeGPT-small-py`
model, designed to perform at the intellectual level of a rat 💻🐀. This demonstrates how existing
models can be customized to handle specific tasks more effectively.

These features make the project a comprehensive tool for understanding cross-language programming,
SLM integration, and code generation using AI.

## Getting the Code

### 0. Clone the repository:
```bash
git clone https://github.com/gnilomedov/slm-polyglot-codestats
cd slm-polyglot-codestats
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
