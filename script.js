const canvases = document.querySelectorAll('.canvas');

canvases.forEach((canvas) => {
    const ctx = canvas.getContext('2d');

    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    const img = new Image();
    img.src = 'coin.png';

    img.onload = () => {
        ctx.drawImage(img, 0, 0, rect.width, rect.height);
    };

    function erase(x, y) {
        ctx.globalCompositeOperation = 'destination-out';
        ctx.beginPath();
        ctx.arc(x, y, 20, 0, Math.PI * 2);
        ctx.fill();
    }

    // 🖱 ПК
    canvas.addEventListener('mousemove', (e) => {
        if (e.buttons === 1) {
            erase(e.offsetX, e.offsetY);
        }
    });

    // 📱 Телефон
    canvas.addEventListener('touchmove', (e) => {
        e.preventDefault();

        const rect = canvas.getBoundingClientRect();
        const touch = e.touches[0];

        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;

        erase(x, y);
    }, { passive: false });

    canvas.addEventListener('touchstart', (e) => {
        const rect = canvas.getBoundingClientRect();
        const touch = e.touches[0];

        erase(touch.clientX - rect.left, touch.clientY - rect.top);
    });
});

let animitems = document.querySelectorAll('._anim-items')
const timerContainer = document.getElementById('timerContainer');
const daysElement = document.getElementById('days');
const hoursElement = document.getElementById('hours');
const minutesElement = document.getElementById('minutes');
const secondsElement = document.getElementById('seconds');

let isPlaying = false

if (animitems.length > 0) {
    window.addEventListener("scroll", animOnScroll);
    function animOnScroll(params) {
        for (let i = 0; i < animitems.length; i++) {
            const animitem = animitems[i]
            const animitemHeight = animitem.offsetHeight
            const animitemOffset = offset(animitem).top
            const animStart = 1;

            let animitemPoint = window.innerHeight - animitemHeight / animStart;

            if (animitemHeight > window.innerHeight) {
                animitemPoint = window.innerHeight - window.innerHeight / animStart;
            }

            if ((pageYOffset > animitemOffset - animitemPoint) && pageYOffset < (animitemOffset + animitemHeight)) {
                animitem.classList.add("active")
            } else {
                animitem.classList.remove("active")
            }
        }
    }
    function offset(el) {
        const rect = el.getBoundingClientRect();
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
        const scrollTop = window.pageXOffset || document.documentElement.scrollTop
        return { top: rect.top + scrollTop, left: rect.left + scrollLeft }
    }

}


window.addEventListener('DOMContentLoaded', function () {
    const audioElement = document.getElementById('audioElement');
    const audiobtn = document.getElementById('audiobtnRef');
    const audioImg = document.getElementById('audioImg');

    audiobtn.addEventListener('click', function () {
        if (audioElement.paused) {
            audioElement.play();
            audioImg.src = "Play.png";
        } else {
            audioElement.pause();
            audioImg.src = "Pause.png";
        }
    });

    audiobtn.style.cursor = 'pointer';
    audiobtn.style.zIndex = '1000';
});

function disableScroll() {
    document.body.style.overflow = 'hidden';
}

function enableScroll() {
    document.body.style.overflow = '';
}

if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
}

window.onload = () => {
    window.scrollTo(0, 0);
};

disableScroll();

const video = document.querySelector('video');

const anim1 = document.querySelector('.name1');
const anim2 = document.querySelector('.and');
const anim3 = document.querySelector('.name2');

video.addEventListener('ended', () => {

    anim1.classList.add('act');
    anim2.classList.add('act');
    anim3.classList.add('act');
    enableScroll()

});

const targetDate = new Date('2026-09-26T00:00:00');

function calculateTimeLeft() {
    const difference = targetDate - new Date();
    if (difference <= 0) return null;

    return {
        days: Math.floor(difference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((difference / (1000 * 60)) % 60),
        seconds: Math.floor((difference / 1000) % 60),
    };
}


function updateTimer() {
    const timeLeft = calculateTimeLeft();

    if (!timeLeft) {
        timerContainer.innerHTML = '<div class="left"">Time over</div>';
        return;
    }

    daysElement.textContent = String(timeLeft.days).padStart(2, '0');
    hoursElement.textContent = String(timeLeft.hours).padStart(2, '0');
    minutesElement.textContent = String(timeLeft.minutes).padStart(2, '0');
    secondsElement.textContent = String(timeLeft.seconds).padStart(2, '0');
}

setInterval(updateTimer, 1000);
updateTimer();