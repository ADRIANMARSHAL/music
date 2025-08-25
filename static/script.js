let currentAudio = document.getElementById("audio-player");
let currentCover = document.getElementById("song-cover");
let currentTitle = document.getElementById("song-title");
let currentArtist = document.getElementById("song-artist");

let bigPlayer = null;

/**
 * Play a song and update both players
 */
function playSong(fileUrl, title, artist, coverUrl) {
  currentAudio.src = fileUrl;
  currentAudio.play();

  currentTitle.textContent = title;
  currentArtist.textContent = artist;
  currentCover.src = coverUrl ? coverUrl : "/static/default_cover.png";

  updateBigPlayer(fileUrl, title, artist, coverUrl);
}

/**
 * Setup big player reference (called in player.html)
 */
function initBigPlayer() {
  bigPlayer = document.getElementById("big-player");
}

/**
 * Update big player details
 */
function updateBigPlayer(fileUrl, title, artist, coverUrl) {
  if (!bigPlayer) return;

  document.getElementById("big-song-cover").src = coverUrl || "/static/default_cover.png";
  document.getElementById("big-song-title").textContent = title;
  document.getElementById("big-song-artist").textContent = artist;

  let bigAudio = document.getElementById("big-audio-player");
  if (bigAudio) {
    bigAudio.src = fileUrl;
    bigAudio.play();
  }
}

/**
 * Open the big player screen
 */
function openBigPlayer() {
  if (!bigPlayer) return;
  bigPlayer.style.display = "flex";
}

/**
 * Minimize the big player back to bottom player
 */
function minimizeBigPlayer() {
  if (!bigPlayer) return;
  bigPlayer.style.display = "none";
}
