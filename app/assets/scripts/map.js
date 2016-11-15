// This JS file is for the map and list view creations on the homepage of the
// Maps4All site for the user. This example requires the Places library. Include
// the libraries=places parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places">

var map;
var markers = [];
var infowindow;

function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 39.949, lng: -75.181}, // TODO(#52): Do not hardcode this.
    zoom: 13
  });
  var input = document.getElementById('pac-input');
  var autocomplete = new google.maps.places.Autocomplete(input);
  autocomplete.bindTo('bounds', map);
  infowindow = new google.maps.InfoWindow();
  var marker = new google.maps.Marker({
    map: map,
    anchorPoint: new google.maps.Point(0, -29)
  });

  autocomplete.addListener('place_changed', function() {
    infowindow.close();
    var place = autocomplete.getPlace();
    if (!place.geometry) {
      window.alert("Autocomplete's returned place contains no geometry");
      return;
    }
    // If the place has a geometry, then present it on a map.
    if (place.geometry.viewport) {
      map.fitBounds(place.geometry.viewport);
    } else {
      map.setCenter(place.geometry.location);
      map.setZoom(17);
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
    marker.setLabel(address);
    var placeDiv = document.createElement('div');
    var br = document.createElement('br');
    $(placeDiv).append(place.name, br, address);
    infowindow.setContent(placeDiv);
    infowindow.open(map, marker);
  });

  var marker = new google.maps.Marker({
    map: map
  });

  $.get('/get-resources').done(function(resourcesString){
    var resources = JSON.parse(resourcesString);
    for (var i = 0; i < resources.length; i++) {
      create_marker(resources[i]);
    }
    for (var i = 0; i < markers.length; i++) {
      markers[i].setMap(map);
    }
   })

  google.maps.event.addListenerOnce(map, 'idle', function(){
    populateListDiv();
  });
  var mapViewButton = document.getElementById("map_view");
  mapViewButton.addEventListener('click', function() {
    $("#map").show();
    $("#list").hide();
    $("#more-info").empty();
    $("#sidebar").show();
  });
}

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
        var contentDiv = document.createElement('div');
        var strong = document.createElement('strong');
        var br = document.createElement('br');
        $(strong).html(resource.name);
        $(contentDiv).append(strong, br, resource.address);
        if (infowindow) {
          infowindow.close();
        }
        infowindow = new google.maps.InfoWindow({
          content: contentDiv
        });
        infowindow.open(map, markerToAdd);
        google.maps.event.addListener(infowindow, 'closeclick', function() {
          $('#more-info').empty();
        });
        $.get('get-associations/' + resource.id).done(function(associations) {
          var associationObject = JSON.parse(associations);
          $('#more-info').empty();
          for (var key in associationObject) {
            var p = document.createElement('p');
            var bolded = document.createElement('strong');
            $(bolded).append(key);
            var value = associationObject[key];
            $(p).append(bolded, ': ', value);
            $('#more-info').append(p);
          }
          var a = document.createElement('a');
          $(a).attr('href', 'suggestion/' + resource.id);
          $(a).html('Suggest an edit for this resource');
          $('#more-info').append(a);
        }).fail(function() {});
      });
      callback();
    }, function() {
         markers.push(markerToAdd)
    }
  );
}

$(document).ready(function() {
  $('#resources-form').submit(function(e) {
    e.preventDefault();
    var query = document.getElementById('resources-input').value;
    var endpoint = '/search-resources/'+query;
    if (query.length == 0) {
        endpoint = '/get-resources';
    }
    $.get(endpoint).done(function(resourcesString) {
      for (var i=0; i < markers.length; i++) {
        markers[i].setMap(null);
      }
      markers = [];
      var resources = JSON.parse(resourcesString);
      for (var i=0; i < resources.length; i++) {
        create_marker(resources[i]);
      }
      for (var i=0; i < markers.length; i++) {
        markers[i].setMap(map);
      }
    populateListDiv();
    });
  });
});

function geocodeLatLng(geocoder, input_lat, input_lng) {
  geocoder.geocode({'location': {lat: input_lat, lng: input_lng}}, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      if (results[1]) {
        return results[1].formatted_address;
      } else {
        return "";
      }
    }
  });
}

function populateListDiv() {
  // Right now, all markers are shown. Filtering can be done here.
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
