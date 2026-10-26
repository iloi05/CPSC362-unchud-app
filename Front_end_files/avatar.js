const SIZE = 64;
const SCALE = 5;
const BASE = "/assets/";

// body options
const BODIES = {
    "Light": "body_one.png",
    "Tan": "body_two.png",
    "Brown": "body_three.png",
};

// layering clothes
const FIXED_LAYERS = ["undies.png"];

// default body
let selectedBody = "Light";

/* data persistence, user's character pick stays 
same even after termination of page
*/
try {
    const saved = localStorage.getItem("avatarBody");
    if (saved && BODIES[saved]) selectedBody = saved;
} catch (e) {}

// loads image file once and remembes it, same file never downloads twice
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
// Sets up avatar canvas to be drawn on
const canvas = document.getElementById("avatarCanvas");
const ctx = canvas.getContext("2d");
ctx.imageSmoothingEnabled = false;
/*  redrawing character from scratch:
- gathers files
- waits for files to load
- wipes canvas
- stacks layers
*/
async function drawAvatar() {
    const paths = [BODIES[selectedBody], ...FIXED_LAYERS];
    const layers = await Promise.all(paths.map(loadImage));
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const img of layers) {
        ctx.drawImage(img, 0, 0, SIZE, SIZE, 0, 0, SIZE * SCALE, SIZE * SCALE);
    }
}
// filling dropdown menu for body options
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
// draw avatar once when page 1st loads and makes sure any failure shoes up in console
// .catch is here to get clear message naming file that failed if error were to ever happen
drawAvatar().catch(console.error);