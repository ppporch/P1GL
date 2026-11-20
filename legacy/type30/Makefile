AM1 ?= am1
PDP1_ROOT ?= /opt/pidp1-mods
CC ?= cc

.PHONY: all test-host test-cpu
all: build/frame_demo.rim build/circle_demo.rim build/line_demo.rim build/calibrate.rim build/calibrate-once.rim build/gplot_demo.rim build/coordinate_sweep.rim

build:
	mkdir -p build

build/calibrate.rim: src/calibrate.am1 src/gplot.am1 | build
	cd build && $(AM1) -d ../src/calibrate.am1

build/calibrate-once.rim: src/calibrate.am1 src/gplot.am1 | build
	cd build && cp ../src/calibrate.am1 calibrate-once.am1 && $(AM1) -d -I../src -DSINGLE_FRAME calibrate-once.am1

build/gplot_demo.rim: examples/gplot_demo.am1 src/gplot.am1 | build
	cd build && $(AM1) -d ../examples/gplot_demo.am1

build/coordinate_sweep.rim: tests/coordinate_sweep.am1 src/gplot.am1 | build
	cd build && $(AM1) -d ../tests/coordinate_sweep.am1

build/plot_runner: tools/plot_runner.c $(PDP1_ROOT)/src/pdp1/pdp1.o | build
	$(CC) -O2 -I$(PDP1_ROOT)/src/pdp1 -I$(PDP1_ROOT)/src/common -o $@ $< $(PDP1_ROOT)/src/pdp1/pdp1.o -lm

test-host:
	python3 tools/run_host_tests.py

test-cpu: all build/plot_runner
	python3 tools/check_cpu.py

build/line_demo.rim: examples/line_demo.am1 src/gline.am1 src/gplot.am1 | build
	cd build && $(AM1) -d ../examples/line_demo.am1

.PHONY: test-lines
test-lines: build/plot_runner
	AM1="$(AM1)" python3 tools/check_lines.py

.PHONY: test
test: test-host test-cpu test-lines test-circles test-frames


build/circle_demo.rim: examples/circle_demo.am1 src/gcircle.am1 src/gplot.am1 | build
	cd build && $(AM1) -d ../examples/circle_demo.am1

.PHONY: test-circles
test-circles: build/plot_runner
	AM1="$(AM1)" python3 tools/check_circles.py


build/frame_demo.rim: examples/frame_demo.am1 src/gframe.am1 src/gtext.am1 src/gplot.am1 src/gcircle.am1 src/gline.am1 $(PDP1_ROOT)/Am1Includes/SYMGEN/ascchars.ac | build
	cd build && $(AM1) -d -I$(PDP1_ROOT)/Am1Includes ../examples/frame_demo.am1

.PHONY: test-frames
test-frames: build/plot_runner
	AM1="$(AM1)" PDP1_ROOT="$(PDP1_ROOT)" python3 tools/check_frames.py
