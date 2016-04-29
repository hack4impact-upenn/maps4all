// This JS file is for the map and list view creations on the homepage of the
// Maps4All site for the user. This example requires the Places library. Include
// the libraries=places parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places">

var map;
var markers = [];

function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 39.949, lng: -75.181},
    zoom: 13
  });
  var input = document.getElementById('pac-input');
  var types = document.getElementById('type-selector');
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(types);
  var autocomplete = new google.maps.places.Autocomplete(input);
  autocomplete.bindTo('bounds', map);
  var infowindow = new google.maps.InfoWindow();
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
    for (var i=0; i < resources.length; i++){
      create_marker(resources[i]);
    }
    for (var i=0; i < markers.length; i++){
      markers[i].setMap(map);
    }
   })

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
            $("#more-info").empty();
          });
          $.get('get-associations/' + resource.id).done(function(associations) {
            var associationObject = JSON.parse(associations);
            $("#more-info" ).empty();
            for (var key in associationObject) {
              var p = document.createElement('p');
              var bolded = document.createElement('strong');
              $(bolded).append(key);
              var value = associationObject[key];
              $(p).append(bolded, ': ', value);
              $("#more-info").append(p);
            }
          }).fail(function() {});
        });
        callback();
      }, function() {
        markers.push(markerToAdd)
      }
    );
  }

  var mapViewButton = document.getElementById("map_view");
  var listViewButton = document.getElementById("list_view");
  mapViewButton.addEventListener('click', function() {
    $("#map").show();
    $("#list").hide();
    $("#more-info").empty();
    $("#sidebar").show();
  });
  listViewButton.addEventListener('click', function() {
    $("#map").hide();
    populateListDiv();
    $("#list").show();
    $("#sidebar").hide();
  });
}

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
  var markersToShow = [];
  $("#list").empty();
  var bounds = map.getBounds();
  for (var i = 0; i < markers.length; i++) {
    if (bounds.contains(markers[i].getPosition())) {
      markersToShow.push(markers[i]);
    }
  }
  var table = document.createElement('table');
  $.each(markersToShow, function(i, markerToShow) {
    var tableCell = document.createElement('td');
    $(tableCell).attr({
      'style': 'overflow:hidden;width:100%;height:100%;position:absolute'
    });
    var tableCellBoldTitle = document.createElement('strong');
    var tableCellNewline = document.createElement('br');
    var tableCellInnerDiv = document.createElement('div');
    $(tableCellInnerDiv).attr({
      'style': 'width:50px;height:50px; text-align:right; float: right;'
    });
    var tableCellImg = document.createElement('img');
    $(tableCellImg).attr({
      'src': 'static/images/red-dot.png',
      'style': 'width:50%;height:50%;'
    });
    $(tableCellInnerDiv).append(tableCellImg);
    $(tableCellBoldTitle).html(markerToShow.getTitle());
    $(tableCell).append(tableCellInnerDiv);
    $(tableCell).append(tableCellBoldTitle, tableCellNewline,
                        '<b>' + markerToShow.title + '</b><br>');

    $(table).append('<br>');
    $(table).append('<br>');
    $(table).append(tableCell);
  });
  $("#list").append(table);
}
