all: formula.svg logo.svg sample.svg

formula.svg: formula.dvi
	dvisvgm --bbox=min --no-fonts formula.dvi

formula.dvi: formula.tex
	tex formula.tex && rm formula.log

logo.svg: logo.dvi
	dvisvgm --bbox=min --no-fonts logo.dvi

logo.dvi: logo.tex
	tex logo.tex && rm logo.log

sample.svg: sample.dvi
	dvisvgm --bbox=min --no-fonts sample.dvi

sample.dvi: sample.tex
	tex sample.tex && rm sample.log

# Photos:
# for f in ~/Downloads/IMG_20190611_212*.jpg; do convert $f -scale 640 -sharpen 0x0.5 $(basename $f); done
