
define [
  "underscore"
  "./has_properties"
  "./logging"
  "./selector"
], (_, HasProperties, Logging, Selector) ->

  logger = Logging.logger

  class SelectionManager extends HasProperties
    type: 'SelectionManager'

    initialize: (attrs, options) ->
      super(attrs, options)
      @selectors = {}

    set_selection: (indices) ->
      @_save(null, indices)
      source.trigger('select')

    select: (tool, renderer_view, geometry, final, append=false) ->
      source = @get('source')
      if source != renderer_view.mget('data_source')
        logger.warn('select called with mis-matched data sources')
      indices = renderer_view.hit_test(geometry)

      selector = @_get_selector(tool)
      selector.update(indices, geometry, final, append)
      data_geom = @data_geom(renderer_view, geometry)
      selector.set('data_geometry', data_geom)
      @_save(selector, selector.get('indices'))
      source.trigger('select')
      source.trigger('select-' + renderer_view.mget('id'))

    data_geom : (renderer_view, geom) ->
      # only rects for now
        xx = [geom['vx0'], geom['vx1']]
        yy = [geom['vy0'], geom['vy1']]
        bounds = renderer_view.plot_view.map_from_screen(xx, yy, 'data')
        x_bounds = bounds[0]
        y_bounds = bounds[1]
        return {
          'x0' : x_bounds[0], 'x1' : x_bounds[1],
          'y0' : y_bounds[0], 'y1' : y_bounds[1]
        }
    inspect: (tool, renderer_view, geometry, data) ->
      source = @get('source')
      if source != renderer_view.mget('data_source')
        logger.warn('inspect called with mis-matched data sources')

      indices = renderer_view.hit_test(geometry)

      if indices?
        source.trigger(
          'inspect', indices, tool, renderer_view, source, data
        )
        source.trigger(
          'inspect' + renderer_view.mget('id'), indices, tool, renderer_view, source, data
        )

    clear: (tool) ->
      if tool?
        selector = @_get_selector(tool)
        selector.clear()
      @get('source').trigger('deselect');
      @_save(null, [])

    _get_selector: (tool) ->
      _.setdefault(@selectors, tool.model.id, new Selector())
      return @selectors[tool.model.id]

    _save: (selector, indices) ->
      @get('source').save({
        "selector": selector
        "selection": indices
        "data_geometry" : if selector then selector.get('data_geometry') else null
      }, {patch: true})
