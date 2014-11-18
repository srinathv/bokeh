define [
  "underscore"
  "backbone"
  "common/has_properties"
  "source/column_data_source"
  "common/logging"
], (_, Backbone, HasProperties, column_data_source, Logging) ->

  logger = Logging.logger

  #maybe generalize to ajax data source later?
  class BlazeDataSource extends column_data_source.Model
    type: 'BlazeDataSource'
    initialize : (attrs, options) ->
      super(attrs, options)
      # thought we needed to auto-update ranges, but we appear to be ok
      # for now
      @ranges = []
      @updated = false

    update : (ranges) ->
      @ranges = @ranges.concat(ranges)
      if @updated
        return null
      @updated = true
      @_update()

    _update : () =>
      console.log('AJAX')
      $.ajax(
        dataType: 'json'
        url : @get('data_url')
        data : JSON.stringify(@get('expr'))
        xhrField :
          withCredentials : true
        method : 'POST'
        contentType : 'application/json'
      ).done((data) =>
        @set_data(data)
      )

    set_data : (data) ->
      console.log('GOT AJAX')
      columns_of_data = _.zip.apply(_, data.data)
      data_dict = {}
      for colname, idx in data.names
        data_dict[colname] = columns_of_data[idx]
      orig_data = _.clone(@get('data'))
      _.extend(orig_data, data_dict)
      @set('data', orig_data)
      #TODO: handle stopping when plot is removed?
      if @get('polling_interval')
        setTimeout(@_update, @get('polling_interval'))

  class BlazeDataSources extends Backbone.Collection
    model: BlazeDataSource
    defaults:
      url : ""
      expr : null

  return {
    "Model": BlazeDataSource,
    "Collection": new BlazeDataSources()
  }
