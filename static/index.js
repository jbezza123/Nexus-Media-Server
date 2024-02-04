document.addEventListener('DOMContentLoaded', function() {
        const filmListContainer = document.getElementById('film-list-container');
        const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        // Create vertical bar with letters
        const verticalBar = document.getElementById('vertical-bar');
        letters.split('').forEach((letter) => {
          const letterDiv = document.createElement('div');
          letterDiv.classList.add('letter');
          letterDiv.textContent = letter;
          letterDiv.addEventListener('click', function() {
            // Scroll to the section with films starting with the clicked letter
            const sectionId = `section-${letter}`;
            const section = document.getElementById(sectionId);
            if (section) {
              section.scrollIntoView({
                behavior: 'smooth',
              });
            }
          });
          verticalBar.appendChild(letterDiv);
        });
        // Intersection Observer setup
        const observer = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (entry.isIntersecting) {
                // Film is in the view window, load poster if not already loaded
                const poster = entry.target.querySelector('.lazy-load-poster');
                if (poster && !poster.classList.contains('loaded')) {
                  const src = poster.dataset.src;
                  // Check if the image has been cached in local storage
                  const cachedImage = localStorage.getItem(src);
                  if (cachedImage) {
                    poster.src = cachedImage;
                  } else {
                    // If not cached, load from the server and cache it
                    poster.src = src;
                    localStorage.setItem(src, src);
                  }
                  poster.classList.add('loaded');
                }
              }
            });
          }, {
            threshold: 0.5,
          }); // Adjust threshold as needed
        // Load posters only when in the view window
        const films = document.querySelectorAll('.film-section');
        films.forEach((film) => {
          observer.observe(film);
        });
        // Search functionality
        const searchInput = document.querySelector('input[type="text"]');
        const filmsList = document.querySelectorAll('.film-section');
        searchInput.addEventListener('input', function() {
          const searchTerm = searchInput.value.toLowerCase();
          filmsList.forEach((film) => {
            const title = film.querySelector('#film-title').textContent.toLowerCase();
            if (title.includes(searchTerm)) {
              film.style.display = 'block';
            } else {
              film.style.display = 'none';
            }
          });
        });
        // Smooth scroll to the correct section
        const letterElements = document.querySelectorAll('.letter');
        letterElements.forEach((letterElement) => {
          letterElement.addEventListener('click', function() {
            const letter = letterElement.textContent;
            const sectionId = `section-${letter}`;
            const section = document.getElementById(sectionId);
            if (section) {
              section.scrollIntoView({
                behavior: 'smooth',
              });
            }
          });
        });
      });
	  
document.addEventListener('DOMContentLoaded', function() {
  const filmListContainer = document.getElementById('film-list-container');
  const filmPopups = document.querySelectorAll('.film-popup');
  const verticalBar = document.getElementById('vertical-bar');

  filmListContainer.addEventListener('click', async function(event) {
    const target = event.target;

    // Check if a film poster is clicked
    if (target.classList.contains('lazy-load-poster')) {
      // Stop the event propagation to prevent it from reaching the filmListContainer
      event.stopPropagation();

      // Find the closest film section
      const filmSection = target.closest('.film-section');

      // Find and toggle the corresponding film popup
      const filmPopup = filmSection.querySelector('.film-popup');
      filmPopup.classList.toggle('show');

      // Adjust z-index of the vertical bar based on the film popup visibility
      if (filmPopup.classList.contains('show')) {
        verticalBar.style.zIndex = -1; // Set a value that ensures the vertical bar is behind the popup
      } else {
        verticalBar.style.zIndex = ''; // Reset to default value
      }

      // Extract film title and year from the clicked film section
      const filmTitleElement = filmSection.querySelector('#film-title');
      const filmTitle = filmTitleElement.textContent.trim();
      const [filmName, filmYear] = filmTitle.match(/(.+) \((\d{4})\)/).slice(1, 3);

      // Make API request to get film ID and description
      const apiUrl = `/API/search/movie?query=${encodeURIComponent(filmName)}&year=${filmYear}`;
      try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        // Get the film ID from the first item in the results array
        const filmId = data.results.length > 0 ? data.results[0].id : null;

        // Update the film-id paragraph in the film popup
        const filmIdElement = filmPopup.querySelector('#film-id');
        filmIdElement.textContent = filmId;

        // Update the film-description paragraph in the film popup with the movie overview
        const filmDescriptionElement = filmPopup.querySelector('#film-description');
        filmDescriptionElement.textContent = data.results.length > 0 ? data.results[0].overview : '';

        // Fetch cast information using film ID
        const castApiUrl = `/API/movie/${filmId}/credits`;
        const castResponse = await fetch(castApiUrl);
        const castData = await castResponse.json();

        // Update the cast list in the film popup
        const castListElement = filmPopup.querySelector('.people.scroller');
        castListElement.innerHTML = ''; // Clear previous cast list

        castData.cast.forEach((cast) => {
          const liElement = document.createElement('li');
          liElement.classList.add('card');

          const profilePath = cast.profile_path
            ? `https://media.themoviedb.org/t/p/w138_and_h175_face/${cast.profile_path}`
            : 'path/to/default/profile/image.jpg';

          liElement.innerHTML = `
            <div class="glyphicons_v2 picture grey profile no_image_holder two">
              <img loading="lazy" class="profile" src="${profilePath}">
            </div>
            <p id="card-name">${cast.name}</p>
            <p class="character">${cast.character}</p>
          `;

          castListElement.appendChild(liElement);
        });
      } catch (error) {
        console.error('Error fetching film ID, description, and cast:', error);
      }
    }
  });
});


	  
	  //load video into tags
