$(function(){
	// Global Map object
	var Map = new google.maps.Map($('#mapcanvas')[0], {
        zoom: 11,
        mapTypeControl: false,
        navigationControlOptions: { style: google.maps.NavigationControlStyle.SMALL },
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });

	var UserLocation = null;
	
	var MapView = Backbone.View.extend({
		el: $("#mapcanvas"),
		
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
			"click #findStop": "findStop"
		},
		
		render: function() {
			this.$el.html(this.template());
			return this;
		},
		
		findStop: function() {
			App.Router.navigate('findStop/', {trigger: true});
		}
	});
	
	var StopSearchView = Backbone.View.extend({
		template: _.template($('#begin-stop-search-template').html()),
		
		events: {
			"click #stopSearch-location": "stopSearchOnLocation",
			"click #stopSearch-intersection": "stopSearchOnIntersection"
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
		},
		
		render: function() {
			this.$el.html(this.template());
			return this;
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
			"findStop/": "findStop",
			"findStop/intersection/": "findStopByIntersection",
			"findStop/:lat/:lng/": "runStopSearchOnLatLng"
		 },
		
		home: function() {
			App.ContentView.setSubView(new HomeView);
		},
		
		findStop: function() {
			App.ContentView.setSubView(new StopSearchView);
		},
		
		findStopByIntersection: function() {
			App.ContentView.setSubView(new StopSearchIntersectionView);
		},
		
		runStopSearchOnLatLng: function(lat, lng) {
			alert('Search Lat: ' + lat + ' Lng: ' + lng);
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