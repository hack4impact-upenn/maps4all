// This JS file is for the map and list view creations on the homepage of the
// Maps4All site for the user. This example requires the Places library. Include
// the libraries=places parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places">

var map;
var oms;
var markers = [];
var infowindow;
var focusZoom = 17;
var locationMarker;
var allResourceBounds;

// Click listener for a marker.
function markerListener(marker, event) {
  $('.list-resource').removeClass('list-selected');
  $('#map').show();
  $('#resource-info').hide();

  var isResponsive = false;
  // Adapt to one column view
  // Clicking a list element/marker should hide the list view and
  // show the marker on the map and a footer underneath the map with marker info
  if ($(window).width() <= singleColBreakpoint) {
    isResponsive = true;
    listToMapSingleColumn();
    $('#map-footer').show();
    $('#map-footer').scrollTop(0);

    // TODO: Remove 15 hack
    // Split view vertically between map and a map footer for info
    $('#right-column').height($('#map-list-grid').height());
    var totalHeight = $('#right-column').height() - 15;
    $('#map-footer').height(totalHeight / 3);
    $('#map').height(2 * totalHeight / 3);
    resizeMapListGrid();

    // Need to set center and zoom since default is not at right location
    map.setCenter(marker.getPosition());
    map.setZoom(17);
  }

  // Show marker info bubble
  var markerInfoWindowTemplate = $("#marker-info-window-template").html();
  var compiledMarkerInfoWindowTemplate =
    Handlebars.compile(markerInfoWindowTemplate);
  var context = {
    name: marker.title,
    address: marker.address,
    avg_rating: marker.avg_rating,
    responsive: isResponsive,
  };
  var markerInfo = compiledMarkerInfoWindowTemplate(context);

  if (infowindow) {
    infowindow.close();
  }

  // If more than one column, display info window
  if ($(window).width() > singleColBreakpoint) {
    infowindow = new google.maps.InfoWindow({
      content: markerInfo,
      maxWidth: 300,
    });
    infowindow.open(map, marker);
  } else { // If one column then display bottom box for info
    $('#map-footer').html(markerInfo);
    // go back to list view from map info
    $('#mobile-list-btn').click(function() {
      mapToListSingleColumn();
    });
  }

  // Marker "more information" link to detailed resource information view
  $(".more-info").click(function() {
    displayDetailedResourceView(marker);
  });
}

// Re-render html for descriptor values containing phone numbers
function displayPhoneNumbers(descriptors) {
  var PHONE_NUMBER_LENGTH = 12;
  for (var desc in descriptors) {
    // skip option descriptors
    if (desc.value) {
      var updated = desc.value.replace(/(\d\d\d-\d\d\d-\d\d\d\d)/g,
        function replacePhoneNum(num) {
          return "<a href=\"tel:+1-" + num + "\">" + num + "</a>";
        }
      );
      $('#descriptor-value-'+desc.key).html(updated);
    }
  }
}

