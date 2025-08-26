// script.js

// Initialize Supabase client
const { createClient } = window.supabase;
const supabaseUrl = "https://zqmotxqejqnjhtdjxbik.supabase.co"; // replace
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpxbW90eHFlanFuamh0ZGp4YmlrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU2ODQ4ODIsImV4cCI6MjA3MTI2MDg4Mn0.2sYGb7X0uDAihr8xyDzHOJFEdAX-zeDa-LJ81VhYSJs"; // replace
const supabase = createClient(supabaseUrl, supabaseKey);

async function fetchSongs() {
  try {
    // Fetch songs from the "songs" table
    const { data, error } = await supabase
      .from("songs")
      .select("id, title, artist, cover_url, audio_url")
      .order("created_at", { ascending: false });

    if (error) throw error;

    const songList = document.getElementById("song-list");
    songList.innerHTML = "";

    if (!data || data.length === 0) {
      songList.innerHTML = "<p>No songs uploaded yet 🎶</p>";
      return;
    }

    data.forEach((song) => {
      const card = document.createElement("div");
      card.classList.add("song-card");

      card.innerHTML = `
        <img src="${song.cover_url}" alt="${song.title}" class="cover">
        <div class="song-info">
          <h3>${song.title}</h3>
          <p>${song.artist}</p>
          <audio controls src="${song.audio_url}"></audio>
        </div>
      `;

      songList.appendChild(card);
    });
  } catch (err) {
    console.error("Error fetching songs:", err.message);
  }
}

// Run on page load
document.addEventListener("DOMContentLoaded", fetchSongs);
