"""This is the Bokeh charts interface. It gives you a high level API to build
complex plot is a simple way.

This is the Line class which lets you build your Line charts just
passing the arguments to the Chart class and calling the proper functions.
"""
#-----------------------------------------------------------------------------
# Copyright (c) 2012 - 2014, Continuum Analytics, Inc. All rights reserved.
#
# Powered by the Bokeh Development Team.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import absolute_import

from six import string_types
import numpy as np

from ..utils import cycle_colors
from .._builder import create_and_build
from .._arbuilder import ARBuilder
from ...models import ServerDataSource, GlyphRenderer, Range1d
from ...models.glyphs import Line as LineGlyph
from ...properties import Any

#-----------------------------------------------------------------------------
# Classes and functions
#-----------------------------------------------------------------------------


def Line(blaze_table, index, **kws):
    """ Create a line chart using :class:`LineBuilder <bokeh.charts.builder.line_builder.LineBuilder>` to
    render the geometry from values and index.

    Args:
        values (iterable): iterable 2d representing the data series
            values matrix.
        index (str|1d iterable, optional): can be used to specify a common custom
            index for all data series as an **1d iterable** of any sort that will be used as
            series common index or a **string** that corresponds to the key of the
            mapping to be used as index (and not as data series) if
            area.values is a mapping (like a dict, an OrderedDict
            or a pandas DataFrame)

    In addition the the parameters specific to this chart,
    :ref:`charts_generic_arguments` are also accepted as keyword parameters.

    Returns:
        a new :class:`Chart <bokeh.charts.Chart>`

    Examples:

    .. bokeh-plot::
        :source-position: above

        import numpy as np
        from bokeh.charts import Line, output_file, show

        # (dict, OrderedDict, lists, arrays and DataFrames are valid inputs)
        xyvalues = np.array([[2, 3, 7, 5, 26], [12, 33, 47, 15, 126], [22, 43, 10, 25, 26]])

        line = Line(xyvalues, title="line", legend="top_left", ylabel='Languages')

        output_file('line.html')
        show(line)

    """
    return create_and_build(LineBuilder, blaze_table, index=index, **kws)


class LineBuilder(ARBuilder):
    """This is the Line class and it is in charge of plotting
    Line charts in an easy and intuitive way.
    Essentially, we provide a way to ingest the data, make the proper
    calculations and push the references into a source object.
    We additionally make calculations for the ranges.
    And finally add the needed lines taking the references from the source.
    """

    index = Any(help="""
    An index to be used for all data series as follows:

    - A 1d iterable of any sort that will be used as
        series common index

    - As a string that corresponds to the key of the
        mapping to be used as index (and not as data
        series) if area.values is a mapping (like a dict,
        an OrderedDict or a pandas DataFrame)
    """)


    def _set_sources(self):
        """
        Push the Line data into the ColumnDataSource and calculate the
        proper ranges.
        """
        from blaze import compute
        self._fields = [x for x in self._values.columns if x != self.index]
        maxes = max([compute(self._values[f].max()) for f in self._fields])
        mins = min([compute(self._values[f].min()) for f in self._fields])
        max_idx = compute(self._values[self.index].max())
        min_idx = compute(self._values[self.index].min())
        self._sources = {}
        for f in self._fields:
            self._sources[f] = ServerDataSource(transform={
                'resample': 'line1d',
                'direction': 'x',
                'auto_bounds' : False,
                'method': 'minmax'
            })
            self._sources[f].from_blaze(self._values, local=True)
        print (min_idx, max_idx, mins, maxes)
        self.x_range = Range1d(start=min_idx, end=max_idx)
        self.y_range = Range1d(start=mins, end=maxes)

    def _yield_renderers(self):
        """Use the line glyphs to connect the xy points in the Line.
        Takes reference points from the data loaded at the ColumnDataSource.
        """
        colors = cycle_colors(self._fields, self.palette)
        for idx, f in enumerate(self._fields):
            glyph = LineGlyph(x=self.index, y=f, line_color=colors[idx])
            renderer = GlyphRenderer(data_source=self._sources[f], glyph=glyph)
            self._legends.append((f, [renderer]))
            yield renderer