// Generate the detailed resource page view after clicking "more information"
// on a marker
function displayDetailedResourceView(marker) {
  // get descriptor information as associations
  $.get('get-associations/' + marker.resourceID).done(function(associations) {

    $("#map").hide();
    $('#map-footer').hide();
    $("#resource-info").empty();
    $("#resource-info").show();

    var associationObject = JSON.parse(associations);
    var descriptors = [];
    for (var key in associationObject) {
      var value = associationObject[key];

      // Combine multiple option descriptor values
      if (Array.isArray(associationObject[key])) {
        value = Object.keys(value).map(function(key) {
          return value[key];
        });
        value = value.join(', ');
      }

      var descriptor = {
        key: key,
        value: value
      };
      descriptors.push(descriptor);
    }
    // Detailed resource information template generation
    Handlebars.registerHelper('concat', function(str1, str2) {
        return str1 + str2;
    });
    var resourceTemplate = $("#resource-template").html();
    var compiledResourceTemplate = Handlebars.compile(resourceTemplate);
    var context = {
      name: marker.title,
      address: marker.address,
      suggestionUrl: 'suggestion/' + marker.resourceID,
      descriptors: descriptors,
      avg_rating: marker.avg_rating,
      requiredOpts: marker.requiredOpts,
    };
    var resourceInfo = compiledResourceTemplate(context);
    $("#resource-info").html(resourceInfo);
    displayPhoneNumbers(descriptors);

    // Set handlers and populate DOM elements from resource template
    // Can only reference elements in template after compilation
    $("#resource-info").scrollTop(0); // reset scroll on div to top
    $('#back-button').click(function() {
      $("#map").show();
      $("#resource-info").hide();

      if ($(window).width() <= singleColBreakpoint) {
        $('#map-footer').show();
      }
      resizeMapListGrid();
    });

    $('.ui.rating')
    .rating({
      initialRating: 0,
      maxRating: 5,
      onRate: function(value) {
        if (value !== 0){
          $('#submit-rating').removeClass('disabled').addClass('active');}
      }
    });

    $('#submit-rating').click(function(e) {
      e.preventDefault();
      var rating = $('#rating-input').rating('get rating');
      var review = $('#review').val();
      var id = marker.resourceID;
      submitReview(rating,review,id);
    });

    // Button to "send" a text to the number using twilio
    $('#text-save-submit').click(function(e){
      var number = $('#phone-number').val();
      var id = marker.resourceID;
      sendText(number,id);
    });

    $('#sms-success-close')
      .on('click', function() {
        $(this)
          .closest('.message')
          .transition('fade');
      });

    // Map for single resource on detailed resource info page
    var singleResourceMap = new google.maps.Map(
      document.getElementById('single-resource-map'),
      {
        center: marker.getPosition(),
        zoom: focusZoom,
        scrollwheel: false,
        draggable: false,
      }
    );
    var singleMarker = new google.maps.Marker({
      position: marker.getPosition(),
      map: singleResourceMap,
    });
  });
}

function submitReview(rating, review, id){
  var ratingReview = {
  'rating': rating,
  'review': review,
  'id': id,
  };
  $.ajax({
     url: '/rating-post',
     data: JSON.stringify(ratingReview),
     contentType: 'application/json',
     dataType: 'json',
     method: 'POST'
  });
  $(".userRating").hide();
  $(".successMessage").show();
}

function sendText(number,id) {
  var twilioText = {
    'number': number,
    'id': id
  };
  $.ajax({
    url:'/send-sms',
    data: JSON.stringify(twilioText),
    contentType: 'application/json',
    dataType:'json',
    method: 'POST',
    success: function(data) {
      if(data.status=='success') {
        $(".textSentSuccess").show();
      }
      else {
        alert('Invalid phone number');
        $("#phone-number").val('');
      }
    }
  });
}

function getCurrentLocation(callback) {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      var currentLocation = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };
      callback(true, currentLocation);
    }, function() {
      console.log('Error getting current user location')
      callback(false, null);
    });
  }
}

/*
 * Set minimum initial zoom level so the map is not zoomed in too much
*/
function setInitialZoom() {
  google.maps.event.addListener(map, 'zoom_changed', function() {
    zoomChangeBoundsListener =
      google.maps.event.addListener(map, 'bounds_changed', function(event) {
        if (this.getZoom() > 16 && this.initialZoom) {
          // Change max/min zoom here
          this.setZoom(16);
          this.initialZoom = false;
        }
      google.maps.event.removeListener(zoomChangeBoundsListener);
    });
  });
  map.initialZoom = true;
}

/*
 * Initializes the map, the corresponding list of resources and search
 * functionality on the resources
 */
function initMap() {
  // Hide resource-info
  $("#resource-info").empty();
  $("#resource-info").hide();

  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 39.8283, lng: -98.5795},
    zoom: 4
  });

  oms = new OverlappingMarkerSpiderfier(map, {keepSpiderfied: true, nearbyDistance: 10});

  // Add click listener to marker for displaying infoWindow
  oms.addListener('click', markerListener);

  infowindow = new google.maps.InfoWindow();
  initLocationSearch(map);
  initResourceSearch();
  initResetButton();
  initCurrentLocationButton();
  setInitialZoom();

  $.get('/get-resources').done(function(resourcesString) {
    var resources = JSON.parse(resourcesString);
    if (resources && resources.length > 0) {
      populateMarkers(resources);
      populateListDiv();
    }
  });
}

