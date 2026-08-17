PDFLATEX ?= pdflatex
TEXFLAGS := -interaction=nonstopmode -halt-on-error -file-line-error
BUILD_DIR := .build
RESUMES := dhruv_resume.pdf edu_resume.pdf

.PHONY: all resumes

all: resumes

resumes: $(RESUMES)

$(BUILD_DIR):
	mkdir -p $@

%.pdf: %.tex altacv.cls | $(BUILD_DIR)
	$(PDFLATEX) $(TEXFLAGS) -output-directory=$(BUILD_DIR) $<
	$(PDFLATEX) $(TEXFLAGS) -output-directory=$(BUILD_DIR) $<
	cp $(BUILD_DIR)/$@ $@
