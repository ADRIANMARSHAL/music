document.addEventListener("DOMContentLoaded", () => {
    const player = document.getElementById("audioPlayer");
    const playBtn = document.getElementById("playBtn");

    if (playBtn && player) {
        playBtn.addEventListener("click", () => {
            if (player.paused) {
                player.play();
                playBtn.textContent = "Pause";
            } else {
                player.pause();
                playBtn.textContent = "Play";
            }
        });
    }
});
