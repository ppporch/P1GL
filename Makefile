AM1 ?= am1
PDP1_ROOT ?= /opt/pidp1-mods
CC ?= cc
LIBS := $(wildcard src/*.am1 src/*.ah src/*.ac)
DEMOS := frame_demo line_demo circle_demo gplot_demo

.PHONY: all test test-host test-type340
all: $(addprefix build/,$(addsuffix .rim,$(DEMOS))) build/calibrate.rim

build:
	mkdir -p build

build/%.rim: examples/%.am1 $(LIBS) | build
	cd build && $(AM1) -d ../$<

build/calibrate.rim: src/calibrate.am1 $(LIBS) | build
	cd build && $(AM1) -d ../$<

build/type340_runner: tools/plot_runner.c $(PDP1_ROOT)/src/pdp1/pdp1.o | build
	$(CC) -O2 -DP1GL_TYPE340_TEST -I$(PDP1_ROOT)/src/pdp1 -I$(PDP1_ROOT)/src/common -o $@ $< $(PDP1_ROOT)/src/pdp1/pdp1.o -lm

test-host:
	python3 tools/run_host_tests.py

test-type340: build/type340_runner
	AM1="$(AM1)" python3 tools/check_type340.py

test: all test-host test-type340
