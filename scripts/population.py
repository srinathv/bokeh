from bokeh.server.app import bokeh_app
from bokeh.server.utils.plugins import object_page
from bokeh.plotting import curdoc, cursession
from bokeh.objects import Plot
from bokeh.widgetobjects import VBox, Select
from bokeh.properties import (HasProps, Dict, Enum, Either, Float, Instance, Int, List,
    String, Color, Include, Bool, Tuple, Any, Date, RelativeDelta, lookup_descriptor)

class Population(VBox):

    year = 2010
    location = "World"
    year_select = Instance(Select)
    location_select = Instance(Select)
    plot = Instance(Plot)
    extra_generated_classes = [["Population", "Population", "VBox"]]
    def __init__(self, *args, **kwargs):
        super(Population, self).__init__(*args, **kwargs)
        from bokeh.objects import ColumnDataSource
        from bokeh.document import Document
        from bokeh.sampledata.population import load_population

        self.df = load_population()
        self.source_pyramid = ColumnDataSource(data=dict())

    def render(self):
        self.pyramid_plot()
        self.create_layout()
        self.update_pyramid()

    def pyramid_plot(self):
        from bokeh.objects import (Plot, DataRange1d, LinearAxis, Grid, Glyph,
                                   Legend, SingleIntervalTicker)
        from bokeh.glyphs import Quad

        xdr = DataRange1d(sources=[self.source_pyramid.columns("male"),
                          self.source_pyramid.columns("female")])
        ydr = DataRange1d(sources=[self.source_pyramid.columns("groups")])

        self.plot = Plot(title=None, data_sources=[self.source_pyramid],
                         x_range=xdr, y_range=ydr, plot_width=600, plot_height=600)

        xaxis = LinearAxis(plot=self.plot, dimension=0)
        yaxis = LinearAxis(plot=self.plot, dimension=1, ticker=SingleIntervalTicker(interval=5))

        xgrid = Grid(plot=self.plot, dimension=0, axis=xaxis)
        ygrid = Grid(plot=self.plot, dimension=1, axis=yaxis)

        male_quad = Quad(left="male", right=0, bottom="groups", top="shifted", fill_color="blue")
        male_quad_glyph = Glyph(data_source=self.source_pyramid,
                                xdata_range=xdr, ydata_range=ydr, glyph=male_quad)
        self.plot.renderers.append(male_quad_glyph)

        female_quad = Quad(left=0, right="female", bottom="groups", top="shifted",
                           fill_color="violet")
        female_quad_glyph = Glyph(data_source=self.source_pyramid,
                                  xdata_range=xdr, ydata_range=ydr, glyph=female_quad)
        self.plot.renderers.append(female_quad_glyph)

        legend = Legend(plot=self.plot, legends=dict(Male=[male_quad_glyph],
                        Female=[female_quad_glyph]))
        self.plot.renderers.append(legend)

    def on_year_change(self, obj, attr, old, new):
        print ('YEAR CHANGE')
        self.year = int(new)
        self.update_pyramid()
        self.pyramid_plot()
        self.children[-1] = self.plot
        curdoc().add(self)
    def on_location_change(self, obj, attr, old, new):
        self.location = new
        self.update_pyramid()
        self.pyramid_plot()
        self.children[-1] = self.plot
        curdoc().add(self)
    def create_layout(self):
        from bokeh.widgetobjects import Select, HBox, VBox

        years = list(map(str, sorted(self.df.Year.unique())))
        locations = sorted(self.df.Location.unique())

        self.year_select = Select(title="Year:", value="2010", options=years)
        self.location_select = Select(title="Location:", value="World", options=locations)

        controls = HBox(children=[self.year_select, self.location_select])
        self.children = [controls, self.plot]

    def update_pyramid(self):
        pyramid = self.df[(self.df.Location == self.location) & (self.df.Year == self.year)]

        male = pyramid[pyramid.Sex == "Male"]
        female = pyramid[pyramid.Sex == "Female"]

        total = male.Value.sum() + female.Value.sum()

        male_percent = -male.Value / total
        female_percent = female.Value / total

        groups = male.AgeGrpStart.tolist()
        shifted = groups[1:] + [groups[-1] + 5]

        self.source_pyramid.data = dict(
            groups=groups,
            shifted=shifted,
            male=male_percent,
            female=female_percent,
        )

    def update(self, **kwargs):
        super(Population, self).update(**kwargs)
        self.setup_events()

    def setup_events(self):
        if self.year_select:
            self.year_select.on_change('value', self.on_year_change)
        if self.location_select:
            self.location_select.on_change('value', self.on_location_change)

@bokeh_app.route("/bokeh/population/")
@object_page("population")
def make_population():
    pop = Population()
    pop.render()
    return pop
