"""texlib.wrap

Implements TeX's algorithm for breaking paragraphs into lines.

This module provides a straightforward implementation of the algorithm
used by TeX to format paragraphs.  The algorithm uses dynamic
programming to find a globally optimal division into lines, enabling
it to produce more attractive results than a first-fit or best-fit
algorithm can.  For a full description, see the reference.

The module provides the ObjectList class, which is a list of Box,
Glue, and Penalty instances.  The elements making up a paragraph of
text should be assembled into a single ObjectList.  Boxes represent
characters of type, and their only attribute is width.  Glue
represents a space of variable size; in addition to a preferred width,
glue can also stretch and shrink, to an amount that's specified by the
user.  Penalties are used to encourage or discourage breaking a line
at a given point.  Positive values discourage line breaks at a given
point, and a value of INFINITY forbids breaking the line at the
penalty.  Negative penalty values encourage line breaks at a given
point, and a value of -INFINITY forces a line break at a particular
point.

The compute_breakpoints() method of ObjectList returns a list of
integers containing the indexes at which the paragraph should be
broken.  If you're setting the text to be ragged-right (or
ragged-left, I suppose), then simply loop over the text and insert
breaks at the appropriate points.  For full justification, you'll have
to loop over each line's contents, calculate its adjustment ratio by
calling compute_adjustment_ratio(), and for each bit of glue, call its
compute_width() method to figure out how long this dab of glue should
be.

Reference:
    "Breaking Paragraphs into Lines", D.E. Knuth and M.F. Plass,
    chapter 3 of _Digital Typography_, CSLI Lecture Notes #78.
"""

__version__ = "1.01"

INFINITY = 1000

# Three classes defining the three different types of object that
# can go into an ObjectList.

class Box:
    """A fixed-width slug of text or other content."""

    def __init__(self, width, content=None):
        self.content = content
        self.width = width
        self.stretch = self.shrink = 0
        self.penalty = 0
        self.flagged = 0

    def is_glue(self):         return 0
    def is_box(self):          return 1
    def is_penalty(self):      return 0
    def is_forced_break(self): return 0

class Glue:
    """Class representing a bit of glue.  Glue has a preferred width,
    but it can stretch up to an additional distance, and can shrink
    by a certain amount.  Line breaks can be placed at any point where
    glue immediately follows a box.
    """

    def __init__(self, width, stretch, shrink):
        self.width, self.stretch, self.shrink = width, stretch, shrink

    def compute_width(self, r):
        """Return how long this glue should be, for the given adjustment
        ratio r."""

        if r < 0: return self.width + r*self.shrink
        else:     return self.width + r*self.stretch

    def is_glue(self):         return 1
    def is_box(self):          return 0
    def is_penalty(self):      return 0
    def is_forced_break(self): return 0

class Penalty:
    """Class representing a penalty.  Negative penalty values
    encourage line breaks at a given point, and positive values
    discourage breaks.  A value of INFINITY either absolutely requires
    or forbids a break.  Penalties have a width of zero unless a break
    is taken at the penalty point, at which point the value of the
    penalty's 'width' attribute is used.

    """

    def __init__(self, width, penalty, flagged = 0):
        self.width = width
        self.penalty = penalty
        self.flagged = flagged
        self.stretch = self.shrink = 0

    def is_glue(self):         return 0
    def is_box(self):          return 0
    def is_penalty(self):      return 1
    def is_forced_break(self):
        return (self.penalty == -INFINITY)


class _BreakNode:
    "Internal class representing an active breakpoint."

    def __init__(self, position, line, fitness_class,
                 totalwidth, totalstretch, totalshrink,
                 demerits, previous = None):
        self.position, self.line = position, line
        self.fitness_class = fitness_class
        self.totalwidth, self.totalstretch = totalwidth, totalstretch
        self.totalshrink, self.demerits = totalshrink, demerits
        self.previous = previous

    def __repr__(self):
        return '<_BreakNode at %i>' % self.position

