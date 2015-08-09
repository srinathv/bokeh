from bokeh.io import save
from bokeh.plotting import figure, vplot

import pytest
pytestmark = pytest.mark.integration


def make_plot(tools=''):
    plot = figure(height=800, width=1000, tools=tools)
    plot.circle(x=[1, 2], y=[1, 2], radius=0.5)
    return plot


def test_scrolling_on_long_page_of_plots(bokeh_file_test, selenium):
    plots = [make_plot() for _ in range(0, 10)]
    save(vplot(*plots))
    selenium.get(bokeh_file_test)
    plotted_plots = selenium.find_elements_by_css_selector('.bk-plot')
    assert len(plotted_plots) == 10
