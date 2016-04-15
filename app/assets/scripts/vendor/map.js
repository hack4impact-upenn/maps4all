      // This JS file is for the map and list view creations on the homepage of
      // the Maps4All site for the user
      // This example requires the Places library. Include the libraries=places
      // parameter when you first load the API. For example:
      // <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places">

      var map;
      var markers = [];
      //var geocoder = new google.maps.Geocoder;

      function initMap() {
        map = new google.maps.Map(document.getElementById('map'), {
          center: {lat: 39.949, lng: -75.181},
          zoom: 13
        });
        var input = /** @type {!HTMLInputElement} */(
            document.getElementById('pac-input'));


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
              (place.address_components[0] && place.address_components[0].short_name || ''),
              (place.address_components[1] && place.address_components[1].short_name || ''),
              (place.address_components[2] && place.address_components[2].short_name || '')
            ].join(' ');
          }
          marker.setLabel(address);
          infowindow.setContent('<div><strong>' + place.name + '</strong><br>' + address);
          infowindow.open(map, marker);
        });

        // Sets a listener on a radio button to change the filter type on Places
        // Autocomplete.
        function setupClickListener(id, types) {
          var radioButton = document.getElementById(id);
          radioButton.addEventListener('click', function() {
            autocomplete.setTypes(types);
          });
        }

        setupClickListener('changetype-all', []);
        setupClickListener('changetype-address', ['address']);
        setupClickListener('changetype-establishment', ['establishment']);

        var marker = new google.maps.Marker({
          map: map
        });
        $.ajax({
          type: "GET",
          url: "/get-resource"
        }).done(function(data){
            data = JSON.parse(data)
            for(var i = 0; i < data.length; i++){
              create_marker(data[i]);
            }

             for(var i = 0; i < markers.length; i ++){
                markers[i].setMap(map);
             }
         })

        function create_marker(data){
              var markerToAdd = new google.maps.Marker({
                 map: map
              })
              latLng = new google.maps.LatLng(data.Latitude, data
              .Longitude)
              markerToAdd.setPosition(latLng);
              markerToAdd.setVisible(true);
              //console.log(data.Name);
              markerToAdd.title = data.Name
              //markerToAdd.address = geocodeLatLng(geocoder, data.Latitude, data.Longitude)
              //markerToAdd.setTitle(data.Name)

              var expandedwindow = new google.maps.InfoWindow({
                content: '<div id="content">'+
                  '<p><b>'+ markerToAdd.title +'</b></p>'+
                  '</div>'
              });

              markerToAdd.data = data.Name;

              var json_data = {
                    csrf_token: $('meta[name="csrf-token"]').prop('content'),
                    data: markerToAdd.data[0]
              };
              markerToAdd.json_data = json_data
              var values = [];
              values.push(markerToAdd.json_data);
              async.each(values,
                function(value, callback){
                  markerToAdd.addListener('click', function() {
                    $.post("/get-info", markerToAdd.json_data)
                    .done(function(data) {
                        data = JSON.parse(data)
                        var addressWindow = new google.maps.InfoWindow({
                          content: '<div id="content">'+
                         '<p><b>'+ data.Address +'</b></p>'+
                         '</div>'
                         });
                        addressWindow.open(map, markerToAdd);
                    }).fail(function() {
                        console.log('fail');
                    });
                  });
                  callback();
               }, function(){
                markers.push(markerToAdd)
              }
            );
        }
        var mapViewButton = document.getElementById("map_view");
        var listViewButton = document.getElementById("list_view");

        mapViewButton.addEventListener('click', function() {
            $("#map").show();
            $("#list").hide();
        });

        listViewButton.addEventListener('click', function() {
            $("#map").hide();
            populateListDiv();
            $("#list").show();
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
            tableCell = document.createElement('td');
            $(tableCell).attr({
              'style': 'overflow:hidden;width:100%;height:100%;position:absolute'
            });
            tableCellBoldTitle = document.createElement('strong');
            tableCellNewline = document.createElement('br');
            tableCellInnerDiv = document.createElement('div');
            $(tableCellInnerDiv).attr({
              'style': 'width:50px;height:50px; text-align:right; float: right;'
            });
            tableCellImg = document.createElement('img');
            $(tableCellImg).attr({
              'src': 'static/images/red-dot.png',
              'style': 'width:50%;height:50%;'
            });      
            $(tableCellInnerDiv).append(tableCellImg);      
            $(tableCellBoldTitle).html(markerToShow.getTitle());
            $(tableCell).append(tableCellInnerDiv);
            //console.log(markerToShow)
            //console.log(markerToShow.infoWindow)
            $(tableCell).append(tableCellBoldTitle, tableCellNewline,
                                '<b>' + markerToShow.title + '</b><br>');
            
            $(table).append('<br>');
            $(table).append('<br>');
            $(table).append(tableCell);
          });
          $("#list").append(table);
      }        