/*
 * Initialize searching on the map by location input.
 * When entering a new location, re-center and zoom the map onto that location
 * and create a custom location marker.
 */
function initLocationSearch(map) {
  var input = document.getElementById('pac-input');
  var autocomplete = new google.maps.places.Autocomplete(input);
  autocomplete.bindTo('bounds', map);

  autocomplete.addListener('place_changed', function() {
    infowindow.close();
    var place = autocomplete.getPlace();
    if (!place.geometry) {
      window.alert("Autocomplete's returned place contains no geometry");
      return;
    }

    var address = '';
    if (place.address_components) {
      address = [
        ((place.address_components[0] &&
          place.address_components[0].short_name) || ''),
        ((place.address_components[1] &&
          place.address_components[1].short_name) || ''),
        ((place.address_components[2] &&
          place.address_components[2].short_name) || '')
      ].join(' ');
    }
    var marker_info = {
      location: place.location,
      address: address,
      name: place.name,
      currentLocation: false
    };
    createLocationMarker(marker_info);

    // If in single column view, entering a location should go to the map view
    if ($(window).width() <= singleColBreakpoint) {
      listToMapSingleColumn();
    }
  });

  // Delete location marker when deleting location query
  $('#pac-input').keyup(function() {
    if ($(this).val() === "") {
      locationMarker.setMap(null);
      locationMarker = null;
    }
  });
}

function initCurrentLocationButton() {
  $('#get-user-location').click(function() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(position) {
        var pos = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };

        var marker_info = {
          location: pos,
          address: "",
          name: "You are here",
          currentLocation: true
        }
        createLocationMarker(marker_info);
      }, function() {
        // TODO: Add error handling
        console.log('Error getting current user location')
      });
    }
  });
}


function createLocationMarker(marker_info){
  if (!locationMarker) {
      locationMarker = new google.maps.Marker({
        map: map,
        position: marker_info.location,
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: 8,
          strokeColor: 'grey',
          fillColor: 'black',
          fillOpacity: 1,
        },
      });
      console.log("location marker made")
    } else {
      locationMarker.setPosition(marker_info.location);
    }

  // Marker info window for searched location
  var searchedLocationInfoWindowTemplate =
    $("#searched-location-info-window-template").html();
  var compiledLocInfoWindowTemplate =
    Handlebars.compile(searchedLocationInfoWindowTemplate);
  if(marker_info.currentLocation){
    var context = {
    name: marker_info.name,
    address: " ",
    };
  } else {
    var context = {
      name: marker_info.name,
      address: address,
    };
  }
  var locationMarkerInfo = compiledLocInfoWindowTemplate(context);

  infowindow.setContent(locationMarkerInfo);
  infowindow.open(map, locationMarker);

  // If in single column view, entering a location should go to the map view
  if ($(window).width() <= singleColBreakpoint) {
    listToMapSingleColumn();
  }
}

/*
 * Initialize searching on the map by resource name input
 */
function initResourceSearch() {
  // Click 'Search' on search box
  $('#search-user-resources').click(function() {
    var query = '?' + 'name=' + $('#resources-input').val();
    var requiredOptions = [];
    $("#search-resources-req-options :selected").each(function() {
      requiredOptions.push($(this).val());
    });
    for (var i = 0; i < requiredOptions.length; i++) {
      query += '&reqoption=' + requiredOptions[i];
    }
    var optionalOptions = [];
    $("#advanced-search select").each(function() {
        optionalOptions.push($(this).val());
    })
    for (var i = 0; i < optionalOptions.length; i++) {
        query += '&optoption=' + optionalOptions[i];
    }
    var endpoint = '/search-resources'+query;
    resourceSearchRequest(endpoint);
    $('#resource-info').hide();
  });

  // Remove query from resource name input displays
  // all resources again
  $('#resources-input').keyup(function() {
    if ($(this).val().length === 0) {
      resourceSearchRequest('/get-resources');
    }
  });
}

/*
 * Initialize resetting search input and filters
 */
