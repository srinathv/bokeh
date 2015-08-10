from bokeh.io import save
from bokeh.plotting import figure
from bokeh.models import Plot, Range1d, ColumnDataSource, Rect, WheelZoomTool
from selenium.webdriver.common.action_chains import ActionChains

import pytest
pytestmark = pytest.mark.integration

import time
SLEEP = 1


def make_plot_2(tools=''):
    plot = Plot(plot_height=800, plot_width=1000, x_range=Range1d(0.5, 2.5), y_range=Range1d(0.5, 2.5), min_border=0)
    source = ColumnDataSource(dict(x=[1, 2, 1, 2], y=[1, 1, 2, 2]))
    rect = Rect(x='x', y='y', width=1, height=1, line_color='black', line_width=1)
    plot.add_glyph(source, rect)
    plot.add_tools(WheelZoomTool())
    return plot


def make_plot(tools=''):
    plot = figure(height=800, width=1000, tools=tools)
    plot.rect(x=[1, 2, 1, 2], y=[1, 1, 2, 2], width=1, height=1, line_color='black', line_width=1)
    return plot


def click_glyph_at_position(selenium, element, x, y):
    actions = ActionChains(selenium)
    actions.move_to_element_with_offset(element, x, y)
    actions.click_and_hold()  # Works on ff & chrome
    # actions.click() - Works on chrome but not ff (cannot release a button when no button pressed)
    actions.release()
    actions.perform()


def test_hovering_and_clicking_on_rectangles(output_file_url, selenium):
    save(make_plot('tap, hover'))
    selenium.get(output_file_url)

    plotted_plot = selenium.find_element_by_css_selector('.bk-plot')
    # Click top left
    click_glyph_at_position(selenium, plotted_plot, 300, 300)
    time.sleep(SLEEP)
    # Click top right
    click_glyph_at_position(selenium, plotted_plot, 600, 300)
    time.sleep(SLEEP)
    # Click bottom left
    click_glyph_at_position(selenium, plotted_plot, 300, 600)
    time.sleep(SLEEP)
    # Click bottom right
    click_glyph_at_position(selenium, plotted_plot, 600, 600)
    time.sleep(SLEEP)

    assert True  # Would be cool if you could assert something about the plot now.


def test_wheel_zoom(output_file_url, selenium):
    save(make_plot_2())  # Use plot_2 - event very edge of canvas-events has scroll
    selenium.get(output_file_url)
    code = """
        var e = Bokeh.$.Event( "wheel", { deltaY: 100, deltaX: 100 } );
        Bokeh.$('.bk-canvas-events').trigger(e)
    """
    selenium.execute_script(code)
    time.sleep(SLEEP)
    assert False  # Doesn't work, causes whole plot to go white


def test_panning(output_file_url, selenium):
    save(make_plot('hover, pan'))

    # Panning one
    selenium.get(output_file_url)
    plotted_plot = selenium.find_element_by_css_selector('.bk-plot')
    actions = ActionChains(selenium)
    actions.drag_and_drop_by_offset(plotted_plot, 200, 200)
    actions.perform()

    time.sleep(SLEEP)

    # Panning two
    selenium.get(output_file_url)
    plotted_plot = selenium.find_element_by_css_selector('.bk-plot')
    actions = ActionChains(selenium)
    actions.move_to_element_with_offset(plotted_plot, 300, 300)
    actions.click_and_hold()
    actions.move_by_offset(50, 50)
    actions.release()
    actions.perform()

    time.sleep(SLEEP)

    assert True  # Works on FF not chrome - chrome gives white screen
