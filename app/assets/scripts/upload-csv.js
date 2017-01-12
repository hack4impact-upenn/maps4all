// Helper to initialize CSV Upload components in templates/bulk_resource/upload.html
function initializeUpload() {
  $('.ui.radio.checkbox').checkbox();

  var csrftoken = "{{ csrf_token() }}"

  // File progress bar
  $('#upload-progress').progress();

  // CSV upload button is disabled by default, enable when a .csv file has been
  // uploaded
  $('#csv-file').change(function() {
    $('#upload-button').removeClass('disabled').addClass('active');
  });

  // Parsing of CSV file on 'Upload'
  $("#csv-upload-form").submit(function(event) {
    event.preventDefault();

    $("#status-success").empty();
    $("#status-errors").empty();
    $('#upload-progress').show();

    parseCSV();
  });
}

// Helper to parse uploaded CSV file
function parseCSV() {
  var numRows = 0;
  var numFields = 0;
  var errorList = [];
  var rowObjects = [];
  var fields;
  $("#csv-file").parse({
    config: {
      delimiter: ",",
      header: true,
      skipEmptyLines: true,
      step: function(row, parser) {
        // Check CSV formatting before parsing first row
        if (numRows == 0) {
          fields = row.meta.fields.map(function(e) {
            return e.trim();
          }).filter(function(e) {
            return e !== '';
          });
          numFields = fields.length;

          // Check that CSV data contains the required headers.
          var nameColumnIndex = fields.indexOf("Name");
          if (nameColumnIndex == -1) {
            errorList.push("'Name' is a required column name.");
          }
          var addressColumnIndex = fields.indexOf("Address");
          if (addressColumnIndex == -1) {
            errorList.push("'Address' is a required column name.");
          }

          // Stop parsing and force user to add the required columns
          if (errorList.length > 0) {
            parser.abort();
          }
        }

        // Remove whitespace from fields and values
        row = JSON.parse(
                JSON.stringify(row.data[0]).replace(/"\s+|\s+"/g,'"')
              );

        // Catch empty lines
        // skipEmptyLines config does not catch this since we include the header
        // so the row is returned as an object which is not considered 'empty'
        var rowValues = Object.values(row).filter(function(e) {
          return e !== '';
        }); // row cell values
        if (rowValues.length != 0) {
          var rowNum = numRows + 2

          // Check that each row has all the headers (can have empty values
          // for each header except required columns)
          if (row['Name'] === '') {
            errorList.push("Row " + (rowNum)
              + " is missing a required 'Name' value.");
          }

          if (row['Address'] === '') {
            errorList.push("Row " + (rowNum)
              + " is missing a required 'Address' value.");
          }

          var rowColumns = Object.keys(row).filter(function(e) {
            return e !== '';
          }); // row header values
          if (rowColumns.length != numFields) {
            errorList.push("Row " + (rowNum)
              + " has the incorrect number of columns: " + rowColumns.length
              + ". Expected: " + numFields);
          }

          // Store each of the rows to be sent to the server
          rowObjects.push(row);
          numRows++;
        }
      },
    },
    error: function(error, file) {
      displayErrors([error]);
    },
    complete: function() {
      if (errorList.length > 0) {
        displayErrors(errorList);
      } else {
        submitCsvData(numRows, rowObjects, fields);
      }
    },
  });
}

// Helper to display errors on the CSV upload page about CSV parsing errors
function displayErrors(errorList) {
  for (var i = 0; i < errorList.length; i++) {
    $("#status-errors").append(
      "<div class='item'>" + errorList[i] + "</div>"
    );
  }
  $('#upload-progress').progress('set error');
}

// Helper to submit the parsed CSV data to the server to go through the
// CSV workflow
function submitCsvData(numRows, rowObjects, fields) {
  // Create list of Ajax requests: first processing the fields of the CSV then
  // the rows
  var ajaxReqs = [];
  var resetOrUpdate = document.getElementById('reset').checked
    ? 'reset' : 'update';
  if (resetOrUpdate === 'reset') {
    ajaxReqs.push({
      action: 'fields-reset',
      fields: fields,
    });
  } else {
    ajaxReqs.push({
      action: 'fields-update',
      fields: fields,
    });
  }

  if (rowObjects.length > 0) {
    var action = resetOrUpdate === 'reset' ? 'reset-update' : 'update';
    rowObjects.forEach(function(obj) {
      ajaxReqs.push({
        action: action,
        row: obj,
      });
    });
  }

  // Finished action to move onto next step
  ajaxReqs.push({
    action: 'finished',
  });


  var moveToNextStep = true;

  // DeferredAjax object definition
  // Each Ajax request will be executed as a DeferredAjax object to enforce
  // all the Ajax requests executing sequentially (next will only execute when
  // previous is finished)
  function DeferredAjax(opts) {
    this.options = opts;
    this.deferred = $.Deferred();
    this.action = opts.action;
    this.row = opts.row;
    this.fields = opts.fields;
    this.count = opts.count;
  }

  DeferredAjax.prototype.invoke = function() {
    var self = this;
    var data = {
      action: self.action,
      row: self.row,
      fields: self.fields,
      count: self.count,
    };
    return $.ajax({
      type: "POST",
      url: "/bulk-resource/_upload",
      data: {json: JSON.stringify(data)},
      dataType: "JSON",
      success: function(res) {
        if (res.redirect) {
            window.location.href = res.redirect;
        }
        if (res.status === 'Success') {
          $("#status-success").append(
            "<div class='item'>" + res.message + "</div>"
          );
        } else if (res.status = 'Error') {
          $("#status-errors").append(
            "<div class='item'>" + res.message + "</div>"
          );
          moveToNextStep = false;
        }
        self.deferred.resolve();
     },
     error: function(res, err, msg) {
       $("#status-errors").append(
         "<div class='item'>There was an unexpected error. " +
         "Please try again.</div>"
       );
       $('#upload-progress').progress('set error');
     },
   });
  }

  DeferredAjax.prototype.promise = function() {
    return this.deferred.promise();
  }

  // Initialize progress values
  var numReqs = ajaxReqs.length;
  $('#upload-progress').progress('set total', numReqs);

  // Execute each Ajax request sequentially, waiting for the previous to
  // finish before executing the next so we can process each row one by one.
  // If one of the rows fails, we abort the entire operation
  prevAjax = $.Deferred();
  prevAjax.resolve();
  $.each(ajaxReqs, function(idx, el) {
    var nextAjax = new DeferredAjax({
      action: el.action,
      row: el.row,
      fields: el.fields,
      count: idx,
    });
    $.when(prevAjax).then(
      function() { /* success */
        // handle progress bar
        $('#upload-progress').progress('increment', 1);

        if (el.action === 'finished' && !moveToNextStep) {
          nextAjax.abort();
        } else {
          nextAjax.invoke();
        }
      },
      function() { /* failure */
        nextAjax.abort();
      }
    );
    prevAjax = nextAjax;
  });
}