function initResetButton() {
  // Click 'Reset' on search box
  $('#reset-button').click(function() {
    // clear search input and option filters
    $('#resources-input').val('');
    $('#search-resources-req-options').dropdown('clear');
    $('.search-resources-options').dropdown('clear');

    // Placeholder text for descriptor dropdowns
    $(".ui.dropdown>.text").text("Choose option(s)");

    // clear location
    locationMarker.setMap(null);
    locationMarker = null;
    $('#pac-input').val('');

    // show all resources again
    resourceSearchRequest('/get-resources');
  });
}

function resourceSearchRequest(endpoint) {
  $.get(endpoint).done(function(resourcesString) {
    for (var i = 0; i < markers.length; i++) {
      markers[i].setMap(null);
    }
    markers = [];
    $('#map').show();
    var resources = JSON.parse(resourcesString);
    if (resources.length != 0) {
      populateMarkers(resources);
    }
    populateListDiv();
  });
}

/*
 * Create markers for each resource and add them to the map
 * Expand the map to show all resources
 */
function populateMarkers(resources) {
  for (var i = 0; i < resources.length; i++) {
    createMarker(resources[i]);
  }
  var bounds = new google.maps.LatLngBounds();
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
    oms.addMarker(markers[i]);
    bounds.extend(markers[i].getPosition());
  }
  allResourceBounds = bounds;
  map.setCenter(bounds.getCenter());
  map.fitBounds(bounds);
}

/*
 * Create a marker for each resource and handle clicking on a marker.
 * Handle clicking on more information for a resource
 */
function createMarker(resource) {
  var markerToAdd = new google.maps.Marker({
    map: map
  });
  latLng = new google.maps.LatLng(resource.latitude, resource.longitude);
  markerToAdd.setPosition(latLng);
  markerToAdd.setVisible(true);
  markerToAdd.title = resource.name;
  markerToAdd.json_data = {
    csrf_token: $('meta[name="csrf-token"]').prop('content'),
    data: resource.name
  };
  markerToAdd.avg_rating = resource.avg_rating;
  markerToAdd.resourceID = resource.id;
  markerToAdd.address = resource.address;
  markerToAdd.requiredOpts = resource.requiredOpts;

  markers.push(markerToAdd);
}

/*
 * Show a corresponding list of resources adjacent to the map
 */
function populateListDiv() {
  var markersToShow = markers;
  $("#list").empty();

  var listResources = [];
  $.each(markersToShow, function(i, markerToShow) {
    var listResource = {
      name: markerToShow.title,
      address: markerToShow.address,
      avg_rating: markerToShow.avg_rating,
      requiredOpts: markerToShow.requiredOpts,
    };
    listResources.push(listResource);
  });

  var listTemplate = $("#listview-template").html();
  var compiledListTemplate = Handlebars.compile(listTemplate);
  var context = {
    resource: listResources,
  };
  var listView = compiledListTemplate(context);
  $("#list").html(listView);

  // Can only add handlers to elements in template after compilation
  $(".list-resource").each(function(i, element) {
    element.addEventListener('click', function() {
      markerListener(markersToShow[i], 'click');
      $('.list-resource').removeClass('list-selected');

      if ($(window).width() > singleColBreakpoint) {
        $(this).addClass('list-selected');
      }
    });
  });
}

// Resize map/list area - set height to fit screen
function resizeMapListGrid() {
  var navHeight = $('.ui.navigation.grid').height();

  // TODO: remove hack of subtracting 50 and 23
  // Adjusts for space between nav and grid
  if ($(window).width() <= singleColNoSpaceBreakpoint) {
    $('#map-list-grid').height($('body').height() - navHeight - 23);
  } else {
    $('#map-list-grid').height($('body').height() - navHeight - 50);
  }

  // If we resize from single col to double col, we remove the map footer
  // so we have to make the map full size of the right column
  if ($(window).width() > singleColBreakpoint) {
    $('#map').height($('#map-list-grid').height());
  }

  var center = map.getCenter();
  var zoom = map.getZoom();
  // Need to call resize event on map or creates dead grey area on map
  google.maps.event.trigger(map, "resize");
  map.setCenter(center);
  map.setZoom(zoom);
}

