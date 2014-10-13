
define [
  "underscore",
  "common/collection",
  "common/has_properties",
  "common/selection_manager",
], (_, Collection, HasProperties, SelectionManager) ->

  # Datasource where the data is defined column-wise, i.e. each key in the
  # the data attribute is a column name, and its value is an array of scalars.
  # Each column should be the same length.
  class ColumnDataSource extends HasProperties
    type: 'ColumnDataSource'

    get_column: (colname) ->
      return @get('data')[colname] ? null

    get_length: () ->
      data = @get('data')
      if _.keys(data).length == 0
        return 0
      return data[_.keys(data)[0]].length

    columns: () ->
      # return the column names in this data source
      return _.keys(@get('data'))

    datapoints: () ->
      # return the data in this data source as a "array of records"
      data = @get('data')
      fields = _.keys(data)
      if fields.length == 0
        return []
      points = []
      for i in [0...data[fields[0]].length]
        point = {}
        for field in fields
          point[field] = data[field][i]
        points.push(point)
      return points

    defaults: =>
      return _.extend {}, super(), {
        data: {}
        selection_manager: new SelectionManager({'source':@})
      }

  class ColumnDataSources extends Collection
    model: ColumnDataSource
    initialize : () ->
      @storage = {}
      @sync_all = _.debounce(@_sync_all, 1000)

    bulk_sync_attrs : (attrs) =>
      for m in attrs
        @storage[m.id] = m
      @sync_all()

    get_base: ()->
      if not @_base
        @_base = require('./common/base')
      return @_base

    _sync_all : () =>
      tosave = {}
      for own id, attrs of @storage
        docid = attrs['docid']
        if not tosave[docid]?
          tosave[docid] = {}
        tosave[docid][id] = attrs
        delete @storage[id]
      for own docid, attrs of tosave
        url = @get_base().Config.prefix + "bokeh/bb/" + docid + "/bulkupsert"
        bulkjson = []
        for own id, attr of attrs
          bulkjson.push({
            'id' : attr.id,
            'type' : @model.prototype.type,
            'attributes' : attr
          })
        resp = $.ajax(
          dataType: 'json'
          url : url
          data : JSON.stringify(bulkjson)
          xhrField :
            withCredentials : true
          method : 'POST'
          contentType : 'application/json'
        )
  return {
    "Model": ColumnDataSource,
    "Collection": new ColumnDataSources()
  }
