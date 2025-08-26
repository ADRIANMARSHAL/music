// ---------------- Supabase Config ----------------
const { createClient } = supabase;
const supabaseUrl = "https://zqmotxqejqnjhtdjxbik.supabase.co";
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpxbW90eHFlanFuamh0ZGp4YmlrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU2ODQ4ODIsImV4cCI6MjA3MTI2MDg4Mn0.2sYGb7X0uDAihr8xyDzHOJFEdAX-zeDa-LJ81VhYSJs";
const supabaseClient = createClient(supabaseUrl, supabaseKey);

// ---------------- DOM Elements ----------------
const songList = document.getElementById("song-list");
const audioPlayer = document.getElementById("audio-player");
const playBtn = document.getElementById("play-btn");
const pauseBtn = document.getElementById("pause-btn");
const coverImg = document.getElementById("cover-img");
const nowPlaying = document.getElementById("now-playing");

// ---------------- Cache ----------------
let songsCache = []; // Stores songs for fast reloading
let currentSongIndex = 0;

// ---------------- Fetch Songs ----------------
async function fetchSongs() {
  try {
    // Get list of files in "songs" bucket
    const { data, error } = await supabaseClient.storage
      .from("songs")
      .list("", { limit: 50, sortBy: { column: "created_at", order: "desc" } });

    if (error) throw error;

    // Convert to public URLs
    songsCache = await Promise.all(
      data.map(async (file) => {
        const { data: urlData } = supabaseClient.storage
          .from("songs")
          .getPublicUrl(file.name);

        // Extract metadata from filename (example: title-artist-cover.jpg)
        const parts = file.name.split("-");
        return {
          title: parts[0] || "Unknown Title",
          artist: parts[1] || "Unknown Artist",
          cover: parts[2] ? `https://YOUR-PROJECT-URL.supabase.co/storage/v1/object/public/covers/${parts[2]}` : "default-cover.jpg",
          url: urlData.publicUrl,
        };
      })
    );

    renderSongs();
  } catch (err) {
    console.error("Fetch songs error:", err.message);
  }
}

// ---------------- Render Songs ----------------
function renderSongs() {
  songList.innerHTML = "";
  songsCache.forEach((song, index) => {
    const li = document.createElement("li");
    li.className = "song-item";

    li.innerHTML = `
      <img src="${song.cover}" alt="cover" class="cover lazy-img" loading="lazy"/>
      <div>
        <h3>${song.title}</h3>
        <p>${song.artist}</p>
      </div>
    `;

    li.addEventListener("click", () => playSong(index));
    songList.appendChild(li);
  });
}

// ---------------- Play Song ----------------
function playSong(index) {
  currentSongIndex = index;
  const song = songsCache[index];

  if (!song) return;

  audioPlayer.src = song.url;
  audioPlayer.play();

  coverImg.src = song.cover;
  nowPlaying.textContent = `🎶 Now Playing: ${song.title} - ${song.artist}`;

  playBtn.style.display = "none";
  pauseBtn.style.display = "inline-block";
}

// ---------------- Controls ----------------
playBtn.addEventListener("click", () => {
  audioPlayer.play();
  playBtn.style.display = "none";
  pauseBtn.style.display = "inline-block";
});

pauseBtn.addEventListener("click", () => {
  audioPlayer.pause();
  pauseBtn.style.display = "none";
  playBtn.style.display = "inline-block";
});

// Auto next song
audioPlayer.addEventListener("ended", () => {
  currentSongIndex = (currentSongIndex + 1) % songsCache.length;
  playSong(currentSongIndex);
});

// ---------------- Speed Optimizations ----------------
// 1. Lazy load images (done via `loading="lazy"` + .lazy-img class)
// 2. Prefetch next song audio
audioPlayer.addEventListener("play", () => {
  const nextIndex = (currentSongIndex + 1) % songsCache.length;
  if (songsCache[nextIndex]) {
    const prefetch = new Audio();
    prefetch.src = songsCache[nextIndex].url;
  }
});

// ---------------- Init ----------------
fetchSongs();
