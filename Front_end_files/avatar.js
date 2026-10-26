const SIZE = 64;
const SCALE = 5;
const BASE = "/assets/";

const BODIES = {
    "Light": "body_one.png",
    "Tan": "body_two.png",
    "Brown": "body_three.png",
};

const FIXED_LAYERS = [];

let selectedBody = "Light";

try {
    const saved = localStorage.getItem("avatarBody");
    if (saved && BODIES[saved]) selectedBody = saved;
} catch (e) {}

const imageCache = {};
function loadImage(path) {
    if (!imageCache[path]) {
        imageCache[path] = new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = () => reject(new Error("Could not load " + path));
            img.src = BASE + path;
        });
    }
    return imageCache[path];
}

const canvas = document.getElementById("avatarCanvas");
const ctx = canvas.getContext("2d");
ctx.imageSmoothingEnabled = false;

async function drawAvatar() {
    const paths = [BODIES[selectedBody], ...FIXED_LAYERS];
    const layers = await Promise.all(paths.map(loadImage));
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const img of layers) {
        ctx.drawImage(img, 0, 0, SIZE, SIZE, 0, 0, SIZE * SCALE, SIZE * SCALE);
    }
}

const select = document.getElementById("bodySelect");
for (const name of Object.keys(BODIES)) {
    select.add(new Option(name, name));
}
select.value = selectedBody;
select.onchange = () => {
    selectedBody = select.value;
    try { localStorage.setItem("avatarBody", selectedBody); } catch (e) {}
    drawAvatar();
};

drawAvatar().catch(console.error);