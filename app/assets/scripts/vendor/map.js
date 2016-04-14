      // This JS file is for the map and list view creations on the homepage of
      // the Maps4All site for the user
      // This example requires the Places library. Include the libraries=places
      // parameter when you first load the API. For example:
      // <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places">

      var map;
      var markers = [];

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
          var markerToAdd = new google.maps.Marker({
            map: map
          });

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
          markerToAdd.setIcon(/** @type {google.maps.Icon} */({
            url: place.icon,
            size: new google.maps.Size(71, 71),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(17, 34),
            scaledSize: new google.maps.Size(35, 35)
          }));
          markerToAdd.setPosition(place.geometry.location);
          markerToAdd.setVisible(true);
          markerToAdd.setTitle(place.name);
          markers.push(markerToAdd);
          marker = markerToAdd;

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
                console.log(markers[i]);
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
              markerToAdd.setTitle(data.Name)

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
                   var nameWindow = new google.maps.InfoWindow({
                          content: '<div id="content">'+
                         '<p>'+ json_data.data +'</p>'+
                         '</div>'
                         });
                  markerToAdd.addListener('mouseover', function() {
                       nameWindow.open(map, markerToAdd);
                    })
                  markerToAdd.addListener('mouseout', function() {
                       nameWindow.close();
                    })
                  markerToAdd.addListener('click', function() {
                    $.post("/get-info", markerToAdd.json_data)
                    .done(function(data) {
                        data = JSON.parse(data)
                        var addressWindow = new google.maps.InfoWindow({
                          content: '<div id="content">'+
                         '<p><b>'+  json_data.data +'</b></p>'+
                         '<p>'+ data.Address +'</p>'+
                         '<p>'+ data.Description +'</p>'+
                         '</div>',
                         maxWidth: 400
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

      function populateListDiv() {
          var markersToShow = [];
          $("#list").empty();
          var bounds = map.getBounds();
          for (var i = 0; i < markers.length; i++) {
              if (bounds.contains(markers[i].getPosition())) {
                  markersToShow.push(markers[i]);
              }
          }
          var table = $("<table border=1></table>");
          $.each(markersToShow, function(i, markerToShow) {
            tableCell = document.createElement('td');
            $(tableCell).attr({
              'style': 'overflow:hidden;width:100%;height:100%;position:absolute'
            });
            tableCellBoldTitle = document.createElement('strong');
            tableCellNewline = document.createElement('br');
            $(tableCellBoldTitle).html(markerToShow.getTitle());
            $(tableCell).append(tableCellBoldTitle, 
                                tableCellNewline, 
                                markerToShow.getLabel());
            tableCellInnerDiv = document.createElement('div');
            $(tableCellInnerDiv).attr({
              'style': 'width:50px;height:50px; text-align:right; float: right;'
            });
            tableCellImg = document.createElement('img');
            $(tableCellImg).attr({
              'src': markerToShow.getIcon().url,
              'style': 'width:50px;height:50px;'
            });
            $(tableCellInnerDiv).append(tableCellImg);
            $(tableCell).append(tableCellInnerDiv);
            table.append(tableCell);
          });
          $("#list").append(table);
      }        