class ObjectList(list):

    """Class representing a list of Box, Glue, and Penalty objects.
    Supports the same methods as regular Python lists.
    """

    # Set this to 1 to trace the execution of the algorithm.
    debug = 0

    def add_closing_penalty (self):
        "Add the standard glue and penalty for the end of a paragraph"
        self.append( Penalty( 0, INFINITY, 0 ) )
        self.append( Glue(0, INFINITY, 0) )
        self.append( Penalty(0, -INFINITY, 1) )

    def is_feasible_breakpoint(self, i):
        "Return true if position 'i' is a feasible breakpoint."

        box = self[i]
        if box.is_penalty() and box.penalty < INFINITY:
            return 1
        elif i>0 and box.is_glue() and self[i-1].is_box():
            return 1
        else:
            return 0

    def is_forced_break(self, i):
        "Return true if position 'i' is a forced breakpoint."

        box = self[i]
        if box.is_penalty() and box.penalty == -INFINITY:
            return 1
        else:
            return 0

    def measure_width(self, pos1, pos2):
        "Add up the widths between positions 1 and 2"

        return self.sum_width[pos2] - self.sum_width[pos1]

    def measure_stretch(self, pos1, pos2):
        "Add up the stretch between positions 1 and 2"

        return self.sum_stretch[pos2] - self.sum_stretch[pos1]

    def measure_shrink(self, pos1, pos2):
        "Add up the shrink between positions 1 and 2"

        return self.sum_shrink[pos2] - self.sum_shrink[pos1]

    def compute_adjustment_ratio(self, pos1, pos2, line, line_lengths):
        "Compute adjustment ratio for the line between pos1 and pos2"
        length = self.measure_width(pos1, pos2)
        if self[pos2].is_penalty(): length += self[pos2].width
        if self.debug:
            print('\tline length=', length)

        # Get the length of the current line; if the line_lengths list
        # is too short, the last value is always used for subsequent
        # lines.

        if line < len(line_lengths):
            available_length = line_lengths[line]
        else:
            available_length = line_lengths[-1]

        # Compute how much the contents of the line would have to be
        # stretched or shrunk to fit into the available space.
        if length < available_length:
            y = self.measure_stretch(pos1, pos2)
            if self.debug:
                print ('\tLine too short: shortfall = %i, stretch = %i'
                       % (available_length - length, y) )
            if y > 0:
                r = (available_length - length) / float(y)
            else:
                r = INFINITY

        elif length > available_length:
            z = self.measure_shrink(pos1, pos2)
            if self.debug:
                print ('\tLine too long: extra = %s, shrink = %s' %
                       (available_length - length, z) )
            if z > 0:
                r = (available_length - length) / float(z)
            else:
                r = INFINITY
        else:
            # Exactly the right length!
            r = 0

        return r


    def add_active_nodes(self, active_nodes, nodes):
        """Add nodes to the active node list.
        The nodes are added so that the list of active nodes is always
        sorted by line number, and so that the set of (position, line,
        fitness_class) tuples has no repeated values.
        """

        for node in nodes:
            index = 0

            # Find the first index at which the active node's line number
            # is equal to or greater than the line for 'node'.  This gives
            # us the insertion point.
            while (index < len(active_nodes) and
                   active_nodes[index].line < node.line):
                index = index + 1

            insert_index = index

            # Check if there's a node with the same line number and
            # position and fitness.  This lets us ensure that the list of
            # active nodes always has unique (line, position, fitness)
            # values.
            while (index < len(active_nodes) and
                   active_nodes[index].line == node.line):
                if (active_nodes[index].fitness_class == node.fitness_class and
                    active_nodes[index].position == node.position):
                    # A match, so just return without adding the node
                    return

                index = index + 1

            active_nodes.insert(insert_index, node)

    def compute_breakpoints(self,
                            line_lengths,
                            looseness = 0,  # q in the paper
                            tolerance = 1,  # rho in the paper
                            fitness_demerit = 100, # gamma (XXX?) in the paper
                            flagged_demerit = 100, # alpha in the paper
                            ):
        """Compute a list of optimal breakpoints for the paragraph
        represented by this ObjectList, returning them as a list of
        integers, each one the index of a breakpoint.

        line_lengths : a list of integers giving the lengths of each
                       line.  The last element of the list is reused
                       for subsequent lines.
        looseness : An integer value. If it's positive, the paragraph
                   will be set to take that many lines more than the
                   optimum value.   If it's negative, the paragraph is
                   set as tightly as possible.  Defaults to zero,
                   meaning the optimal length for the paragraph.
        tolerance : the maximum adjustment ratio allowed for a line.
                    Defaults to 1.
        fitness_demerit : additional value added to the demerit score
                          when two consecutive lines are in different
                          fitness classes.
        flagged_demerit : additional value added to the demerit score
                          when breaking at the second of two flagged
                          penalties.
        """

        m = len(self)
        if m == 0: return []            # No text, so no breaks

        # Precompute lists containing the numeric values for each box.
        # The variable names follow those in Knuth's description.
        w = [0]*m ;
        y = [0]*m ; z = [0]*m
        p = [0]*m ; f = [0]*m
        for i in range(m):
            box = self[i]
            w[i] = box.width
            if box.is_glue():
                y[i] = box.stretch
                z[i] = box.shrink
            elif box.is_penalty():
                p[i] = box.penalty
                f[i] = box.flagged

        # Precompute the running sums of width, stretch, and shrink
        # (W,Y,Z in the original paper).  These make it easy to measure the
        # width/stretch/shrink between two indexes; just compute
        # sum_*[pos2] - sum_*[pos1].  Note that sum_*[i] is the total
        # up to but not including the box at position i.

        self.sum_width = [0] * m
        self.sum_stretch = [0] * m
        self.sum_shrink = [0] * m
        width_sum = stretch_sum = shrink_sum = 0
        for i in range(m):
            self.sum_width[i] = width_sum
            self.sum_stretch[i] = stretch_sum
            self.sum_shrink[i] = shrink_sum

            box = self[i]
            if not box.is_penalty():
                width_sum   = width_sum + box.width
                stretch_sum = stretch_sum + box.stretch
                shrink_sum  = shrink_sum + box.shrink

        # Initialize list of active nodes to a single break at the
        # beginning of the text.
        A = _BreakNode(position=0, line=0, fitness_class = 1,
                 totalwidth = 0, totalstretch = 0,
                 totalshrink = 0, demerits = 0)
        active_nodes = [A]

        if self.debug:
            print('Looping over %i box objects' % m)

        for i in range(m):
            B = self[i]
            #print(B, getattr(B, 'content', None))
            # Determine if this box is a feasible breakpoint and
            # perform the main loop if it is.
            if not self.is_feasible_breakpoint(i):
                continue
            if self.debug:
                print('Feasible breakpoint at %i:' % i)
                print('\tCurrent active node list:', active_nodes)

            if self.debug:
                # Print the list of active nodes, sorting them
                # so they can be visually checked for uniqueness.
                def key_f(n):
                    return (n.line, n.position, n.fitness_class)
                active_nodes.sort(key=key_f)
                for A in active_nodes:
                    print(A.position, A.line, A.fitness_class)
                print ; print

            # Loop over the list of active nodes, and compute the fitness
            # of the line formed by breaking at A and B.  The resulting
            breaks = []                 # List of feasible breaks
            for A in active_nodes[:]:
                r = self.compute_adjustment_ratio(A.position, i, A.line, line_lengths)
                if self.debug:
                    print('\tr=', r)
                    print('\tline=', A.line)

                # #print(r)
                # if r<-1 or B.is_forced_break():
                #     #continue
                #     # Deactivate node A
                #     if len(active_nodes) == 1:
                #         if self.debug:
                #             print "Can't remove last node!"
                #             # XXX how should this be handled?
                #             # Raise an exception?
                #     else:
                #         if self.debug:
                #             print '\tRemoving node', A
                #         active_nodes.remove(A)

                # TODO: eliminate one of these?
                assert B.is_forced_break() == self.is_forced_break(i)

                if r < -1 or B.is_forced_break():
                    active_nodes.remove(A)

                tolerable = (-1 <= r <= tolerance)
                # print r, tolerable
                if not tolerable:
                    continue

                # Compute demerits and fitness class
                if p[i] >= 0:
                    demerits = (1 + 100 * abs(r)**3 + p[i]) ** 3
                elif self.is_forced_break(i):
                    demerits = (1 + 100 * abs(r)**3) ** 2 - p[i]**2
                else:
                    demerits = (1 + 100 * abs(r)**3) ** 2
                demerits += flagged_demerit * f[i] * f[A.position]

                # Figure out the fitness class of this line (tight, loose,
                # very tight or very loose).
                if   r < -.5: fitness_class = 0
                elif r <= .5: fitness_class = 1
                elif r <= 1:  fitness_class = 2
                else:         fitness_class = 3

                # If two consecutive lines are in very
                # different fitness classes, add to the
                # demerit score for this break.
                if abs(fitness_class - A.fitness_class) > 1:
                    demerits += fitness_demerit

                if self.debug:
                    print('\tDemerits=', demerits)
                    print('\tFitness class=', fitness_class)

                # Record a feasible break from A to B
                brk = _BreakNode(position = i, line = A.line + 1,
                              fitness_class = fitness_class,
                              totalwidth = self.sum_width[i],
                              totalstretch = self.sum_stretch[i],
                              totalshrink = self.sum_shrink[i],
                              demerits = demerits,
                              previous = A)
                breaks.append(brk)
                # print '=========='
                if self.debug:
                    print('\tRecording feasible break', B)
                    print('\t\tDemerits=', demerits)
                    print('\t\tFitness class=', fitness_class)

                #print(r)

                    # #continue
                    # # Deactivate node A
                    # if len(active_nodes) == 1:
                    #     if self.debug:
                    #         print "Can't remove last node!"
                    #         # XXX how should this be handled?
                    #         # Raise an exception?
                    # else:
                    #     if self.debug:
                    #         print '\tRemoving node', A
                    #     active_nodes.remove(A)

            # end for A in active_nodes
            if breaks:
                if self.debug:
                    print('List of breaks at ', i, ':', breaks)
                self.add_active_nodes(active_nodes, breaks)

            if not active_nodes:
                raise RuntimeError('no solutions for this paragraph within a'
                                   ' bound of tolerance={}'.format(tolerance))

        # end for i in range(m)

        if self.debug:
            print('Main loop completed')
            print('Active nodes=', active_nodes)

        # Find the active node with the lowest number of demerits.
        least_demerits = min(A.demerits for A in active_nodes)
        for A in active_nodes:
            if A.demerits == least_demerits:
                break
        # L = map(lambda A: (A.demerits, A), active_nodes)
        # L.sort()
        # _, A = L[0]

        if looseness != 0:
            # The search for the appropriate active node is a bit more
            # complicated; we look for a node with a paragraph length
            # that's as close as possible to (A.line+looseness), and
            # with the minimum number of demerits.

            best = 0
            d = INFINITY
            for br in active_nodes:
                delta = br.line - A.line
                # The two branches of this 'if' statement
                # are for handling values of looseness that are
                # either positive or negative.
                if ((looseness<= delta < best) or
                    (best<delta<looseness) ):
                    d = br.demerits
                    b = br

                elif delta == best and br.demerits < d:
                    # This break is of the same length, but has fewer
                    # demerits and hence is a more attractive one.
                    d = br.demerits
                    b = br

            A = b

        # Use the chosen node A to determine the optimum breakpoints,
        # and return the resulting list of breakpoints.
        breaks = []
        while A is not None:
            breaks.append( A.position )
            A = A.previous
        breaks.reverse()
        return breaks
