formula.svg: formula.dvi
	dvisvgm --bbox=min --no-fonts formula.dvi

formula.dvi: formula.tex
	tex formula.tex && rm formula.log
