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

    update : () ->
      $.ajax(
        dataType: 'json'
        url : @get('data_url')
        data : JSON.stringify(@get('expr'))
        xhrField :
          withCredentials : true
        method : 'POST'
        contentType : 'application/json'
      ).done((data) =>
        columns_of_data = _.zip.apply(_, data.data)
        data_dict = {}
        for colname, idx in data.names
          data_dict[colname] = columns_of_data[idx]
        orig_data = _.clone(@get('data'))
        _.extend(orig_data, data_dict)
        @set('data', orig_data)
      )

  class BlazeDataSources extends Backbone.Collection
    model: BlazeDataSource
    defaults:
      url : ""
      expr : null

  return {
    "Model": BlazeDataSource,
    "Collection": new BlazeDataSources()
  }
