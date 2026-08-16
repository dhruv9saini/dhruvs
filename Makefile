TYPST ?= nix run --impure nixpkgs\#typst --

.PHONY: all resumes

all: resumes

resumes:
	$(TYPST) compile --root . dhruv_resume.typ dhruv_resume.pdf
	$(TYPST) compile --root . edu_resume.typ edu_resume.pdf
