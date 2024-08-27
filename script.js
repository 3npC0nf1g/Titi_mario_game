function calculateMaxZombies(screenWidth, zombieWidth) {
    return Math.floor(screenWidth / zombieWidth);
}

const mario = document.getElementById("mario");
const road = document.getElementById("road");
const scoreDisplay = document.getElementById("score");
const replayButton = document.getElementById("replay");

const initialZombieSpeed = 5;
const marioSpeed = 50;
const zombieSpeedIncrement = 0.3;
const maxSpeedZombie = 7;
const zombieWidth = 50;
const screenWidth = window.innerWidth;

const maxZombiesNeeded = Math.ceil(calculateMaxZombies(screenWidth, zombieWidth) * 0.66);
const MIN_ZOMBIES = Math.ceil(maxZombiesNeeded * 0.50);
const MAX_ZOMBIES = Math.ceil(maxZombiesNeeded);
const STEP_MAX_ZOMBIE = Math.ceil(maxZombiesNeeded * 0.1);
const STEP_MIN_ZOMBIE = Math.ceil(maxZombiesNeeded * 0.05);

let score = 0;
let obstacles = [];
let currentZombieSpeed = initialZombieSpeed;
let zombieCounts = {maxZombies: 1, minZombies: 1};
let trainingData = [];
let intervalCreateZombieId, intervalMoveZombieId;

replayButton.addEventListener("click", () => window.location.reload());
document.addEventListener("keydown", handleMarioMovement);

function incrementZombieCount() {
    if (zombieCounts.minZombies < MIN_ZOMBIES) {
        zombieCounts.minZombies += STEP_MIN_ZOMBIE;
    }
    if (zombieCounts.maxZombies < MAX_ZOMBIES) {
        zombieCounts.maxZombies += STEP_MAX_ZOMBIE;
    }
}

function handleMarioMovement(event) {
    const marioPosition = {
        left: parseInt(window.getComputedStyle(mario).getPropertyValue("left")),
        top: parseInt(window.getComputedStyle(mario).getPropertyValue("top"))
    };
    const roadDimensions = {
        width: road.offsetWidth,
        height: road.offsetHeight
    };

    switch (event.key) {
        case "ArrowUp":
            moveMarioVertically(marioPosition, -marioSpeed, roadDimensions.height);
            saveTrainingData("move", "up", {marioPosition, roadDimensions});
            break;
        case "ArrowDown":
            moveMarioVertically(marioPosition, marioSpeed, roadDimensions.height);
            saveTrainingData("move", "down", {marioPosition, roadDimensions});
            break;
        case "ArrowLeft":
            moveMarioHorizontally(marioPosition, -marioSpeed, roadDimensions.width);
            saveTrainingData("move", "left", {marioPosition, roadDimensions});
            break;
        case "ArrowRight":
            moveMarioHorizontally(marioPosition, marioSpeed, roadDimensions.width);
            saveTrainingData("move", "right", {marioPosition, roadDimensions});
            break;
    }
}

function moveMarioVertically(position, movement, roadHeight) {
    if (position.top > 50 && movement < 0 || position.top < roadHeight - (50 + marioSpeed) && movement > 0) {
        mario.style.top = position.top + movement + "px";
    }
}

function moveMarioHorizontally(position, movement, roadWidth) {
    let newPosition = position.left + movement;
    newPosition = Math.max(25, Math.min(newPosition, roadWidth - 25));
    mario.style.left = newPosition + "px";
}

function createZombie() {
    const zombie = document.createElement("div");
    zombie.classList.add("zombie");
    zombie.style.left = Math.floor(Math.random() * (road.offsetWidth - 50 - (marioSpeed * 0.25))) + "px";
    zombie.style.top = -Math.floor(Math.random() * road.offsetHeight * 0.25) + "px";
    road.appendChild(zombie);
    obstacles.push(zombie);
}

function getRandomPosition(maxValue) {
    return Math.floor(Math.random() * maxValue);
}

function createMultipleZombies() {
    const numberOfZombies = getRandomZombieCount();
    for (let i = 0; i < numberOfZombies; i++) {
        createZombie();
    }
    saveTrainingData("spawn", "zombies", {numberOfZombies});
}

function getRandomZombieCount() {
    return Math.floor(Math.random() * (zombieCounts.maxZombies - zombieCounts.minZombies + 1)) + zombieCounts.minZombies;
}

function moveZombies() {
    obstacles.forEach((zombie, index) => {
        const zombieTop = parseInt(window.getComputedStyle(zombie).getPropertyValue("top"));

        if (zombieTop >= road.offsetHeight) {
            removeZombie(zombie, index);
        } else {
            zombie.style.top = zombieTop + currentZombieSpeed + "px";
        }

        if (checkCollision(mario, zombie)) {
            handleCollision({mario, zombie});
        }
    });
}

function removeZombie(zombie, index) {
    obstacles.splice(index, 1);
    zombie.remove();
    score++;
    incrementZombieCount();
    updateScore();
    increaseZombieSpeed();
}

function updateScore() {
    scoreDisplay.textContent = `Score: ${score}`;
}

function increaseZombieSpeed() {
    if (currentZombieSpeed < maxSpeedZombie) {
        currentZombieSpeed += zombieSpeedIncrement;
    }
}

function checkCollision(mario, zombie) {
    const marioRect = mario.getBoundingClientRect();
    const zombieRect = zombie.getBoundingClientRect();

    return !(
        marioRect.top > zombieRect.bottom ||
        marioRect.bottom < zombieRect.top ||
        marioRect.right < zombieRect.left ||
        marioRect.left > zombieRect.right
    );
}

function handleCollision({zombie}) {
    saveTrainingData("collision", "zombie", {score});
    clearInterval(intervalMoveZombieId);
    clearInterval(intervalCreateZombieId);
    document.removeEventListener("keydown", handleMarioMovement);
    const zombieRect = zombie.getBoundingClientRect();
    triggerBoomAnimation(zombieRect.left, zombieRect.top);
    replayButton.style.display='block';
    saveTrainingData("game", "end", {finalScore: score});
    saveTrainingDataToFile();
}

function triggerBoomAnimation(x, y) {
    const boom = document.createElement("div");
    boom.classList.add("boom");
    boom.style.left = `${x + 25}px`;
    boom.style.top = `${y + 25}px`;
    road.appendChild(boom);

    setTimeout(() => {
        boom.remove();
    }, 700);
}


function saveTrainingData(actionType, actionDetail, additionalData = {}) {
    const gameState = {
        timestamp: new Date().toISOString(),
        score,
        marioPosition: {
            left: parseInt(mario.style.left),
            top: parseInt(mario.style.top)
        },
        obstacles: obstacles.map(zombie => ({
            left: parseInt(zombie.style.left),
            top: parseInt(zombie.style.top)
        })),
        speed: currentZombieSpeed,
        actionType,
        actionDetail,
        ...additionalData
    };
    trainingData.push(gameState);
}

function saveTrainingDataToFile() {
    const date = new Date();
    const formattedDate = `${date.getFullYear()}-${date.getMonth()}-${date.getDay()}`;
    const formattedTime = `${date.getHours()}h${date.getMinutes()}m${date.getSeconds()}s`;
    const filename = `training_data_${formattedDate}_${formattedTime}.json`;

    const dataStr = JSON.stringify(trainingData, null, 2);
    const blob = new Blob([dataStr], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function startGame() {
    createMultipleZombies();
    intervalCreateZombieId = setInterval(createMultipleZombies, 2000);
    intervalMoveZombieId = setInterval(moveZombies, 20);
    saveTrainingData("game", "start");
}

startGame();