document.addEventListener("DOMContentLoaded", function () {
    // Get all play buttons
    var playButtons = document.querySelectorAll(".play-btn");

    // Iterate through each play button
    playButtons.forEach(function (playButton) {
        // Add click event listener to each play button
        playButton.addEventListener("click", function () {
            // Find the corresponding film-popup element
            var filmPopup = playButton.closest(".film-popup");

            // Find the video element inside the film-popup
            var videoElement = filmPopup.querySelector("video");

            // Find the URL for the video
            var videoUrlElement = filmPopup.querySelector("#url-for-video");
            var videoUrl = videoUrlElement.textContent;

            // Find the URL for the subtitle
            var subtitleUrlElement = filmPopup.querySelector("#url-for-subtitle");
            var subtitleUrl = subtitleUrlElement.textContent;

            // Determine the file extension for video
            var videoFileExtension = videoUrl.split('.').pop().toLowerCase();

            // Set the video source dynamically
            videoElement.src = videoUrl;
            videoElement.type = "video/" + videoFileExtension;

            // Find the track element for captions
            var trackElement = filmPopup.querySelector("track");

            // Set the subtitle source dynamically
            trackElement.src = subtitleUrl;

            // Display the video and subtitle elements
            videoElement.style.display = "block";
            trackElement.style.display = "block";

            // Hide the play button
            playButton.style.display = "none";

            
        });
    });
});



  
  //close button
  document.addEventListener("DOMContentLoaded", function () {
    // Get all close buttons
    var closeButtons = document.querySelectorAll(".close-btn");
	const verticalBar = document.getElementById('vertical-bar');

    // Iterate through each close button
    closeButtons.forEach(function (closeButton) {
      // Add click event listener to each close button
      closeButton.addEventListener("click", function () {
        // Find the corresponding film-popup element
        var filmPopup = closeButton.closest(".film-popup");

        // Find the video element inside the film-popup
        var videoElement = filmPopup.querySelector("video");

        // Check if the video is currently visible
        if (videoElement.style.display !== "none") {
          // Unload the video
          videoElement.src = "";

          // Hide the video element
          videoElement.style.display = "none";

          // Show the play button (assuming it has a class 'play-btn')
          var playButton = filmPopup.querySelector(".play-btn");
          if (playButton) {
            playButton.style.display = "block";
          }
        } else {
          // Close the popup
          filmPopup.classList.toggle("show");
          verticalBar.style.zIndex = ""; // Reset to default value
        }
      });
    });
  });
  
  function toggleActive(castParagraph) {
        var castElement = castParagraph.closest('#cast');
        castElement.classList.toggle("active");
    }