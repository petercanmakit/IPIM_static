$(document).ready(function () {
    var path = []; // [[lat, lng], [lat, lng], ...]
    var map;

    // path = [[40.763836272185216,-73.9619779586792], [40.749922934625694,-73.97219181060791 ], [40.75336903249924,-73.9813756942749], [40.7649414124685,-73.97244930267334]];
    var path_str = sessionStorage.getItem('path');

    var path_strs = path_str.split(",");

    for(var i=0; i<path_strs.length; i+=2) {
        var lati = parseFloat(path_strs[i]);
        var lngi = parseFloat(path_strs[i+1]);
        path.push([lati, lngi]);
    }

    map = presentRoute(path, '#map');

    var print_btn = document.getElementById("shareEmail");
    print_btn.onclick = function() {myFunction()};

    function myFunction() {
        ga('send', 'social', 'Email', 'send', 'https://petercanmakit.github.io/IPIM/');
        window.open('mailto:test@example.com?subject=Use%20I-PIM%20to%20report%20a%20collision&body=https%3A%2F%2Fpetercanmakit.github.io%2FIPIM%2F%2E%20I%20have%20reported%20a%20collision%20on%20I-PIM%2C%20which%20contributes%20to%20the%20research%20at%20Department%20of%20Epidemiology%2CCUMC%2E');
        alert("email msg sent to ga.")
    }


    $('#mapPrint').on('click',
        // printAnyMaps :: _ -> HTML
        function printAnyMaps() {
          var $body = $('body');
          var $mapContainer = $('#map');
          var $mapContainerParent = $mapContainer.parent();
          var $printContainer = $('<div style="position:relative;">');

          $printContainer
            .height($mapContainer.height())
            .append($mapContainer)
            .prependTo($body);

          var $content = $body
            .children()
            .not($printContainer)
            .not('script')
            .detach();

          /**
           * Needed for those who use Bootstrap 3.x, because some of
           * its `@media print` styles ain't play nicely when printing.
           */
          var $patchedStyle = $('<style media="print">')
            .text(
              'img { max-width: none !important; }' +
              'a[href]:after { content: ""; }'
            )
            .appendTo('head');

          window.print();

          $body.prepend($content);
          $mapContainerParent.prepend($mapContainer);

          $printContainer.remove();
          $patchedStyle.remove();
      });

});

// take the path and present on the map
var presentRoute = function(path, mapElement) {
    var lat_lng_object_array = [];

    var start_point = [path[0][0], path[0][1]]; // [lat, lng]
    // compute center
    var lat_min = start_point[0];
    var lat_max = start_point[1];
    var lng_min = start_point[0];
    var lng_max = start_point[1];
    for(var cord of path) {
        lat_lng_object_array.push(new google.maps.LatLng(cord[0], cord[1]));
        if(lat_max < cord[0])
            lat_max = cord[0];
        if(lat_min > cord[0])
            lat_min = cord[0];
        if(lng_max < cord[1])
            lng_max = cord[1];
        if(lng_min > cord[1])
            lng_min = cord[1];
    }
    var center_lat = (lat_max+lat_min)/2;
    var center_lng = (lng_max+lng_min)/2;

    var map = new GMaps({
    el: mapElement,
    lat: center_lat,
    lng: center_lng
    });
    map.setCenter(center_lat, center_lng);
    map.fitLatLngBounds(lat_lng_object_array);
    map.addMarker({
      lat: start_point[0],
      lng: start_point[1],
      title: 'Accident spot',
      infoWindow: {
        content : "This is a spot of the accident: \n".concat([start_point[0], start_point[1]])
      }
    });
    drawRoute(path, map);
    return map;
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
