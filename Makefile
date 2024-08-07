KOTLIN = kotlinc
KOTLIN_FLAGS = -include-runtime

CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall -fPIC

PYTHON = python3.10


OUT_DIR = build-out


.PHONY: all clean

all: $(OUT_DIR)/polyglot.jar $(OUT_DIR)/polyglot.so $(OUT_DIR)/polyglot_pyc

$(OUT_DIR):
	mkdir -p $(OUT_DIR)

$(OUT_DIR)/polyglot.so: src-cpp/*.cpp src-cpp/*.h
	$(CXX) $(CXXFLAGS) -shared -o $@ src-cpp/*.cpp `python3-config --includes --ldflags` -l$(PYTHON)

$(OUT_DIR)/polyglot.jar: $(OUT_DIR) src-kt
	$(KOTLIN) $(KOTLIN_FLAGS) -d $@ src-kt

$(OUT_DIR)/polyglot_pyc: src-py
	python -m compileall -b src-py
	@find src-py -type f -name '*.pyc' ! -path '*/__pycache__/*' | \
	while read pyc_file ; do \
		dest_dir=$$(echo "$$pyc_file" | sed -e "s|src-py/\(.*\)|\1|") ; \
		dest_dir=$$(dirname "$$dest_dir") ; \
		dest_dir=$(OUT_DIR)/polyglot_pyc/$$dest_dir ; \
		if [ ! -d "$$dest_dir" ] ; then \
			echo "\033[0;32mmkdir\033[0m $$dest_dir/..." ; \
			mkdir -p "$$dest_dir" ; \
		fi ; \
		dest_name=$$(basename $$pyc_file | sed -e 's|.cpython-3[0-9]\{2\}.pyc|.pyc|') ; \
		mv "$$pyc_file" $$dest_dir/$$dest_name ; \
	done

clean:
	rm -rf $(OUT_DIR)
