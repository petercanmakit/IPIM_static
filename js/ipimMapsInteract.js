var map;
var start_point;
var path;

$(document).ready(function(){
  var map = new GMaps({
    el: '#map',
    lat: -12.043333,
    lng: -77.028333
  });

  $('#locate_me_button').click(function(e){
      e.preventDefault();
      alert("clicked!");
      GMaps.geolocate({
        success: function(position){
          map.setCenter(position.coords.latitude, position.coords.longitude);
        },
        error: function(error){
          alert('Geolocation failed: '+error.message);
        },
        not_supported: function(){
          alert("Your browser does not support geolocation");
        },
        always: function(){
          alert("You are located!");
        }
      });
  });

  $('#geocoding_form').submit(function(e){
    e.preventDefault();
    var city = $('#city').val().trim();
    var street = $('#street').val().trim();
    var cross_street = $('#cross_street').val().trim();
    var address_list = [street, ', ', cross_street, ', ', city];
    var address_in = "".concat(...address_list);
    alert(address_in);
    GMaps.geocode({
      address: address_in,
      callback: function(results, status){
        if(status=='OK'){
          var latlng = results[0].geometry.location;
          map.setCenter(latlng.lat(), latlng.lng());
          map.addMarker({
            lat: latlng.lat(),
            lng: latlng.lng()
          });
        }
      }
    });
  });

  $('#place_pin').click(function(e){
      e.preventDefault();
      alert("put a pin");
      // document.getElementById('map').style.cursor='url(Pencil.cur), auto';
      map.setOptions({draggableCursor:'url(../static/cursors/Locate.cur), auto'});

      GMaps.on('click', map.map, function(event) {
        // var index = map.markers.length;
        map.removeMarkers();
        var lat = event.latLng.lat();
        var lng = event.latLng.lng();

        // var template = $('#edit_marker_template').text();

        // var content = template.replace(/{{index}}/g, index).replace(/{{lat}}/g, lat).replace(/{{lng}}/g, lng);
        start_point = [lat, lng];
        map.addMarker({
          lat: lat,
          lng: lng,
          title: 'Marker',
          infoWindow: {
            content : "this is a spot of the accident: \n".concat([lat, lng])
          }
        });
      });
  });

  $('#place_pin_end').click(function(e){
      e.preventDefault();
      alert("Spot set!");
      map.setOptions({draggableCursor:''});

      GMaps.off('click', map.map, function(event) {
          event.preventDefault();
      });

  });

  $('#draw_start').click(function(e){
      e.preventDefault();
      alert("start drawing!");
      map.setOptions({draggableCursor:'url(../static/cursors/Pencil.cur), auto'});

      path = [start_point];

      map.addControl({
          position: 'top_right',
          content: 'remove last intersection',
          style: {
            margin: '5px',
            padding: '1px 6px',
            border: 'solid 1px #717B87',
            background: '#fff'
          },
          events: {
            click: function(){
              if (path.length>0) {
                  path.pop();
                  map.removePolylines();
                  map.drawPolyline({
                    path: path,
                    strokeColor: '#131540',
                    strokeOpacity: 0.6,
                    strokeWeight: 6
                  });
              }
            }
          }
       });

      GMaps.on('click', map.map, function(event) {
        var lat = event.latLng.lat();
        var lng = event.latLng.lng();
        path.push([lat, lng]);

        map.removePolylines();
        map.drawPolyline({
          path: path,
          strokeColor: '#131540',
          strokeOpacity: 0.6,
          strokeWeight: 6
        });

      });

  });

  $('#draw_end').click(function(e){
      e.preventDefault();
      alert("end drawing!");
      // document.getElementById('map').style.cursor='url(Pencil.cur), auto';
      map.setOptions({draggableCursor:''});
      GMaps.off('click', map.map, function(event) {
          event.preventDefault();
      });
  });

  $('#submit_route').click(function(e){
      e.preventDefault();
      alert("Submitting drawing!");
      var s;
      for (s of path) {
          $('#path_print').append('<p>'+s+'</p>');
      }
  });

});
