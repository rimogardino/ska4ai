
// function playPause(videoPlayer) { 
//     if (videoPlayer.paused) 
//       videoPlayer.play(); 
//     else 
//       videoPlayer.pause(); 
//   };

//   function newChallenge(button) { 
//     const base_link = "{% url 'pk_challenge:new_challenge_form' %}";
//     var event = button.getAttribute("data-event");
//     window.location.href = base_link + event; 
//   };


// // Function to fetch content using HTMX manually
// function fetchPopupContent(challengeId) {
//     htmx.ajax('GET', `{% url 'pk_challenge:challenge_simple_info' 12345 %}`.replace(/12345/, challengeId.toString()), {
//         target: `#popup-details-${challengeId}`,
//         swap: 'innerHTML'
//     });
// }


// $ (document).ready(function(){


// $ (".event-item").on("click", function() {
//     var selected_event = $ (this).attr("data-event-id");
//     // add data-event to new challenge button
//     const new_challenge_button = document.getElementById('new-challenge');
//     new_challenge_button.setAttribute("data-event", selected_event);
//     // list view logic
//     $ (".challenges-container").hide();
//     $ ('#ev-chs-' + selected_event).show();
//     $ ("#event-description-" + selected_event).show();
//     $ ('#new-challenge-link').attr('href', `{% url 'challenges:create_challenge' %}` + selected_event)
//     //map view markers
//     $ (".mapboxgl-marker").hide();
//     $ (".marker-event-" + selected_event).show();
// });


// $ ("#event_selection").on("change", function() {
//     $ (".event-description").hide();
//     var selected_event = $ (this).val();
//     $ (".challenges-container").hide();
//     $ ('#ev-chs-' + selected_event).show();
//     $ ("#event-description-" + selected_event).show();
//     $ ('#new-challenge-link').attr('href', `{% url 'pk_challenge:new_challenge_form' %}` + selected_event)
// }).change();












// mapboxgl.accessToken = '{{ mapbox_api_key }}';
// const map = new mapboxgl.Map({
//     container: 'map', // container ID
//     //style: 'mapbox://styles/mapbox/dark-v11',
//     center: [23.321869, 42.697085], // starting position [lng, lat]. Note that lat must be set between -90 and 90
//     //an array of numbers in [west, south, east, north] order.
//     maxBounds: [23.2, 42.6, 23.45, 42.75],
//     zoom: 13, // starting zoom
//     antialias: false, // Disable antialiasing for performance
// });

// map.on('load', () => {
//     //Remove exess landmark and icons
//     map.on('style.load', () => {
//         map.setConfigProperty('basemap', 'showPointOfInterestLabels', false);
//     });

//     // Show user location on map button
//     map.addControl(new mapboxgl.GeolocateControl({
//         positionOptions: {
//             enableHighAccuracy: true
//         },
//         trackUserLocation: true,
//         showUserHeading: true
//     }));

//     // Show ruler with scale on bottom left
//     const scale = new mapboxgl.ScaleControl({
//         maxWidth: 100,
//         unit: 'metric'
//     });
//     map.addControl(scale);

//     // var json_data = document.getElementById('main-div').getAttribute('data-json');
//     // const geojson = JSON.parse(json_data);
//     // console.log(geojson);



//     for (const feature of geojson) {
//         const popupContent = `
//             <div class="popup-content">
//                 <div id="popup-details-${feature.properties.challenge_id}">
//                     Loading...
//                 </div>
//             </div>
//         `;



//         const ch_popup = new mapboxgl.Popup({ 
//             offset: 25,
//             closeOnClick: true
//         }).setHTML(popupContent);
    
//         // make a marker for each feature and add to the map
//         console.log("creating marker with coords: ", feature.geometry.coordinates)
//         const marker = new mapboxgl.Marker({
//             className: `marker-event-${feature.properties.event}`,
//             //color: "#FFFFFF",
//             draggable: false,
//         }).setLngLat(feature.geometry.coordinates)
//         .setPopup(
//             ch_popup
//         ) // sets a popup on this marker
//         .addTo(map);

//         marker.getElement().addEventListener('click', () => {
//             // Small delay to ensure popup is rendered
//             setTimeout(() => {
//                 fetchPopupContent(feature.properties.challenge_id);
//             }, 50);
//         });


//         //marker.on('dragend', onDragEnd);
//     }


//     //const staticContainer = document.getElementById('static');
//     //staticContainer.style.visibility = 'hidden';
//     const mapContainerEl = document.getElementById('map');
//     mapContainerEl.style.visibility = 'visible';

//     $ (".event-item").eq(0).click();
// });

// map.resize();



// }); 