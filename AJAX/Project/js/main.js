var map = null;

// Should be called if there is a problem loading the google API
function googleError() {
  window.alert("Google Maps API could not be loaded at this time");
  console.error("Google Map API Not Loaded");
}

// Callback function for flickr api request
function jsonFlickrFeed(json) {
  photos = [];
  _.forEach(json.items, function(photo) {
    photos.push({
      src: photo.media.m,
      title: photo.title
    });
  });
}

// Store a single instance of an infoWindow object
var infoWindow = null;

var flickr = {
  key: "b7642d77cc5cbc2cfa7ec8363710d961"
};

// Default locations
var locations = [
  {
    lat: 32.755488,
    lng: -97.330766,
    name: "Fort Worth",
    searchTerm: "Fort Worth, Texas"
  },
  {
    lat: 32.788562,
    lng: -97.346234,
    name: "Stockyards",
    searchTerm: "Fort Worth Stockyards"
  },
  {
    lat: 32.740179,
    lng: -97.363902,
    name: "Botanic Gardens",
    searchTerm: "Fort Worth Botanic Gardens"
  },
  { lat: 32.722969, 
    lng: -97.35669, 
    name: "Zoo", 
    searchTerm: "Fort Worth Zoo" },
  {
    lat: 32.744213,
    lng: -97.369307,
    name: "Museum of Science and History",
    searchTerm: "Fort Worth Museum of Science and History"
  }
];

var photos = [];

function LocationsViewModel() {
  var self = this;

  self.selectedTitle = ko.observable("");
  self.filter = ko.observable("");

  // Map markers
  self.markers = [];

  self.photos = ko.observableArray(photos);

  // Filters markers via user input
  self.filteredLocations = ko.computed(function() {
    if (self.filter().length > 0) {
      return ko.utils.arrayFilter(locations, function(location) {
        return (location.name.toLowerCase().indexOf(self.filter().toLowerCase()) >= 0);
      });
    } else {
      return locations;
    }
  });

  // Updates the map with available markers
  self.updateMap = function() {
    // Clear existing markers
    self.clearMarkers();

    // Load Locations
    var filteredArray = self.filteredLocations();

    // Create markers and store a reference to them in the markers array
    if (filteredArray.length > 0) {
      for (var i in filteredArray) {
        var location = filteredArray[i];
        var marker = new google.maps.Marker({
          position: { lat: location.lat, lng: location.lng },
          map: map,
          location: location
        });

        marker.addListener("click", self.loadImages);

        self.markers.push(marker);
      }
    }
  };

  // Load images from flickr for the selected marker
  self.loadImages = function() {
    // if "this" has a location property use that, otherwise "this" is the location object.
    var location = this.location || this;

    if (!location) {
      console.error("Location object not available");
    }

    // Close infoWindow if it exists
    if (infoWindow) {
      infoWindow.close();
    }

    self.photos.removeAll();

    self.selectedTitle(location.searchTerm);

    $.ajax({
      url: "https://api.flickr.com/services/feeds/photos_public.gne",
      dataType: "jsonp",
      data: {
        tags: location.searchTerm,
        api_key: flickr.key,
        format: "json"
      }
    }).always(function() {
      // After request completes load photos obtained in the
      // callback function into the observable array
      _.forEach(photos, function(photo) {
        self.photos.push(photo);
      });

      infoWindow = new google.maps.InfoWindow({
        content: location.searchTerm
      });

      // Add animation and infoWindow to the selected marker
      _.forEach(self.markers, function(marker) {
        marker.setAnimation(null);

        if (marker.location.name === location.name) {
          marker.setAnimation(google.maps.Animation.BOUNCE);
          infoWindow.open(map, marker);
        }
      });
    });
  };

  self.clearMarkers = function() {
    // Remove markers from the existing map
    _.forEach(self.markers, function(marker) {
      marker.setMap(null);
    });

    // Reset the markers array
    self.markers = [];
  };

  self.updateMap();
}

// Called when the google map API successfully loads
function googleSuccess() {
  // Map Center
  var uluru = { lat: locations[0].lat, lng: locations[0].lng };

  // Global instance of the google map
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 12,
    center: uluru
  });

  var VM = new LocationsViewModel();
  ko.applyBindings(VM);

  // subscribe to the filter object to call updateMap when filter changes
  VM.filter.subscribe(function() {
    VM.updateMap();
  });
}
