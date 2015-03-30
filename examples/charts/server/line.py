from collections import OrderedDict
from blaze.server.client import Client
from blaze import Data
from bokeh.charts import ARLine, show, output_server, curdoc, cursession
import pandas as pd
import numpy as np
N = 100000
df = pd.DataFrame({'x' : np.arange(N),
                   'a' : np.random.random(N),
                   'b' : 2 * np.random.random(N)})
output_server("lines_ar")
sess = cursession()
server_loc = sess.data_source('lines', df)
c = Client('http://localhost:5006')
d = sess.blaze_data()
table = d[server_loc]
chart = ARLine(table, index='x')
curdoc().add(chart)
show(chart)
