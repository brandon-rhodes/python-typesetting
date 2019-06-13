all: formula.svg logo.svg

formula.svg: formula.dvi
	dvisvgm --bbox=min --no-fonts formula.dvi

formula.dvi: formula.tex
	tex formula.tex && rm formula.log

logo.svg: logo.dvi
	dvisvgm --bbox=min --no-fonts logo.dvi

logo.dvi: logo.tex
	tex logo.tex && rm logo.log
