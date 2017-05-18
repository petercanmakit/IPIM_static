var map;
var start_point;
var path;
var acc_date;
var txt_1, txt_2, txt_3, txt_4, txt_5;
var step_1, step_2, step_3, step_4, step_5;
var ctrl_rm_last_inter;

$(document).ready(function () {
    var map = new GMaps({
    el: '#map',
    lat: 40.80754030525040,
    lng: -73.96257877349854
  });

  ins_box = document.getElementById("ins_box");
  txt_1 = document.createTextNode("Step 1: Time the accident occured\nTell us the date on which you were injured. (mm/dd/yyyy) Press \"Next\" to continue.");
  txt_2 = document.createTextNode("Step 2: Locate the area\nYou can either type in the city and street and nearest cross-street where you were hit by a vehicle. Or if your current location is around the spot, you may use \"locate me\" to let the browser use your current position. After the area is located, press \"Next\" to continue.");
  txt_3 = document.createTextNode("Step 3: Locate the spot of collision\nUse the mouse to place the pin at the place where you were hit by a vehicle. You can edit the spot as many times as you want. Press \"Next\" when finishing.");
  txt_4 = document.createTextNode("Step 4: Draw the route\nUse the pencil tool to draw lines on the map showing us the streets you walked along before you were hit. Move the pencil to the previous intersection and click the mouse and then the next intersection and click the mouse and so on. You can delete a most recent intersection that you draw by pressing \"remove last intersection\" on the map. Press \"Next\" after finishing.");
  txt_5 = document.createTextNode("Step 5: Submit your route\nIf your toute is all set, please press \"Submit\"");
  txt_6 = document.createTextNode("Completed: Your route is submitted.\nThank you!");
  step_1 = document.getElementById('step1');
  step_2 = document.getElementById('step2');
  step_3 = document.getElementById('step3');
  step_4 = document.getElementById('step4');
  step_5 = document.getElementById('step5');

  // step1 starts
  step_1.style.display = 'block';
  ins_box.innerText = txt_1.textContent;

  $('#date_form').submit(function(e){
      e.preventDefault();
      acc_date = document.getElementById("accident_date");
      if(acc_date.value.length == 0) {
          alert("Please input date.");
          return;
      }
      alert("date is "+acc_date.value);

      // hide step1, start step2
      step_1.style.display = 'none';
      step_2.style.display = 'block';
      ins_box.innerText = txt_2.textContent;
  });

  $('#locate_me_button').click(function(e){
      e.preventDefault();
      alert("Locating! Please allow the browser to locate.");
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

  $('#step2_next').click(function(e) {
      e.preventDefault();
      // hide step2, start step3
      step_2.style.display = 'none';
      step_3.style.display = 'block';
      ins_box.innerText = txt_3.textContent;

      map.setOptions({draggableCursor:'url(static/cursors/Locate.cur), auto'});

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
            content : "This is a spot of the accident: \n".concat([lat, lng])
          }
        });
      });
  })

  $('#place_pin_end').click(function(e){
      e.preventDefault();
      if(start_point == null) {
          alert("Please set the spot of accident on the map.");
          return;
      }
      // alert("Spot set!");
      map.setOptions({draggableCursor:''});

      GMaps.off('click', map.map, function(event) {
          event.preventDefault();
      });

      // hide step3, start step4
      step_3.style.display = 'none';
      step_4.style.display = 'block';
      ins_box.innerText = txt_4.textContent;

      // alert("start drawing!");
      map.setOptions({draggableCursor:'url(static/cursors/Pencil.cur), auto'});

      path = [start_point];

      ctrl_rm_last_inter = map.addControl({
          position: 'BOTTOM_LEFT',
          content: 'remove last intersection',
          style: {
            margin: '5px',
            padding: '1px 6px',
            border: 'solid 1px #717B87',
            background: '#fff'
          },
          events: {
            click: function(){
              if (path.length>1) {
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
      // alert("end drawing!");
      if(path.length == 1) {
          alert("Please draw the route with at least one intersection before the accident.");
          return;
      }
      // document.getElementById('map').style.cursor='url(Pencil.cur), auto';
      map.setOptions({draggableCursor:''});
      GMaps.off('click', map.map, function(event) {
          event.preventDefault();
      });

      map.removeControl(ctrl_rm_last_inter);
      // hide step4, start step5
      step_4.style.display = 'none';
      step_5.style.display = 'block';
      ins_box.innerText = txt_5.textContent;
  });

  $('#submit_route').click(function(e){
      e.preventDefault();
      alert("Submitting drawing!");
      // hide step5
      step_5.style.display = 'none';
      ins_box.innerText = txt_6.textContent;

      $('#path_print').append('<p>'+'Date is '+acc_date.value+'</p>');
      $('#path_print').append('<p>'+'Spot is '+path[0]+'</p>');
      $('#path_print').append('<p>'+'Route is '+'</p>');
      var s;
      for (s of path) {
          $('#path_print').append('<p>'+s+'</p>');
      }
  });

});
