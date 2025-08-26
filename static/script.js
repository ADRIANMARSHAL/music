// script.js
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm";

// Your Supabase credentials
const SUPABASE_URL = "https://zqmotxqejqnjhtdjxbik.supabase.co"; 
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpxbW90eHFlanFuamh0ZGp4YmlrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU2ODQ4ODIsImV4cCI6MjA3MTI2MDg4Mn0.2sYGb7X0uDAihr8xyDzHOJFEdAX-zeDa-LJ81VhYSJs";

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function loadSongs() {
  try {
    // Fetch songs list from Supabase Storage (bucket: songs)
    const { data: files, error } = await supabase.storage
      .from("songs")
      .list("", { limit: 100 });

    if (error) {
      console.error("Error fetching songs:", error);
      return;
    }

    if (!files || files.length === 0) {
      document.getElementById("songs-list").innerHTML =
        "<p>No songs uploaded yet.</p>";
      return;
    }

    // Clear old list
    const songsList = document.getElementById("songs-list");
    songsList.innerHTML = "";

    // Loop through each song
    for (const file of files) {
      // Generate public URL
      const { data: urlData } = supabase.storage
        .from("songs")
        .getPublicUrl(file.name);

      const songUrl = urlData.publicUrl;

      // Fetch metadata from Supabase table (title, artist, cover)
      const { data: meta, error: metaError } = await supabase
        .from("songs_meta")
        .select("*")
        .eq("file_name", file.name)
        .single();

      if (metaError) {
        console.warn(`No metadata for ${file.name}`);
      }

      // Create song card
      const songCard = document.createElement("div");
      songCard.className =
        "song-card p-4 rounded-lg shadow-md flex items-center gap-4 bg-white mb-4";

      songCard.innerHTML = `
        <img src="${meta?.cover_url || "default-cover.jpg"}" 
             alt="cover" class="w-16 h-16 rounded-lg object-cover">
        <div class="flex-1">
          <h3 class="text-lg font-semibold">${meta?.title || file.name}</h3>
          <p class="text-sm text-gray-600">${meta?.artist || "Unknown Artist"}</p>
        </div>
        <audio controls src="${songUrl}" class="h-10"></audio>
      `;

      songsList.appendChild(songCard);
    }
  } catch (err) {
    console.error("Unexpected error:", err);
  }
}

// Load songs on page load
document.addEventListener("DOMContentLoaded", loadSongs);
