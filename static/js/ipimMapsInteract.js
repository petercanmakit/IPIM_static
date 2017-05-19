var map;
var start_point;
var path;
var acc_date;
var txt_1, txt_2, txt_3, txt_4, txt_5;
var step_1, step_2, step_3, step_4, step_5;
var ctrl_rm_last_inter;
var answers = [];
var st_cst_city = "";

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
  txt_5 = document.createTextNode("Step 5: Other information\nPlease press \"Finish\" after answering all the questions below.");
  txt_6 = document.createTextNode("Review: Here is all the information about this accident.\nPress \"Submit\"");
  txt_7 = document.createTextNode("Completed: Your route is submitted.\nThank you!");
  step_1 = document.getElementById('step1');
  step_2 = document.getElementById('step2');
  step_3 = document.getElementById('step3');
  step_4 = document.getElementById('step4');
  step_5 = document.getElementById('step5');
  step_6 = document.getElementById('step6');

  // step1 starts
  step_1.style.display = 'block';
  ins_box.innerText = txt_1.textContent;

  var now = new Date(),
    maxDate = now.toLocaleDateString().substring(0,10);
  // alert(maxDate);
  var input_date = new Date();

  var city = "";
  var street = "";
  var cross_street = "";

  $('#accident_date').prop('max', maxDate);

  $('#date_form').submit(function(e){
      e.preventDefault();
      acc_date = document.getElementById("accident_date");
      if(acc_date.value.length == 0) {
          alert("Please input date.");
          return;
      }
      // alert("date is "+acc_date.value);
      acc_date_str = ""+acc_date.value
      if(acc_date_str.includes("/")) {
          // safari
          acc_date_strs = acc_date_str.split("/");
          mm = acc_date_strs[0];
          dd = acc_date_strs[1];
          yyyy = acc_date_strs[2];
      }
      else {
          // chrome
          acc_date_strs = acc_date_str.split("-");
          yyyy = acc_date_strs[0];
          mm = acc_date_strs[1];
          dd = acc_date_strs[2];
      }
      input_date = new Date(yyyy, mm-1, dd);
      if(input_date.getTime() > now.getTime()) {
          alert("Date is in the future.");
          return;
      }

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
    city = $('#city').val().trim();
    street = $('#street').val().trim();
    cross_street = $('#cross_street').val().trim();
    var address_list = [street, ', ', cross_street, ', ', city];
    var address_in = "".concat(...address_list);
    // alert(address_in);
    st_cst_city = address_in; // "street, cross_street, city"
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
      map.setOptions({draggableCursor:'url(../static/cursors/Pencil.cur), auto'});

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

  $('#tell_end').click(function(e){
      e.preventDefault();
      // alert("tell ending");

      var answer_list;
      var answer_value;
      for(var j = 1; j<6; j++) {
          answer_list = document.getElementsByName('question'+j);
          for(var i = 0; i < answer_list.length; i++){
              if(answer_list[i].checked){
                  answer_value = answer_list[i].value;
                  answers.push(answer_value);
                  // alert("question"+j+" answer is "+answer_value);
              }
          }
      }
      // alert(answers.length);
      if(answers.length!=5) {
          alert("Please answer all the questions.");
          for (var i = answers.length; i > 0; i--) {
              answers.pop();
          }
          return;
      }

      // hide step5, start step6
      step_5.style.display = 'none';
      step_6.style.display = 'block';
      var path_with_linebreak = [];
      for(var a_spot of path) {
          path_with_linebreak.push(a_spot+"\n");
      }
      $('#content_to_submmit').append(
          '                                             \
          <table class="table table-striped">           \
              <tbody>                                   \
                <tr>                                    \
                  <th scope="row">1</th>                \
                  <td>Date</td>                         \
                  <td>'+ acc_date.value +'</td>     \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">2</th>                \
                  <td>Accident spot</td>                \
                  <td>'+ path[0] +'</td>            \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">3</th>                \
                  <td>Route before accident</td>        \
                  <td>'+ path_with_linebreak.toString() +'</td>        \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">4</th>                \
                  <td>City</td>                         \
                  <td>'+ city +'</td>               \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">5</th>                \
                  <td>Street</td>                       \
                  <td>'+ street +'</td>             \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">6</th>                \
                  <td>Cross Street</td>                 \
                  <td>'+ cross_street +'</td>       \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">7</th>                \
                  <td>You were hit by a </td>           \
                  <td>'+ answers[0] +'</td>         \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">8</th>                \
                  <td>Was a police report filed at the scene of the collision?</td>           \
                  <td>'+ answers[1] +'</td>         \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">9</th>                \
                  <td>Were you provided medical evaluation or care at the scene of the collision?</td>           \
                  <td>'+ answers[2] +'</td>         \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">10</th>                \
                  <td>Were you taken from the scene of the collision to an emergency room or hospital?</td>           \
                  <td>'+ answers[3] +'</td>         \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">11</th>                \
                  <td>Did you later seek medical care for injuries occurring from the collision?</td>           \
                  <td>'+ answers[4] +'</td>         \
                </tr>                                   \
              </tbody>                                  \
            </table>                                    \
          '
      );
      ins_box.innerText = txt_6.textContent;
  });

  $('#submit_route').click(function(e){
      e.preventDefault();
      var answer_form = document.forms["answer_form"];

      for(var j = 1; j<=5; j++) {
          an_answer = answer_form['answer'+j];
          an_answer.value = answers[j-1];
          // alert(an_answer.value);
      }
      answer_form['answer_route'].value = path.toString();
      answer_form['answer_st_cst_city'].value = st_cst_city;
      answer_form['answer_date'].value = input_date.getTime();

      answer_form.submit();
      // alert("Submitting drawing!");
      // hide step5
      step_6.style.display = 'none';
      ins_box.innerText = txt_7.textContent;
  });

});
