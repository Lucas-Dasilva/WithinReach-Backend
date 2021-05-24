function geoFindMe() {

  const status = document.querySelector('#status');
  //const mapLink = document.querySelector('#map-link');

  // mapLink.href = '';
  // mapLink.textContent = '';

  function success(position) {
    const latitude  = position.coords.latitude;
    const longitude = position.coords.longitude;
    var obj = new Object();
    obj.name = "location";
    obj.latitude  = latitude;
    obj.longitude = longitude;
    var locationString= JSON.stringify(obj);
    status.textContent = '';
    // mapLink.textContent = `Latitude: ${latitude} °, Longitude: ${longitude} °`;
    //console.log(typeof(locationString));
    
    callAjax(locationString);
  }
  function error(err) {
    status.textContent = 'Unable to retrieve your location'();
    console.error(err)
  }

  if(!navigator.geolocation) {
    status.textContent = 'Geolocation is not supported by your browser';
  } else {
    status.textContent = 'Locating…';
    navigator.geolocation.getCurrentPosition(success, error);
  }

  function callAjax(location){
    console.log("What it looks like:", location);
    jQuery.ajax({ 
      url: '/getLocation', 
      type: "POST", 
      contentType: "application/json",
      data: location,
      dataType: "text",
      timeout: 5000,
      crossDomain:true,
      success: function() { 
        alert('location Saved');
      },
      error:function(){
        alert('error saving location');
      }
    });
  }
}
function geoFindMeUpdate() {

  const status = document.querySelector('#status');
  //const mapLink = document.querySelector('#map-link');

  // mapLink.href = '';
  // mapLink.textContent = '';

  function success(position) {
    const latitude  = position.coords.latitude;
    const longitude = position.coords.longitude;
    var obj = new Object();
    obj.name = "location";
    obj.latitude  = latitude;
    obj.longitude = longitude;
    var locationString= JSON.stringify(obj);
    status.textContent = '';
    // mapLink.textContent = `Latitude: ${latitude} °, Longitude: ${longitude} °`;
    //console.log(typeof(locationString));
    
    callAjaxUpdate(locationString);
  }
  function error(err) {
    status.textContent = 'Unable to retrieve your location'();
    console.error(err)
  }

  if(!navigator.geolocation) {
    status.textContent = 'Geolocation is not supported by your browser';
  } else {
    status.textContent = 'Locating…';
    navigator.geolocation.getCurrentPosition(success, error);
  }

  function callAjaxUpdate(location){
    console.log("What it looks like:", location);
    jQuery.ajax({ 
      url: '/getLocation', 
      type: "POST", 
      contentType: "application/json",
      data: location,
      dataType: "text",
      timeout: 5000,
      crossDomain:true,
      success: function() { 
        console.log('New Location Saved to Session!');
      },
      error:function(){
        alert('error saving location');
      }
    });
  }
}
var element = document.getElementById('find-me');
var element2 = document.getElementById('updateLocation');

if (element !== null) {
  document.getElementById('find-me').addEventListener('click', geoFindMe);
}
if (element2 !== null) {
  document.getElementById('updateLocation').addEventListener('click', geoFindMeUpdate);
}

