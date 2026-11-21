AM1 ?= am1
PDP1_ROOT ?= /opt/pidp1-mods
CC ?= cc
LIBS := $(wildcard src/*.am1 src/*.ah src/*.ac)
DEMOS := frame_demo line_demo circle_demo gplot_demo vector_text_demo retained_demo viewport_demo transform_demo arc_demo

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

test: all test-host test-type340 test-vector-text test-vector-sink


build/vector_text_demo.rim: examples/vector_text_demo.am1 $(LIBS) generated/vector-font.ac | build
	cd build && $(AM1) -d ../$<

generated/vector-font.ac: fonts/futural.jhf tools/generate_vfont.py
	python3 tools/generate_vfont.py

.PHONY: test-vector-text
test-vector-text: build/type340_runner generated/vector-font.ac
	AM1="$(AM1)" python3 tools/check_vector_text.py


.PHONY: test-vector-sink
test-vector-sink: build/type340_runner
	AM1="$(AM1)" python3 tools/check_vector_sink.py

.PHONY: test-retained
test: test-retained
test-retained: build/type340_runner
	AM1="$(AM1)" python3 tools/check_retained.py

.PHONY: test-viewport
test: test-viewport
test-viewport: build/type340_runner
	AM1="$(AM1)" python3 tools/check_viewport.py

build/transform_demo.rim build/arc_demo.rim: generated/transform-sine.ac

generated/transform-sine.ac: tools/generate_transform_sine.py
	python3 tools/generate_transform_sine.py

.PHONY: test-transform
test: test-transform
test-transform: build/type340_runner generated/transform-sine.ac
	AM1="$(AM1)" python3 tools/check_transform.py

.PHONY: test-arcs
test: test-arcs
test-arcs: build/type340_runner generated/transform-sine.ac
	AM1="$(AM1)" python3 tools/check_arcs.py

PENMENU_DEPS := $(wildcard $(PDP1_ROOT)/Am1Includes/PENMENU/*.ac \
                           $(PDP1_ROOT)/Am1Includes/PENMENU/*.ah \
                           $(PDP1_ROOT)/Am1Includes/TYPE340/*.ah \
                           $(PDP1_ROOT)/Am1Includes/memory.ah)
build/penmenu_demo.rim: generated/transform-sine.ac $(PENMENU_DEPS)

.PHONY: test-penmenu
ifneq ($(wildcard $(PDP1_ROOT)/Am1Includes/PENMENU/penmenu.ac),)
all: build/penmenu_demo.rim
test: test-penmenu
endif
test-penmenu: build/type340_runner generated/transform-sine.ac
	AM1="$(AM1)" python3 tools/check_penmenu.py
