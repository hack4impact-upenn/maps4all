// This JS file is for the map and list view creations on the homepage of the
// Maps4All site for the user. This example requires the Places library. Include
// the libraries=places parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places">

var map;
var markers = [];
var infowindow;

/*
 * Initializes the map, the corresponding list of resources and search
 * functionality on the resources
 */
function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 39.949, lng: -75.181}, // TODO(#52): Do not hardcode this.
    zoom: 13
  });

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
    map.setCenter(place.geometry.location);
    map.setZoom(17);

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

    var marker = new google.maps.Marker({
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
    var placeDiv = document.createElement('div');
    var br = document.createElement('br');
    $(placeDiv).append(place.name, br, address);
    infowindow.setContent(placeDiv);
    infowindow.open(map, marker);
  });
}

/*
 * Initialize searching on the map by resource name input
 */
function initResourceSearch() {
  $('#resources-form').submit(function(e) {
    e.preventDefault();
    var query = $('#resources-input').val();
    var endpoint = '/search-resources/'+query;
    if (query.length == 0) {
        endpoint = '/get-resources';
    }
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
  });
}

/*
 * Create markers for each resource and add them to the map
 * Expand the map to show all resources
 */
function populateMarkers(resources) {
  for (var i = 0; i < resources.length; i++) {
    create_marker(resources[i]);
  }

  var bounds = new google.maps.LatLngBounds();
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
    bounds.extend(markers[i].getPosition());
  }

  map.fitBounds(bounds);
  map.setCenter(bounds.getCenter());
}

/*
 * Create a marker for each resource and handle clicking on a marker.
 * Handle clicking on more information for a resource
 */
function create_marker(resource){
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
  var values = [];
  values.push(markerToAdd.json_data);
  async.each(values,
    function(value, callback){
      markerToAdd.addListener('click', function() {
        $("#map").show();
        $("#resource-info").hide();

        var contentDiv = document.createElement('div');
        var resName = document.createElement('strong');
        $(resName).html(resource.name);
        var br = document.createElement('br');

        // information pane to replace map
        // TODO: refactor how the page elements are generated
        var moreLink = document.createElement('p');
        moreLink.innerHTML = 'More Info';
        moreLink.setAttribute('class', 'more-info')
        moreLink.addEventListener('click', function() {
          // get descriptor information
          $.get('get-associations/' + resource.id).done(function(associations) {
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

            // render resource info with handlebars
            var resourceTemplate = $("#resource-template").html();
            var compiledTemplate = Handlebars.compile(resourceTemplate);
            var context = {
              name: resource.name,
              address: resource.address,
              suggestionUrl: 'suggestion/' + resource.id,
              descriptors: descriptors,
            };
            var resourceInfo = compiledTemplate(context);
            $("#resource-info").html(resourceInfo);

            // can only reference elements in template after compilation
            $('#back-button').click(function() {
              $("#map").show();
              $("#resource-info").hide();
            });

            // map for single resource
            var singleMap = new google.maps.Map(
              document.getElementById('single-map'),
              {
                center: markerToAdd.getPosition(),
                zoom: 17,
              }
            );
            var singleMarker = new google.maps.Marker({
              position: markerToAdd.getPosition(),
              map: singleMap
            });
          }).fail(function() {});
        });
        $(contentDiv).append(resName, br, resource.address, moreLink);

        if (infowindow) {
          infowindow.close();
        }
        infowindow = new google.maps.InfoWindow({
          content: contentDiv
        });
        infowindow.open(map, markerToAdd);
        map.setCenter(markerToAdd.getPosition());
        map.setZoom(17);
      });
      callback();
    }, function() {
         markers.push(markerToAdd)
    }
  );
}

/*
 * Show a corresponding list of resources adjacent to the map
 */
function populateListDiv() {
  var markersToShow = markers;
  $("#list").empty();

  var list = document.getElementById('list');
  $.each(markersToShow, function(i, markerToShow) {
    var listElement = document.createElement('a');
    listElement.setAttribute('class', 'item');

    var rightArrowElement = document.createElement('div');
    rightArrowElement.setAttribute('class', 'right floated content');

    var rightArrowImage = document.createElement('i');
    rightArrowImage.setAttribute('class', 'right chevron icon');

    rightArrowElement.appendChild(rightArrowImage);
    listElement.appendChild(rightArrowElement);

    var mainContent = document.createElement('div');
    mainContent.setAttribute('class', 'content');

    var placeTitle = document.createElement('div');
    placeTitle.setAttribute('class', 'list-item-title');
    $(placeTitle).html(markerToShow.title);

    mainContent.appendChild(placeTitle);
    listElement.appendChild(mainContent);

    list.appendChild(listElement);

    listElement.addEventListener('click', function() {
      google.maps.event.trigger(markerToShow, 'click');
    });
  });
}
