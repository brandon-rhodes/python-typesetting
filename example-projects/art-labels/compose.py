from bookbinding import document as bb

story = [
    bb.Paragraph(
        text=(
"""
In olden times when wishing still helped one, there lived a king
whose daughters were all beautiful, but the youngest was so beautiful
that the sun itself, which has seen so much, was astonished whenever
it shone in her face.  Close by the king's castle lay a great dark
forest, and under an old lime-tree in the forest was a well, and when
the day was very warm, the king's child went out into the forest and
sat down by the side of the cool fountain, and when she was bored she
took a golden ball, and threw it up on high and caught it, and this
ball was her favorite plaything.
"""
        ),
        style=None,
    ),
    bb.Paragraph(
        text=(
            "Vivamus fermentum semper porta. Nunc diam velit, "
            "adipiscing ut tristique vitae, sagittis vel odio. "
            "Maecenas convallis ullamcorper ultricies. Curabitur "
            "ornare, ligula semper consectetur sagittis, nisi diam "
            "iaculis velit, id fringilla sem nunc vel mi. Nam "
            "dictum, odio nec pretium volutpat, arcu ante placerat "
            "erat, non tristique elit urna et turpis. Quisque mi "
            "metus, ornare sit amet fermentum et, tincidunt et orci. "
            "Fusce eget orci a orci congue vestibulum. Ut dolor "
            "diam, elementum et vestibulum eu, porttitor vel elit. "
            "Curabitur venenatis pulvinar tellus gravida ornare. "
            "Sed et erat faucibus nunc euismod ultricies ut id "
            "justo. Nullam cursus suscipit nisi, et ultrices justo "
            "sodales nec. Fusce venenatis facilisis lectus ac "
            "semper. Aliquam at massa ipsum. Quisque bibendum purus "
            "convallis nulla ultrices ultricies. Nullam aliquam, mi "
            "eu aliquam tincidunt, purus velit laoreet tortor, "
            "viverra pretium nisi quam vitae mi. Fusce vel volutpat "
            "elit. Nam sagittis nisi dui."
          ),
          style="indented-paragraph",
    ),
]
doc = bb.Document()
doc.format(story, 72., 72., 72., 72.)
doc.render(doc.pages)
