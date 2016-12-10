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

// Click listener for a marker.
function markerListener(marker, event) {
  $("#map").show();
  $("#resource-info").hide();

  // Show marker info bubble
  var markerInfoWindowTemplate = $("#marker-info-window-template").html();
  var compiledMarkerInfoWindowTemplate =
    Handlebars.compile(markerInfoWindowTemplate);
  var context = {
    name: marker.title,
    address: marker.address,
  };
  var markerInfo = compiledMarkerInfoWindowTemplate(context);

  if (infowindow) {
    infowindow.close();
  }
  infowindow = new google.maps.InfoWindow({
    content: markerInfo,
    maxWidth: 300,
  });
  infowindow.open(map, marker);

  // Marker "more information" link to detailed resource information view
  $(".more-info").click(function() {
    displayDetailedResourceView(marker);
  });
}

// Generate the detailed resource page view after clicking "more information"
// on a marker
function displayDetailedResourceView(marker) {
  // get descriptor information as associations
  $.get('get-associations/' + marker.resourceID).done(function(associations) {
    $("#map").hide();
    $("#resource-info").empty();
    $("#resource-info").show();

    var associationObject = JSON.parse(associations);
    var descriptors = [];
    for (var key in associationObject) {
      var descriptor = {
        key: key,
        value: associationObject[key],
      };
      descriptors.push(descriptor);
    }

    // Detailed resource information template generation
    var resourceTemplate = $("#resource-template").html();
    var compiledResourceTemplate = Handlebars.compile(resourceTemplate);
    var context = {
      name: marker.title,
      address: marker.address,
      suggestionUrl: 'suggestion/' + marker.resourceID,
      descriptors: descriptors,
    };
    var resourceInfo = compiledResourceTemplate(context);
    $("#resource-info").html(resourceInfo);

    // Set handlers and populate DOM elements from resource template
    // Can only reference elements in template after compilation
    $('#back-button').click(function() {
      $("#map").show();
      $("#resource-info").hide();
    });

    // Map for single resource on detailed resource info page
    var singleResourceMap = new google.maps.Map(
      document.getElementById('single-resource-map'),
      {
        center: marker.getPosition(),
        zoom: focusZoom,
      }
    );
    var singleMarker = new google.maps.Marker({
      position: marker.getPosition(),
      map: singleResourceMap,
    });
  });
}

/*
 * Initializes the map, the corresponding list of resources and search
 * functionality on the resources
 */
function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 39.949, lng: -75.181}, // TODO(#52): Do not hardcode this.
    zoom: focusZoom,
  });

  oms = new OverlappingMarkerSpiderfier(map, {keepSpiderfied: true, nearbyDistance: 10});

  // Add click listener to marker for displaying infoWindow
  oms.addListener('click', markerListener);

  infowindow = new google.maps.InfoWindow();
  initLocationSearch(map);
  initResourceSearch();

  $.get('/get-resources').done(function(resourcesString) {
    var resources = JSON.parse(resourcesString);
    populateMarkers(resources);
  });

  google.maps.event.addListenerOnce(map, 'idle', function() {
    populateListDiv();
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

    if (!locationMarker) {
      locationMarker = new google.maps.Marker({
        map: map,
        position: place.geometry.location,
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: 8,
          strokeColor: 'grey',
          fillColor: 'black',
          fillOpacity: 1,
        },
      });
    } else {
      locationMarker.setPosition(place.geometry.location);
    }

    // Marker info window for searched location
    var searchedLocationInfoWindowTemplate =
      $("#searched-location-info-window-template").html();
    var compiledLocInfoWindowTemplate =
      Handlebars.compile(searchedLocationInfoWindowTemplate);
    var context = {
      name: place.name,
      address: address,
    };
    var locationMarkerInfo = compiledLocInfoWindowTemplate(context);

    infowindow.setContent(locationMarkerInfo);
    infowindow.open(map, locationMarker);
  });

  // Delete location marker when deleting location query
  $('#pac-input').keyup(function() {
    if ($(this).val() === "") {
      locationMarker.setMap(null);
      locationMarker = null;
    }
  });
}

/*
 * Initialize searching on the map by resource name input
 */
function initResourceSearch() {
  // Click 'Search' on resource name input
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
    var optionalOptionNames = [];
    $("#option-descriptor-name").each(function() {
        optionalOptionNames.push($(this).val());
    })
    for (var i = 0; i < optionalOptions.length; i++) {
        query += '&optoption=' + optionalOptions[i];
    }
    var endpoint = '/search-resources'+query;
    resourceSearchRequest(endpoint);
  });

  // Remove query from resource name input displays
  // all resources again
  $('#resources-input').keyup(function() {
    if ($(this).val().length === 0) {
      resourceSearchRequest('/get-resources');
    }
  });
}

function resourceSearchRequest(endpoint) {
  $.get(endpoint).done(function(resourcesString) {
    for (var i = 0; i < markers.length; i++) {
      markers[i].setMap(null);
    }
    markers = [];
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

  map.fitBounds(bounds);
  map.setCenter(bounds.getCenter());
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
  markerToAdd.resourceID = resource.id;
  markerToAdd.address = resource.address;

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
    });
  });
}

// Resize map/list area - set height to fit screen
function resizeMapListGrid() {
  var navHeight = $('.ui.navigation.grid').height();
  // TODO: remove hack of subtracting 40
  $('#map-list-grid').height($('body').height() - navHeight - 40);

  var center = map.getCenter();
  // Need to call resize event on map or creates dead grey area on map
  google.maps.event.trigger(map, "resize");
  map.setCenter(center);
}
