document.addEventListener("DOMContentLoaded", function () {
    const timers = document.querySelectorAll("[id^='timer-']");

    timers.forEach(timer => {
        const endTime = new Date(timer.dataset.endtime).getTime();

        function updateTimer() {
            const now = new Date().getTime();
            const distance = endTime - now;

            if (distance <= 0) {
                timer.innerHTML = "⛔ Terminé";
                timer.style.color = "red"; 
                timer.style.fontWeight = "bold";
                timer.style.animation = "";
                return;
            }

            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            timer.innerHTML = minutes + "m " + seconds + "s";

            if (distance > 2 * 60 * 1000) {
                timer.style.color = "green"; 
                timer.style.animation = "";
            } else if (distance > 60 * 1000) {
                timer.style.color = "orange"; 
                timer.style.animation = "";
            } else if (distance > 30 * 1000) {
                timer.style.color = "red"; 
                timer.style.animation = "";
            } else {
                timer.style.color = "red";
                timer.style.fontWeight = "bold";
                timer.style.animation = "blink 1s infinite";

                // 🔔 Bip chaque seconde dans les 10 dernières secondes
                if (seconds <= 10) {
                    playBeep();
                }
            }
        }

        updateTimer();
        setInterval(updateTimer, 1000);
    });
});

// 🔊 Fonction bip
function playBeep() {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.type = "sine"; // onde sinusoïdale
    oscillator.frequency.value = 1200; // fréquence en Hz (un peu plus aigu)
    gainNode.gain.value = 0.2; // volume

    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.2); // durée = 0.2s (court bip)
}

// Animation clignotante
const style = document.createElement('style');
style.innerHTML = `
@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0; }
  100% { opacity: 1; }
}
`;
document.head.appendChild(style);
