$(function(){
	// Global Map object
	var Map = new google.maps.Map($('#mapcanvas')[0], {
        zoom: 11,
        mapTypeControl: false,
        navigationControlOptions: { style: google.maps.NavigationControlStyle.SMALL },
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });
	
	var MapView = Backbone.View.extend({
		el: $("#mapcanvas"),
		
		initialize: function() {
			_.bindAll(this);
			$(window).resize(this.render);
			
			this.userPosition = new google.maps.LatLng(36.863794,-76.285608);
			this.center = this.userPosition;
			this.render();
		},
		
		render: function() {
			this.$el.height($(window).height() - $('#header').outerHeight() - $('#content').outerHeight());
			Map.setCenter(this.center);
			return this;
		}
	});
	
	var ContentView = Backbone.View.extend({
		el: $("#content"),
		
		events: {
			"click #findStop": "findStop"
		},
		
		findStop: function() {
			App.Router.navigate('findStop');
			this.showSection('#beginStopSearch');
		},
		
		showSection: function(section) {
			$('.section').hide();
			$(section).show();
		}
	});
	
	var Router = Backbone.Router.extend({
		 routes: {
			"": "home",
			"findStop": "findStop"
		 },
		
		home: function() {
			App.ContentView.showSection('#home');
		},
		
		findStop: function() {
			App.ContentView.showSection('#beginStopSearch');
		}
	});
	
	var App = {
		MapView: new MapView,
		ContentView: new ContentView,
		Router: new Router
	};
	
	Backbone.history.start({pushState: true, root: "/busfinder-backbone/"});
});