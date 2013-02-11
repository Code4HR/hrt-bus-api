$(function(){
	
	// Fix JavaScript Modulo of negative numbers
	// http://javascript.about.com/od/problemsolving/a/modulobug.htm
	Number.prototype.mod = function(n) {
		return ((this%n)+n)%n;
	};
	
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
			navigator.geolocation && navigator.geolocation.getCurrentPosition(this.setUserLocation);
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
		
		initialize: function() {
			this.collection.on('reset', this.render, this);
			this.collection.fetch();
		},
		
		render: function() {
			this.$el.html(this.template({routes: this.collection.toJSON()}));
			return this;
		},
		
		routeSelected: function() {
			var route = this.$('#route option:selected').val();
		}
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
			"routes/": "routes",
			"findStop/": "findStop",
			"findStop/intersection/": "findStopByIntersection",
			"findStop/intersection/:intersection/:city/": "runStopSearchOnIntersection",
			"findStop/:lat/:lng/": "runStopSearchOnLatLng",
			"nextBus/:stop/:route/:direction": "nextBus"
		 },
		
		home: function() {
			App.ContentView.setSubView(new HomeView);
		},
		
		routes: function() {
			var routes = new Backbone.Collection;
			routes.url = '/api/routes/active/';
			App.ContentView.setSubView(new RouteView({collection: routes}));
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
			
		}
	});
	
	var App = {
		MapView: new MapView,
		ContentView: new ContentView,
		Router: new Router
	};
	
	App.ContentView.on('contentChanged', App.MapView.render, App.MapView);
	Backbone.history.start({pushState: true, root: "/busfinder-backbone/"});
});