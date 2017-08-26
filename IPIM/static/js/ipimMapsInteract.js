$(document).ready(function () {

    var map;
    var start_point;
    var path = [];
    var acc_date;
    var txt_1, txt_2, txt_3, txt_4, txt_5;
    var step_1, step_2, step_3, step_4, step_5, step_6;
    var ctrl_rm_last_inter;
    var answers = [];
    var state_city_st_cst = "";

    var gender = "";
    var age = 0;
    var ethnicity = "";
    var race = "";

    // for time spent for answering the report
    var time_start_to_report = (new Date).getTime();

    // for recording which step the user quited for incomplete datasets
    var cur_step = 0;
    var max_step = 0;
    ga('send', 'event', {
            'eventCategory': 'maxstep',
            'eventAction': max_step.toString()
        }
    );
    // ga('send', 'maxstep', max_step);
    //  0,            1,        2,      3,        4,        5,          6,          7
    //  consent form, locate,  spot,    draw,    time,    questions, personalInfo, submitted

    /*
    var inFormOrLink = false;
    $('a').on('click', function() { inFormOrLink = true; });
    $('form').on('submit', function() { inFormOrLink = true; });

    $(window).on("beforeunload", function() {
        if(inFormOrLink) {
            return null;
        }
        else {
            return null;
            // return "Are you sure?";
        }
    });
    */

    map = new GMaps({
    el: '#map',
    lat: 40.74959782183326,
    lng: -73.98781299591064,
    zoom: 14,
    clickableIcons: false
    });

  ins_box = document.getElementById("ins_box");
  /*
  txt_1 = document.createTextNode("Step 1: Time the accident occured\nTell us the Month/Year in which you were injured. Press \"Next\" to continue.");
  txt_2 = document.createTextNode("Step 2: Locate the area near where you were hit.\nYou can either type in the state, city, street and nearest cross-street where you were hit by a vehicle to locate the maps. Or if your current location is near the location where you were hit, you may use \"locate me\" to let the browser use your current position. After the area is located, press \"Next\" to continue.");
  txt_3 = document.createTextNode("Step 3: Locate the spot of collision\nUse the mouse to place the pin at the place where you were hit by a vehicle. You can edit the spot as many times as you want. Press \"Next\" when finishing.");
  txt_4 = document.createTextNode("Step 4: Draw the route\nUse the cross-hairs tool to map out the route you walked along before you were hit.” Move the crosshair to the previous intersection and click the mouse and then the next intersection and click the mouse and so on. You can delete a most recent intersection that you draw by pressing \"remove last intersection\" on the map. Press \"Next\" after finishing.");
  txt_5 = document.createTextNode("Step 5: Collision Information\nPlease press \"Next\" after answering all the questions below.");
  txt_6 = document.createTextNode("Step 6: A little bit about youserlf\nPlease answer them and then press \"Done\"");
  // txt_7 = document.createTextNode("Review: Here is all the information about this accident.\nPress \"Submit\"");
  txt_8 = document.createTextNode("Completed: Your report is submitted.\nThank you!");
  */
  step_1 = document.getElementById('step1');
  step_2 = document.getElementById('step2');
  step_3 = document.getElementById('step3');
  step_4 = document.getElementById('step4');
  step_5 = document.getElementById('step5');
  step_6 = document.getElementById('step6');

  // step1 starts
  step_1.style.display = 'block';
  // ins_box.innerText = txt_1.textContent;

  var now = new Date(),
    maxDate = now.toLocaleDateString().substring(0,10);
  // alert(maxDate);
  var input_date = new Date();

  var state = "";
  var city = "";
  var street = "";
  var cross_street = "";

  function acc_spot_start() // take step element for html element transform
  {
      map.setOptions({draggableCursor:'url(../static/cursors/Locate.cur), auto'});

      GMaps.on('click', map.map, function(event) {
        // var index = map.markers.length;
        map.removeMarkers();
        var lat = event.latLng.lat();
        var lng = event.latLng.lng();

        start_point = [lat, lng];
        map.addMarker({
          lat: lat,
          lng: lng,
          title: 'Marker',
          infoWindow: {
            content : "This is a spot of the accident: \n".concat([lat, lng])
          }
        });

        map.setOptions({draggableCursor:''});

        GMaps.off('click', map.map, function(event) {
            event.preventDefault();
        });

        /*************************** step 3:  Draw the route ***********************************/
        // hide step3, start step4
        // step_2.style.display = 'none';
        // step_3.style.display = 'block';
        $("#step2").fadeOut(function(){$("#step3").fadeIn();});
        draw_route_start();

      });
  };

  function draw_route_start()
  {
      map.setOptions({draggableCursor:'url(../static/cursors/Locate0.cur), auto'});

      if(path.length == 0) path = [start_point];

      ctrl_rm_last_inter = map.addControl({
          position: 'TOP_RIGHT',
          content: 'remove last intersection',
          style: {
            textAlign: 'center',
            height: '30px',
            lineHeight: '18px',
            fontSize : '16px',
            margin: '5px',
            padding: '1px 6px',
            border: 'solid 4px #717B87',
            background: '#fff'
          },
          events: {
            click: function(){
              if (path.length>1) {
                  path.pop();
                  map.removePolylines();
                  drawRoute(path, map);
              }
            }
          }
       });

      GMaps.on('click', map.map, function(event) {
        var lat = event.latLng.lat();
        var lng = event.latLng.lng();
        path.push([lat, lng]);

        drawRouteOneStep(path, map);
      });
  };

  function draw_route_end()
  {
      if(path.length == 1) {
          alert("Please draw the route with at least one intersection before the accident.");
          return -1; // fail
      }
      // document.getElementById('map').style.cursor='url(Pencil.cur), auto';
      map.setOptions({draggableCursor:''});
      GMaps.off('click', map.map, function(event) {
          event.preventDefault();
      });

      map.removeControl(ctrl_rm_last_inter);
      return 0; // success
  };

  // back buttons
  $('#step2_back').click(function(e){
      e.preventDefault();
      // step_2.style.display = 'none';
      // step_1.style.display = 'block';
      $("#step2").fadeOut();
      step_2.style.display = 'none';
      $("#step1").fadeIn();
      // clean start_point
      start_point = null;
      map.removeMarkers();
      // disable locate cursor
      map.setOptions({draggableCursor:''});

      GMaps.off('click', map.map, function(event) {
          event.preventDefault();
      });
  });
  $('#step3_back').click(function(e){
      e.preventDefault();
      // step_3.style.display = 'none';
      // step_2.style.display = 'block';
      $("#step3").fadeOut();
      step_3.style.display = 'none';
      $("#step2").fadeIn();
      // clean crosshair cursor, clean remove last button, clean path
      map.setOptions({draggableCursor:''});
      GMaps.off('click', map.map, function(event) {
          event.preventDefault();
      });
      map.removeControl(ctrl_rm_last_inter);
      path = [];
      // clean route stroke on map
      map.removePolylines();
      // enable locate cursor
      acc_spot_start();
  });
  $('#step4_back').click(function(e){
      e.preventDefault();
      // step_4.style.display = 'none';
      // step_3.style.display = 'block';
      $("#step4").fadeOut();
      step_4.style.display = 'none';
      $("#step3").fadeIn();
      // enable crosshair cursor, enable remove last button
      draw_route_start();
  });
  $('#step5_back').click(function(e){
      e.preventDefault();
      // step_5.style.display = 'none';
      // step_4.style.display = 'block';
      $("#step5").fadeOut();
      step_5.style.display = 'none';
      $("#step4").fadeIn();
  });
  $('#step6_back').click(function(e){
      e.preventDefault();
      // step_6.style.display = 'none';
      // step_5.style.display = 'block';
      $("#step6").fadeOut();
      step_6.style.display = 'none';
      $("#step5").fadeIn();
  });

  /*************************** step 1: Locate the area ***********************************/
  $('#locate_me_button').click(function(e){
      e.preventDefault();
      // alert("Locating! Please allow the browser to locate.");
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
        }
      });
  });

  $('#geocoding_form').submit(function(e){
    e.preventDefault();
    state = $('#state').val().trim();
    city = $('#city').val().trim();
    street = $('#street').val().trim();
    cross_street = $('#cross_street').val().trim();

    var address_list = [state, ', ', city, ', ', street, ', ', cross_street];
    var address_in = "".concat(...address_list);
    // alert(address_in);
    state_city_st_cst = address_in; // "state, city, street, cross_street"
    // e.g. Main Street & everett st, Lafayette, IN
    address_list = [street, ' & ', cross_street, ', ', city, ', ', state];
    address_in = "".concat(...address_list);
    GMaps.geocode({
      address: address_in,
      callback: function(results, status){
        if(status=='OK'){
          var latlng = results[0].geometry.location;
          map.setCenter(latlng.lat(), latlng.lng());
          map.setZoom(17);
        }
      }
    });
  });

  /*************************** step 2: acc spot ***********************************/
  $('#step1_next').click(function(e) {
      e.preventDefault();
      cur_step = 2;
      if(cur_step > max_step) {
          max_step = cur_step;
          ga('send', 'event', {
                  'eventCategory': 'maxstep',
                  'eventAction': max_step.toString()
              }
          );
          //ga('send', 'maxstep', max_step);
      }
      // hide step2, start step3
      // step_1.style.display = 'none';
      // step_2.style.display = 'block';
      $("#step1").fadeOut(function(){$("#step2").fadeIn();});
      acc_spot_start();
      cur_step = 3;
      if(cur_step > max_step) {
          max_step = cur_step;
          ga('send', 'event', {
                  'eventCategory': 'maxstep',
                  'eventAction': max_step.toString()
              }
          );
          // ga('send', 'maxstep', max_step);
      }
      // ins_box.innerText = txt_3.textContent;
  });

  /*************************** step 3.1: route confirm ***********************************/
  $('#draw_end').click(function(e){
      e.preventDefault();
      // alert("end drawing!");
      if(draw_route_end() == -1) return;
      // hide step4, start step5
      // step_3.style.display = 'none';
      // step_4.style.display = 'block';
      $("#step3").fadeOut(function(){$("#step4").fadeIn();});
      cur_step = 4;
      if(cur_step > max_step) {
          max_step = cur_step;
          ga('send', 'event', {
                  'eventCategory': 'maxstep',
                  'eventAction': max_step.toString()
              }
          );
          // ga('send', 'maxstep', max_step);
      }
  });

  /*************************** step 4: date ***********************************/
  $('#date_form').submit(function(e){
      e.preventDefault();

      var acc_date_t = document.getElementById("accident_date");
      if(acc_date_t.value.length==0) {
          alert("Please input Month/Year.");
          return;
      }
      // alert(acc_date_t.value);
      var monthandyear = acc_date_t.value.split(" ");
      var year = monthandyear[1].trim();
      // alert(parseInt(year));
      var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      var months_1 = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
      var month = months_1.indexOf(monthandyear[0].trim());
      if(month == -1)
        month = months.indexOf(monthandyear[0].trim());
      // alert(month);
      if(month == -1) {
          alert('Please use the datepicker to select month/year. The format must be "mmm yyyy". Or you can use the correct spelling of a month such as "January 2015".');
          return;
      }

      input_date = new Date(parseInt(year), parseInt(month), 1);

      // alert("date is "+input_date);
      if(input_date.getTime() > now.getTime()) {
          alert("Date is in the future.");
          return;
      }
      acc_date = input_date;

      // step_4.style.display = 'none';
      // step_5.style.display = 'block';
      $("#step4").fadeOut(function(){$("#step5").fadeIn();});
      cur_step = 5;
      if(cur_step > max_step) {
          max_step = cur_step;
          ga('send', 'event', {
                  'eventCategory': 'maxstep',
                  'eventAction': max_step.toString()
              }
          );
          // ga('send', 'maxstep', max_step);
      }

  });

  /*************************** step 5: questions ***********************************/
  $('#tell_end').click(function(e){
      e.preventDefault();
      // alert("tell ending");

      var answer_list;
      var answer_value;
      var flag_answered_all = true;
      for(var j = 1; j<=6; j++) {
          answer_list = document.getElementsByName('question'+j);
          var j_answerd = false;
          for(var i = 0; i < answer_list.length; i++){
              if(answer_list[i].checked){
                  answer_value = answer_list[i].value;
                  answers.push(answer_value);
                  j_answerd = true;
                  // alert("question"+j+" answer is "+answer_value);
              }
          }
          if(j_answerd) {
              j_answerd = false;
          }
          else {
              answers.push("");
              flag_answered_all = false;
          }
      }
      // alert(answers.length);

      if(!flag_answered_all) {
          // alert("Please answer all the questions.");
          $('#confirmBox').css('display', 'block');
          flag_answered_all = true;
          return;
      }

      // hide step5, start step6
      // step_5.style.display = 'none';
      // step_6.style.display = 'block';
      $("#step5").fadeOut(function(){$("#step6").fadeIn();});
      // ins_box.innerText = txt_6.textContent;
      cur_step = 6;
      if(cur_step > max_step) {
          max_step = cur_step;
          ga('send', 'event', {
                  'eventCategory': 'maxstep',
                  'eventAction': max_step.toString()
              }
          );
          // ga('send', 'maxstep', max_step);
      }
  });

  doConfirm("Some questions are not answered. Press \"Answer\" to answer them or press \"Next\" to go to next section.",
            function yes() {
                // continue_anwser
                // alert("yes is pressed");
                return;
            },
            function no() {
                // not continue_anwser
                // alert("no is pressed");
                // hide step5, start step6
                // step_5.style.display = 'none';
                // step_6.style.display = 'block';
                $("#step5").fadeOut(function(){$("#step6").fadeIn();});
                cur_step = 6;
                if(cur_step > max_step) {
                    max_step = cur_step;
                    ga('send', 'event', {
                            'eventCategory': 'maxstep',
                            'eventAction': max_step.toString()
                        }
                    );
                    // ga('send', 'maxstep', max_step);
                }
            }
  );

  /*************************** step 6: personal info ***********************************/

  $('#person_info_form').submit(function(e){
      e.preventDefault();
      // inFormOrLink = true;
      // hide step6, start step7
      // step_6.style.display = 'none';
      $("#step6").fadeOut();
      cur_step = 7;
      if(cur_step > max_step) {
          max_step = cur_step;
          ga('send', 'event', {
                  'eventCategory': 'maxstep',
                  'eventAction': max_step.toString()
              }
          );
          // ga('send', 'maxstep', max_step);
      }
      // ins_box.innerText = txt_8.textContent;

      gender = $('#gender').val().trim();
      var age_element = document.getElementById('age');
      if(age_element.value == ""){
          age = -1;
      }
      else {
          age = $('#age').val();
      }
      ethnicity = $('#ethn').val().trim();
      race = $('#race').val().trim();

      var answer_form = document.forms["answer_form"];

      for(var j = 1; j<=6; j++) {
          an_answer = answer_form['answer'+j];
          an_answer.value = answers[j-1];
          // alert(an_answer.value);
      }
      answer_form['answer_route'].value = path.toString();
      answer_form['answer_state_city_st_cst'].value = state_city_st_cst;
      answer_form['answer_date'].value = acc_date.getTime();
      answer_form['answer_gender'].value = gender;
      answer_form['answer_ethnicity'].value = ethnicity;
      answer_form['answer_race'].value = race;
      answer_form['answer_age'].value = age;
      sessionStorage.setItem('path', path);

      // for time spent
      var time_end_to_report = (new Date).getTime();
      var time_interval_in_second = parseInt((time_end_to_report - time_start_to_report) / 1000);
      answer_form['timespent'].value = time_interval_in_second;

      // for refer url
      var referURL = document.referrer;
      answer_form['referURL'].value = referURL;


      // for submit
      var hostname = ""+window.location.hostname;
      if(hostname == "petercanmakit.github.io" || hostname == "") {
          // var child_thankspage = window.open("thanks.html");
          window.location.assign("thanks.html");
      }
      else answer_form.submit(); // server will ask it goto thanks screen
      // alert("Submitting drawing!");
      // hide step7

      // ins_box.innerText = txt_8.textContent;


      /*
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
                  <td>Month/Year</td>                   \
                  <td>'+ (acc_date.getMonth()+1)+'/'+(acc_date.getYear()+1900) +'</td>     \
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
                  <td>State</td>                        \
                  <td>'+ state +'</td>                  \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">4.5</th>                \
                  <td>City</td>                         \
                  <td>'+ city +'</td>                   \
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
                  <th scope="row">7.1</th>                \
                  <td>You were hit during </td>           \
                  <td>'+ answers[1] +'</td>         \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">8</th>                \
                  <td>Was a police report filed at the scene of the collision?</td>           \
                  <td>'+ answers[2] +'</td>         \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">9</th>                \
                  <td>Were you provided medical evaluation or care at the scene of the collision?</td>           \
                  <td>'+ answers[3] +'</td>         \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">10</th>                \
                  <td>Were you taken from the scene of the collision to an emergency room or hospital?</td>           \
                  <td>'+ answers[4] +'</td>         \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">11</th>                \
                  <td>Did you later seek medical care for injuries occurring from the collision?</td>           \
                  <td>'+ answers[5] +'</td>         \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">12</th>                \
                  <td>Gender: </td>           \
                  <td>'+ gender +'</td>         \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">13</th>                \
                  <td>Age:</td>           \
                  <td>'+ age +'</td>         \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">14</th>                \
                  <td>Ethnicity</td>           \
                  <td>'+ ethnicity +'</td>         \
                </tr>                                   \
                <tr>                                    \
                  <th scope="row">15</th>                \
                  <td>race</td>           \
                  <td>'+ race +'</td>         \
                </tr>                                   \
              </tbody>                                  \
            </table>                                    \
          '
      );
      ins_box.innerText = txt_7.textContent;
      */
  });



});

var drawRouteOneStep = function(path, map) {
    var walk = path[path.length-2];
    var walk_next = path[path.length-1];

    map.drawRoute({
        origin: [walk[0], walk[1]],
        destination: [walk_next[0], walk_next[1]],

        strokeColor: '#131540',
        strokeOpacity: 0.6,
        strokeWeight: 6
    });
    walk = walk_next;
};

var drawRoute = function(path, map) {
    var start_point = path[0];
    var walk = start_point;
    var walk_next;
    for(var j = 1; j<path.length; j++) {
        walk_next = path[j];
        map.drawRoute({
            origin: [walk[0], walk[1]],
            destination: [walk_next[0], walk_next[1]],
            // travelMode: 'driving', // default walking
            strokeColor: '#131540',
            strokeOpacity: 0.6,
            strokeWeight: 6
        });
        walk = walk_next;
    }
};

function doConfirm(msg, yesFn, noFn)
{
    var confirmBox = $("#confirmBox");
    confirmBox.find(".message").text(msg);
    confirmBox.find(".yes,.no").click(function()
    {
        confirmBox.hide();
    });
    confirmBox.find(".yes").click(yesFn);
    confirmBox.find(".no").click(noFn);
    // confirmBox.show();
};
