Date.prototype.addHours = function(h){
    this.setHours(this.getHours()+h);
    return this;
}

var map;
var userPosition;
var stopPosition;
var busesOnMap = [];
var stopsOnMap = [];
var visibleBus;
var selectedStop;

function createMap(position) {
    map = new google.maps.Map($('#mapcanvas')[0], {
        zoom: 11,
        mapTypeControl: false,
        navigationControlOptions: { style: google.maps.NavigationControlStyle.SMALL },
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });
	setMapSize();
	
	if(position) {
		userPosition = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
		new google.maps.Marker({
            position: userPosition,
            map: map,
            title: "I am here!"
        });
	} else {
		userPosition = new google.maps.LatLng(36.863794,-76.285608);
	}
	map.setCenter(userPosition);
}

function setMapSize() {
	$('#mapcanvas').height($(window).height() - $('#header').outerHeight() - $('#content').outerHeight())
}

function showBuses() {
    clearBusesOnMap();
    $('#msg').val('');
    
    $.getJSON("/api/buses/on_route/" + $("#routeNumber").val())
        .done(function (buses) {
            $('#msg').text(buses.length + ' buses found');

            var bounds = new google.maps.LatLngBounds();
            bounds.extend(userPosition);
			if(selectedStop) bounds.extend(selectedStop.position);
            $.each(buses, function () {
                var bus = new Bus(this);
                bus.addToMap();
                bounds.extend(bus.position);
                busesOnMap.push(bus);
            });
            map.fitBounds(bounds);
        });
}

function clearBusesOnMap() {
    $.each(busesOnMap, function() { this.destroy(); });
    busesOnMap.length = 0;
}

function locationSearchOnPosition() {
	$.getJSON('/api/stops/near/' + userPosition.lat() + '/' + userPosition.lng())
	 .done(showLocationSearchResults);
}

function locationSearchOnIntersection() {
	$.getJSON('/api/stops/near/intersection/' + $('#city').val() + '/' + $('#intersection').val())
	 .done(showLocationSearchResults);
}

function showLocationSearchResults(results) {
	clearStopSearchResults();
	
	var bounds = new google.maps.LatLngBounds();
    $.each(results, function () {
        var stop = new Stop(this);
        stop.addToMap();
        bounds.extend(stop.position);
        stopsOnMap.push(stop);
    });
    map.fitBounds(bounds);
}

function clearStopSearchResults() {
	while(stopsOnMap.length)
		stopsOnMap.pop().destroy();
}

function setSelectedStop(stop) {
	selectedStop = stop;
	
	clearStopSearchResults();
	stop.createMarker();
    stop.createInfoWindow();

	var bounds = new google.maps.LatLngBounds();
	bounds.extend(stop.position);
	bounds.extend(userPosition);
    map.fitBounds(bounds);

	showContent('routeSelect');
}

function showContent(contentId) {
	$('.option').hide();
	$('#' + contentId).show();
	setMapSize();
}

function geoError() {
	var errMsg = typeof msg == 'string' ? msg : "Geolocation failed";
    $('#msg').html(errMsg);
	createMap();
}

$(document).ready(function () {
	$(window).resize(setMapSize);
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(createMap, geoError);
    } else {
        createMap();
    }

    $.getJSON("/api/routes/active/")
        .done(function (result) {
            var options = $("#routeNumber");
            $.each(result, function() {
                options.append($("<option />").val(this.route_id).text(this.route_short_name + " - " + this.route_long_name));
            });
            options.append($("<option />").val(0).text("No Route"));
        });
});