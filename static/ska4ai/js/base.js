// Challenge_simple_info

console.log('base js API Key:', apiKey);

function playPause(video) {
    var this_video_paused = video.paused;
    var all_videos = document.querySelectorAll('.video-player');
    for (var i = 0; i < all_videos.length; i++) {
        all_videos[i].pause();
        all_videos[i].parentElement.querySelector('.play-overlay').style.display = 'flex'
    }
    if (this_video_paused) {
      video.play();
      video.parentElement.querySelector('.play-overlay').style.display = 'none';
    }
  }

  function scrollMedia(direction) {
    const container = document.querySelector('.media-container');
    const scrollAmount = 300; // Adjust this value to control scroll distance
    
    if (direction === 'left') {
      container.scrollBy({
        left: -scrollAmount,
        behavior: 'smooth'
      });
    } else {
      container.scrollBy({
        left: scrollAmount,
        behavior: 'smooth'
      });
    }
  }











  // Optional: Hide scroll buttons if no overflow
//   function updateScrollButtons() {
//     const container = document.querySelector('.media-container');
//     const buttons = document.querySelectorAll('.scroll-button');
    
//     if (container.scrollWidth <= container.clientWidth) {
//       buttons.forEach(button => button.style.display = 'none');
//     } else {
//       buttons.forEach(button => button.style.display = 'flex');
//     }
//   }

//   // Call on load and resize
//   window.addEventListener('load', updateScrollButtons);
//   window.addEventListener('resize', updateScrollButtons);