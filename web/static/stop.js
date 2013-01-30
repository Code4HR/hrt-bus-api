function Stop(data) {
	this.data = data;
	
	this.addToMap = function () {
        this.createMarker();
        this.createInfoWindow(true);
    };

    this.createMarker = function () {
        this.position = new google.maps.LatLng(this.data.location[1], this.data.location[0]);
        this.marker = new google.maps.Marker({
            position: this.position,
            map: map,
            animation: google.maps.Animation.DROP,
            title: this.data.stopName
        });
    };

    this.createInfoWindow = function (withButton) {
        this.infoWindow = new google.maps.InfoWindow({
            content: this.getInfoWindowMsg(withButton)
        });
        var context = this;
		google.maps.event.addListener(this.marker, 'click', function () { context.markerSelected(context); });
		
		if(withButton) {
			google.maps.event.addListener(this.infoWindow, 'domready', function () {
				$('#chooseStop_' + context.data.stopId).click(function(){setSelectedStop(context);})
			});
		}
    };

	this.getInfoWindowMsg = function(withButton) {
		var msg = this.data.stopName;
		msg += '<br>Stop ID: ' + this.data.stopId;
		msg += '<br>Inbound Routes: ' + (this.data.inboundRoutes.length ? this.data.inboundRoutes.join() : 'None');
		msg += '<br>Outbound Routes: ' + (this.data.outboundRoutes.length ? this.data.outboundRoutes.join() : 'None');
		if(withButton) {
			msg += '<br><button id="chooseStop_'+ this.data.stopId +'" style="width:100%; font-size:18px;">Choose Stop</button>';
		}
		return msg;
	};
	
	this.markerSelected = function (context) {
        if (selectedStop) {
            selectedStop.infoWindow.close();
        }
        selectedStop = context;
        if (selectedStop.infoWindow) selectedStop.infoWindow.open(map, context.marker);
    };

	this.destroy = function () {
        if(this.marker)
            this.marker.setMap(null);
    };
}