/********************* MOBILE RESPONSIVE *******************/
/*
 * Adjust the map list grid based on window width
 * In general:
 *  - For <= singleColBreakpoint we only display one column
 *  - For > singleColBreakpoint we display two columns
 * Specific fixes:
 * - For <= singleColNoSpaceBreakpoint we have no white space
 *   around the #map-list-grid div while for singleColBreakpoint
 *   we do as for smaller screen sizes we need to maximize space use
 * - For > twoColResizeBreakpoint we make the #left-column a little larger
 *   to avoid that element getting too squished
 *
 * Single column things:
 * - We only display either list or map at a time
 * - When we display the map, we display a map footer, which is a div
 *   underneath the map that will display a link back to the list and
 *   replaces in the infowindow for showing content relating to a selected
 *   marker
 */
function makeResponsive() {
  setInitialZoom();

  // Change to a single column view
  if ($(window).width() <= singleColNoSpaceBreakpoint) {
    singleColumnResets();
    $('#map-list-grid').removeClass('grid-space-large');
    $('#map-list-grid').addClass('grid-space-small');
  } else if (
    $(window).width() > singleColNoSpaceBreakpoint
    && $(window).width() <= singleColBreakpoint
  ) {
    singleColumnResets();
    $('#map-list-grid').removeClass('grid-space-small');
    $('#map-list-grid').addClass('grid-space-large');
  } else if ( // Change to double column views
    $(window).width() > singleColBreakpoint
    && $(window).width() <= twoColResizeBreakpoint
  ) {
    $('#left-column').removeClass().addClass('five wide column');
    $('#right-column').removeClass().addClass('eleven wide column');
    doubleColumnResets();
  } else if ($(window).width() > twoColResizeBreakpoint) {
    $('#left-column').removeClass().addClass('four wide column');
    $('#right-column').removeClass().addClass('twelve wide column');
  }
}

// Switching from double -> single column
// Default show list view
function singleColumnResets() {
  $('#left-column').removeClass().addClass('sixteen wide column');
  $('#right-column').removeClass().addClass('sixteen wide column');

  // switched from double to single
  // don't want to hide if a resize within single view is triggered
  if ($('#right-column').is(':visible') && $('#left-column').is(':visible')) {
    $('#right-column').hide();
    setNavSwitching();
  }
}

// Set a nav element that allows toggling between list and map view
// when in single column mode
function setNavSwitching() {
  // initialize to 'Show Map'
  $('#nav-to-list').hide();
  $('#nav-to-map').show();

  // Switch from list to map
  $('#nav-to-map').click(function() {
    listToMapSingleColumn();
  });

  // Switch from map to list
  $('#nav-to-list').click(function() {
    mapToListSingleColumn();
  });
}

// Changing from list view to map view in single column mode
function listToMapSingleColumn() {
  $('#left-column').hide();
  $('#right-column').show();
  $('#map').show();
  $('#map-footer').hide();
  $('#map').height($('#right-column').height());

  // show all resources on map
  if (allResourceBounds) {
    map.fitBounds(allResourceBounds);
    map.setCenter(allResourceBounds.getCenter());
  }
  var center = map.getCenter();
  // Need to call resize event on map or creates dead grey area on map
  google.maps.event.trigger(map, "resize");
  map.setCenter(center);

  $('#nav-to-list').show();
  $('#nav-to-map').hide();

  if (infowindow) {
    infowindow.close();
  }
}

// Changing from map view to list view in single column mode
function mapToListSingleColumn() {
  $('#left-column').show();
  $('#right-column').hide();
  $('#nav-to-list').hide();
  $('#nav-to-map').show();
}

// Switching from single -> double column
function doubleColumnResets() {
  $('#map-list-grid').removeClass('grid-space-small');
  $('#map-list-grid').removeClass('grid-space-large');

  $('#map-footer').hide();
  $('#left-column').show();
  $('#right-column').show();
  $('.nav-mobile-switch').hide();

  // show all resources on map
  if (allResourceBounds) {
    map.fitBounds(allResourceBounds);
    map.setCenter(allResourceBounds.getCenter());
  }
  var center = map.getCenter();
  // Need to call resize event on map or creates dead grey area on map
  google.maps.event.trigger(map, "resize");
  map.setCenter(center);
}
