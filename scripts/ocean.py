from bokeh.volumeslicer.objects import VolumeSlicer, ServerDataSource
from bokeh.widgetobjects import VBox
from bokeh.server.app import bokeh_app
from bokeh.server.utils.plugins import object_page

@bokeh_app.route("/bokeh/ocean/")
@object_page("ocean")
def make_object():
    slicer = VolumeSlicer.create("/defaultuser/oceantemperature/big4.table/big",
                                 [4096, 8192, 94],
                                 x_bounds=[-180,180],
                                 y_bounds=[-90,90],
                                 z_bounds=[2012, 2014])
    return slicer

@bokeh_app.route("/bokeh/timeseries/")
@object_page("timeseries")
def timeseries():
    import numpy as np
    from bokeh.plotting import line, curdoc
    from bokeh.objects import Range1d
    import datetime as dt
    source = ServerDataSource(data_url="/defaultuser/stocks/AAPL.pandas/AAPL.stock", 
                              transform={'resample':'line1d',
                                         'domain' : 'x',
                                         'method' : 'minmax'
                                     },
                              owner_username="defaultuser")
    x_range = Range1d(start=dt.datetime(2004,1,1), end=dt.datetime(2011,1,1))
    plot1 = line('Date_Time', 'Close',
                 x_axis_type = "datetime",
                 color='black', tools="pan,wheel_zoom,box_zoom,reset,previewsave",
                 source=source,
                 plot_height=300,
                 x_range=x_range,
                 title="AAPL", 
                 legend='AAPL')

    source = ServerDataSource(data_url="/defaultuser/stocks/INTC.pandas/INTC.stock",
                              transform={'resample':'line1d',
                                         'domain' : 'x',
                                         'method' : 'minmax'
                                     },
                              owner_username="defaultuser")
    plot2=line('Date_Time', 'Close',
         x_axis_type = "datetime",
         color='black', tools="pan,wheel_zoom,box_zoom,reset,previewsave",
         source=source,
         plot_height=300,
         legend='INTC',
         title="INTC",
         x_range = x_range
     )


    source = ServerDataSource(data_url="/defaultuser/stocks/GOOG.pandas/GOOG.stock", 
                              transform={'resample':'line1d',
                                         'domain' : 'x',
                                         'method' : 'minmax'
                                     },
                              owner_username="defaultuser")
    plot3=line('Date_Time', 'Close',
         x_axis_type = "datetime",
         color='black', tools="pan,wheel_zoom,box_zoom,reset,previewsave",
         source=source,
         plot_height=300,
         title="GOOG",
         x_range = x_range)
    box = VBox()
    box.children.append(plot1)
    box.children.append(plot2)
    box.children.append(plot3)
    return box
        
import crossfilter
import downloads
