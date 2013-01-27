function Bus(checkin) {
    this.checkin = checkin;

    this.addToMap = function () {
        this.createMarker();
        this.createInfoWindow();
        this.getCheckinHistory(this.createPath);
    };

    this.createMarker = function () {
        this.position = new google.maps.LatLng(this.checkin.location[1], this.checkin.location[0]);
        this.marker = new google.maps.Marker({
            position: this.position,
            map: map,
            animation: google.maps.Animation.DROP,
            title: 'Bus ' + this.checkin.busId,
            icon: '/static/bus.png'
        });
    };

    this.createInfoWindow = function () {
        this.infoWindow = new google.maps.InfoWindow({
            content: this.getInfoWindowMsg()
        });
        var context = this;
        google.maps.event.addListener(this.marker, 'click', function () { context.markerSelected(context); });
        google.maps.event.addListener(this.infoWindow, 'closeclick', this.markerUnselected);
    };

    this.createPath = function (pastCheckins) {
        var stopMarkers = [];
        var pathCoordinates = [];
        $.each(pastCheckins, function () {
            var position = new google.maps.LatLng(this.location[1], this.location[0]);
            pathCoordinates.push(position);

            if (this.stopId)
                stopMarkers.push(new google.maps.Marker({
                    position: position,
                    icon: { path: google.maps.SymbolPath.CIRCLE, scale: 2 }
                }));
        });

        this.stopMarkers = stopMarkers;
        this.path = new google.maps.Polyline({
            path: pathCoordinates,
            strokeColor: "#FF0000",
            strokeOpacity: 1.0,
            strokeWeight: 2
        });
    };

    this.markerSelected = function (context) {
        map.setCenter(context.position);

        if (visibleBus) {
            visibleBus.infoWindow.close();
            visibleBus.path.setMap(null);
            $.each(visibleBus.stopMarkers, function () { this.setMap(null); });
        }

        visibleBus = context;
        if (visibleBus.infoWindow) visibleBus.infoWindow.open(map, context.marker);
        if (visibleBus.path) visibleBus.path.setMap(map);
        if (visibleBus.stopMarkers) $.each(visibleBus.stopMarkers, function () { this.setMap(map); });
    };

    this.markerUnselected = function() {

    };

    this.getCheckinHistory = function(callback) {
        $.getJSON("/api/buses/history/" + this.checkin.busId)
            .done($.proxy(callback, this));
    };

    this.getInfoWindowMsg = function() {
        var msg = '';
        msg += 'Bus #' + this.checkin.busId + ' traveling ';
        msg += this.checkin.direction == 0 ? 'outbound' : 'inbound';
        
		if (this.checkin.adherence != null) msg += '<br>is ';
		if (this.checkin.adherence == null) msg += '<br>has no adherence'
        else if (this.checkin.adherence == 0) msg += 'on time';
        else if (this.checkin.adherence == 1) msg += '1 minute early';
        else if (this.checkin.adherence > 0) msg += this.checkin.adherence + ' minutes early';
        else if (this.checkin.adherence == -1) msg += '1 minute late';
        else msg += (this.checkin.adherence * -1) + ' minutes late';

        var date = new Date(this.checkin.time).addHours(-5);
        var timePassed = new Date(new Date().getTime() - date).getMinutes();

        msg += '<br>as of ';
        if (timePassed == 0) msg += 'just now.';
        else if (timePassed == 1) msg += '1 minute ago.';
        else msg += timePassed + ' minutes ago.';

        return msg;
    };

    this.destroy = function () {
        if(this.marker)
            this.marker.setMap(null);
        
        if(this.path)
            this.path.setMap(null);

        if (this.stopMarkers)
            $.each(this.stopMarkers, function () { this.setMap(null); });
    };
};