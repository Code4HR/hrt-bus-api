$(function(){
	
	// Fix JavaScript Modulo of negative numbers
	// http://javascript.about.com/od/problemsolving/a/modulobug.htm
	Number.prototype.mod = function(n) {
		return ((this%n)+n)%n;
	};
	
	
	// Create addHours function for Date object so we can
	// easily get from GMT to EST (probably need to find a library for this)
	Date.prototype.addHours = function(h){
	    this.setHours(this.getHours()+h);
	    return this;
	}
	Date.prototype.addMinutes = function(h){
	    this.setMinutes(this.getMinutes()+h);
	    return this;
	}
	
	// Global Map object
	var Map = new google.maps.Map($('#mapcanvas')[0], {
        zoom: 11,
        mapTypeControl: false,
        navigationControlOptions: { style: google.maps.NavigationControlStyle.SMALL },
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });

	var UserLocation = null;
	
	var MapView = Backbone.View.extend({
		el: $('#mapcanvas'),
		
		initialize: function() {
			_.bindAll(this);
			$(window).resize(this.render);
			
			this.downtownNorfolk = new google.maps.LatLng(36.863794,-76.285608);
			this.center = this.downtownNorfolk;
			navigator.geolocation && navigator.geolocation.getCurrentPosition(this.setUserLocation, this.showGeolocationError);
			this.render();
		},
		
		render: function() {
			this.$el.height($(window).height() - $('#header').outerHeight() - $('#content').outerHeight());
			Map.setCenter(this.center);
			return this;
		},
		
		setUserLocation: function(position) {
			UserLocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
			this.userPositionMarker = new google.maps.Marker({
	            position: UserLocation,
	            map: Map
	        });
			this.center = UserLocation;
			this.render();
		},
		
		showGeolocationError: function(error) {
			alert('Geolocation Error: ' + error);
		}
	});
	
	var HomeView = Backbone.View.extend({
		template: _.template($('#home-template').html()),
		
		events: {
			'click #findStop': 'findStop',
			'click #goToRoutes': 'goToRoutes'
		},
		
		render: function() {
			this.$el.html(this.template());
			return this;
		},
		
		findStop: function() {
			App.Router.navigate('findStop/', {trigger: true});
		},
		
		goToRoutes: function() {
			App.Router.navigate('routes/', {trigger: true});
		}
	});
	
	var StopSearchView = Backbone.View.extend({
		template: _.template($('#begin-stop-search-template').html()),
		
		events: {
			'click #stopSearch-location': 'stopSearchOnLocation',
			'click #stopSearch-intersection': 'stopSearchOnIntersection'
		},
		
		render: function() {
			this.$el.html(this.template());
			return this;
		},
		
		stopSearchOnLocation: function() {
			if(UserLocation) {
				App.Router.navigate('findStop/' + UserLocation.lat() + '/' + UserLocation.lng() + '/', {trigger: true});
			} else {
				alert("Sorry, but I don't know where you are.");
			}
		},
		
		stopSearchOnIntersection: function() {
			App.Router.navigate('findStop/intersection/', {trigger: true});
		}
	});
	
	var StopSearchIntersectionView = Backbone.View.extend({
		template: _.template($('#stop-search-template').html()),
		
		events: {
			'click #search': 'search'
		},
		
		render: function() {
			this.$el.html(this.template());
			return this;
		},
		
		search: function() {
			var intersection = this.$('#intersection').val();
			var city = this.$('#city').val();
			if(intersection == "" || city == "") {
				alert("Please enter an intersection and a city");
			} else {
				App.Router.navigate('findStop/intersection/' + intersection + '/' + city + '/', {trigger: true});
			}
		}
	});
	
	var StopSearchResultsView = Backbone.View.extend({
		template: _.template($('#stop-search-results-template').html()),
		
		events: {
			'click #prev-stop': 'prevStop',
			'click #next-stop': 'nextStop',
			'change #route': 'routeSelected'
		},
		
		initialize: function() {
			this.collection.on('reset', this.stopsLoaded, this);
			this.collection.fetch();
		},
		
		render: function() {
			if(this.collection && this.collection.length > 0) {
				var viewModel = this.collection.at(this.currentCollection).toJSON();
				viewModel.curStop = this.currentCollection + 1;
				viewModel.numStops = this.collection.length;
				this.$el.html(this.template(viewModel));
				this.renderStopMarker(viewModel);
			} else {
				this.$el.html(this.template({
					stopName:'Loading...', 
					stopId: 0,
					inboundRoutes:[], 
					outboundRoutes:[],
					curStop:0,
					numStops:0
				}));
			}
			this.$el.trigger('create');
			return this;
		},
		
		renderStopMarker: function(stop) {
			if(this.marker) {
				this.marker.setMap(null);
			}
			
			if(stop) {
	        	this.marker = new google.maps.Marker({
		            position: new google.maps.LatLng(stop.location[1], stop.location[0]),
		            map: Map,
		            title: stop.stopName,
					icon: '/static/img/busstop.png'
		        });
				Map.panTo(this.marker.getPosition());
				Map.setZoom(18);
			}
		},
		
		stopsLoaded: function() {
			this.currentCollection = 0;
			this.render();
		},
		
		prevStop: function() {
			this.currentCollection = (this.currentCollection - 1).mod(this.collection.length);
			this.render();
		},
		
		nextStop: function() {
			this.currentCollection = (this.currentCollection + 1).mod(this.collection.length);
			this.render();
		},
		
		routeSelected: function() {
			var stopId = this.collection.at(this.currentCollection).get('stopId');
			var route = this.$('#route option:selected').val();
			var direction = this.$('#route option:selected').parent()[0].id;
			App.Router.navigate('nextBus/' + stopId + '/' + route + '/' + direction + '/', {trigger: true});
		}
	});
	
	var RouteView = Backbone.View.extend({
		template: _.template($('#route-view-template').html()),
		
		events: {
			'change #route': 'routeSelected'
		},
		
		busViews: [],
		
		initialize: function() {
			this.buses = new Backbone.Collection;
			this.buses.on('reset', this.addBuses, this);
			
			if(this.options.route) {
				this.selectedRoute = this.options.route;
				this.getBusesForSelectedRoute();
			}
			
			this.collection.on('reset', this.render, this);
			this.collection.fetch();
		},
		
		render: function() {
			this.$el.html(this.template({ routes: this.collection.toJSON(), buses: this.buses.length }));
			this.selectedRoute && this.$('#route').val(this.selectedRoute);
			this.$el.trigger('create');
			return this;
		},
		
		addBus: function(bus) {
			var busView = new BusView({model: bus});
			busView.on('markerSelected', this.showBusDetails, this);
			this.bounds.extend(busView.position);
			this.busViews.push(busView);
		},
		
		addBuses: function() {
			while(this.busViews.length) {
				this.busViews.pop().destroy();
			}
			
			this.bounds = new google.maps.LatLngBounds();
			this.buses.each(this.addBus, this);
			
			UserLocation && this.bounds.extend(UserLocation);
			Map.fitBounds(this.bounds);
			
			this.render();
		},
		
		getBusesForSelectedRoute: function() {
			this.buses.url = '/api/buses/on_route/' + this.selectedRoute;
			this.buses.fetch();
		},
		
		routeSelected: function() {
			this.selectedRoute = this.$('#route option:selected').val();
			this.getBusesForSelectedRoute();
			App.Router.navigate('routes/' + this.selectedRoute + '/');
		},
		
		showBusDetails: function(busView) {
			this.selectedBus && this.selectedBus.hideDetails();
			this.selectedBus = busView;
			
			Map.panTo(this.selectedBus.position);
			this.selectedBus.showDetails();
		}
	});
	
	var BusView = Backbone.View.extend({
		initialize: function() {
			_.bindAll(this);
			this.collection = new Backbone.Collection;
			this.collection.url = '/api/buses/history/' + this.model.get('busId');
			this.collection.on('reset', this.createPath, this);
			this.collection.fetch();
			this.createMarker();
		},
		
		createMarker: function () {
			this.position = new google.maps.LatLng(this.model.get('location')[1], this.model.get('location')[0]);

			this.marker = new google.maps.Marker({
				position: this.position,
				map: Map,
				animation: google.maps.Animation.DROP,
				title: 'Bus ' + this.model.busId,
				icon: '/static/img/bus.png'
			});

			this.infoWindow = new google.maps.InfoWindow({ 
				content: this.getInfoWindowMsg() 
			});
			google.maps.event.addListener(this.marker, 'click', this.markerSelected);
		},
		
		getInfoWindowMsg: function() {
			var msg = '';
			msg += 'Bus #' + this.model.get('busId') + ' traveling ';
			msg += this.model.get('direction') == 0 ? 'outbound' : 'inbound';
			
			var adherence = this.model.get('adherence');
			if (adherence != null) msg += '<br>is ';
			if (adherence == null) msg += '<br>has no adherence'
			else if (adherence == 0) msg += 'on time';
			else if (adherence == 1) msg += '1 minute early';
			else if (adherence > 0) msg += adherence + ' minutes early';
			else if (adherence == -1) msg += '1 minute late';
			else msg += (adherence * -1) + ' minutes late';

			var date = new Date(this.model.get('time')).addHours(-5);
			var timePassed = new Date(new Date().getTime() - date).getMinutes();

			msg += '<br>as of ';
			if (timePassed == 0) msg += 'just now.';
			else if (timePassed == 1) msg += '1 minute ago.';
			else msg += timePassed + ' minutes ago.';

			return msg;
	    },

		createPath: function () {
			var stopMarkers = [];
			var pathCoordinates = [];
			this.collection.each(function (checkin) {
				var position = new google.maps.LatLng(checkin.get('location')[1], checkin.get('location')[0]);
				pathCoordinates.push(position);

				if (checkin.get('stopId')) {
					stopMarkers.push(new google.maps.Marker({
						position: position,
						icon: { path: google.maps.SymbolPath.CIRCLE, scale: 2 }
					}));
				}
			});

			this.stopMarkers = stopMarkers;
			this.path = new google.maps.Polyline({
				path: pathCoordinates,
				strokeColor: "#FF0000",
				strokeOpacity: 1.0,
				strokeWeight: 2
			});
		},
		
		markerSelected: function() {
			this.trigger('markerSelected', this);
		},
		
		showDetails: function() {
			this.infoWindow.open(Map, this.marker);
			this.path.setMap(Map);
			$.each(this.stopMarkers, function () { this.setMap(Map); });
		},
		
		hideDetails: function() {
			this.infoWindow.close();
			this.path.setMap(null);
			$.each(this.stopMarkers, function () { this.setMap(null); });
		},
	
		destroy: function () {
			this.hideDetails();
			this.marker && this.marker.setMap(null);
			this.remove();
	    }
	});
	
	var NextBusView = Backbone.View.extend({
		template: _.template($('#stop-times-template').html()),
		
		events: {
			'click #prev': 'prevTime',
			'click #next': 'nextTime'
		},
		
		initialize: function() {
			this.collection.on('reset', this.stopTimesLoaded, this);
			this.collection.fetch();
		},
		
		render: function() {
			if(this.collection && this.collection.length > 0) {
				var model = this.collection.at(this.currentCollection);
				var date = new Date(model.get('arrival_time'));
				var adherence = model.get('adherence');
				if(adherence) {
					date = date.addMinutes(adherence);
				}
				
				var now = new Date();
				var stopTimeMinutesFromNow = (date.getTime() - now.getTime()) / 1000 / 60 | 0;
				
				var viewModel = model.toJSON();
				
				if(stopTimeMinutesFromNow < 0) {
					viewModel.stopTimeMsg = 'left ' + (stopTimeMinutesFromNow * -1) + ' minutes ago';	
				} else {
					viewModel.stopTimeMsg = 'arrives in ' + stopTimeMinutesFromNow + ' minutes';
				}
				
				viewModel.curItem = this.currentCollection + 1;
				viewModel.numItems = this.collection.length;
				if(!viewModel.busId) viewModel.busId = null;
				
				this.$el.html(this.template(viewModel));
			} else {
				this.$el.html('Loading...');
			}
			this.$el.trigger('create');
			return this;
		},
		
		stopTimesLoaded: function() {
			this.currentCollection = 0;
			this.render();
		},
		
		prevTime: function() {
			this.currentCollection = (this.currentCollection - 1).mod(this.collection.length);
			this.render();
		},
		
		nextTime: function() {
			this.currentCollection = (this.currentCollection + 1).mod(this.collection.length);
			this.render();
		},
	});
	
	var ContentView = Backbone.View.extend({
		el: $("#content"),
		
		setSubView: function(subView) {
			this.subView && this.subView.remove();
			this.subView = subView;
			this.$el.html(this.subView.render().el);
			this.$el.trigger('create');
			this.trigger('contentChanged');
		}
	});
	
	var Router = Backbone.Router.extend({
		 routes: {
			"": "home",
			"routes/(:route/)": "busRoutes",
			"findStop/": "findStop",
			"findStop/intersection/": "findStopByIntersection",
			"findStop/intersection/:intersection/:city/": "runStopSearchOnIntersection",
			"findStop/:lat/:lng/": "runStopSearchOnLatLng",
			"nextBus/:stop/:route/:direction/": "nextBus"
		 },
		
		home: function() {
			App.ContentView.setSubView(new HomeView);
		},
		
		busRoutes: function(route) {
			var routes = new Backbone.Collection;
			routes.url = '/api/routes/active/';
			App.ContentView.setSubView(new RouteView({collection: routes, route: route}));
		},
		
		findStop: function() {
			App.ContentView.setSubView(new StopSearchView);
		},
		
		findStopByIntersection: function() {
			App.ContentView.setSubView(new StopSearchIntersectionView);
		},
		
		runStopSearchOnIntersection: function(intersection, city) {
			var stops = new Backbone.Collection;
			stops.url = '/api/stops/near/intersection/' + city + '/' + intersection + '/';
			App.ContentView.setSubView(new StopSearchResultsView({collection: stops}));
		},
		
		runStopSearchOnLatLng: function(lat, lng) {
			var stops = new Backbone.Collection;
			stops.url = '/api/stops/near/' + lat + '/' + lng + '/';
			App.ContentView.setSubView(new StopSearchResultsView({collection: stops}));
		},
		
		nextBus: function(stop, route, direction) {
			var stopTimes = new Backbone.Collection;
			stopTimes.url = '/api/stop_times/' + route + '/' + stop + '/';
			App.ContentView.setSubView(new NextBusView({ collection: stopTimes, stop: stop, route: route }));
		}
	});
	
	var App = {
		MapView: new MapView,
		ContentView: new ContentView,
		Router: new Router
	};
	
	App.ContentView.on('contentChanged', App.MapView.render, App.MapView);
	Backbone.history.start({ pushState: true, root: '/busfinder-backbone/' });
});