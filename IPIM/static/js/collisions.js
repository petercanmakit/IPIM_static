$(document).ready(function () {
    var path_element = document.getElementById("path_str");
    var path_str; // [40.7657215004278, -73.9642524719238, 40.764421348742, -73.9589309692383]
    if (path_element != null) {
        path_str = path_element.innerHTML;
    }
    else {
        return;
    }

    var path = [];
    // var path = []; // [[lat, lng], [lat, lng], ...]

    // path = [[40.763836272185216,-73.9619779586792], [40.749922934625694,-73.97219181060791 ], [40.75336903249924,-73.9813756942749], [40.7649414124685,-73.97244930267334]];

    var path_strs = path_str.replace("[", "").replace("]", "").split(", ");

    for(var i=0; i<path_strs.length; i+=2) {
        var lati = parseFloat(path_strs[i]);
        var lngi = parseFloat(path_strs[i+1]);
        path.push([lati, lngi]);
    }

    map = presentRoute(path, '#map');

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

var drawWorldMap = function(spots, cids, mapElement, cluserImgPath) {

    var lat_lng_object_array = [];
    var map = new GMaps({
        el: document.getElementById(mapElement),
        lat: 40.763836272185216,
        lng: -73.9619779586792
    });

    var start_point = [spots[0][0], spots[0][1]]; // [lat, lng]
    // compute center
    var lat_min = start_point[0];
    var lat_max = start_point[1];
    var lng_min = start_point[0];
    var lng_max = start_point[1];
    i = 0;

    var markers = [];

    for(var cord of spots) {

        var latLng = new google.maps.LatLng(cord[0], cord[1]);
        var marker = new google.maps.Marker({
            'position': latLng,
            map: map.map,
            title: "cid: " + cids[i]
        });
        var contentString = '<div id="content'+cids[i]+'" style="color: black;">'+
              'spot: '+cids[i]+'</div>';
        addInfoWindow(map.map, marker, contentString);
        markers.push(marker);

        lat_lng_object_array.push(latLng);
        if(lat_max < cord[0])
            lat_max = cord[0];
        if(lat_min > cord[0])
            lat_min = cord[0];
        if(lng_max < cord[1])
            lng_max = cord[1];
        if(lng_min > cord[1])
            lng_min = cord[1];
        i+=1;
    }
    var center_lat = (lat_max+lat_min)/2;
    var center_lng = (lng_max+lng_min)/2;

    map.setCenter({lat: center_lat, lng: center_lng});
    map.fitLatLngBounds(lat_lng_object_array);


    var markerCluster = new MarkerClusterer(map.map, markers,
            {imagePath: cluserImgPath});
    return map;
}

function addInfoWindow(map, marker, message) {

    var infoWindow = new google.maps.InfoWindow({
        content: message
    });

    google.maps.event.addListener(marker, 'click', function () {
        infoWindow.open(map, marker);
    });
}
