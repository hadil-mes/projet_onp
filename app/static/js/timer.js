document.addEventListener("DOMContentLoaded", function () {
    const timers = document.querySelectorAll("[id^='timer-']");

    // ✅ Fonction pour générer un beep sans fichier
    function playBeep() {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = ctx.createOscillator();
        const gainNode = ctx.createGain();

        oscillator.type = "sine";      // forme d'onde (sine = bip pur)
        oscillator.frequency.value = 800; // fréquence en Hz
        gainNode.gain.value = 0.1;     // volume

        oscillator.connect(gainNode);
        gainNode.connect(ctx.destination);

        oscillator.start();
        oscillator.stop(ctx.currentTime + 0.2); // durée du bip (0.2s)
    }

    timers.forEach(timer => {
        const endTime = Date.parse(timer.dataset.endtime);

        function updateTimer() {
            const now = new Date().getTime();
            const distance = endTime - now;

            if (distance <= 0) {
                timer.innerHTML = "<span style='color:red; font-weight:bold;'>⛔ Terminé</span>";
                return;
            }

            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);
            let timeString = `${minutes}m ${seconds}s`;

            if (distance <= 10 * 1000) {
                timer.innerHTML = `<span style="color:red; font-weight:bold;">⏳ ${timeString}</span>`;
                
                // ✅ Beep dans les 3 dernières secondes
                if (seconds <= 3 && seconds > 0) {
                    playBeep();
                }
            } else if (distance <= 3 * 60 * 1000) {
                timer.innerHTML = `<span style="color:orange; font-weight:bold;">⚠️ ${timeString}</span>`;
            } else {
                timer.innerHTML = `<span style="color:green; font-weight:bold;">🟢 ${timeString}</span>`;
            }
        }

        updateTimer();
        setInterval(updateTimer, 1000);
    });
});
