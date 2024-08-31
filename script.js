const socket = new WebSocket("ws://localhost:8765");

const messageQueue = [];

function sendMessage(socket, message) {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(message);
  } else {
    console.warn("WebSocket is not open. Cannot send message.");
  }
}

function queueOrSend(message) {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(message);
  } else {
    messageQueue.push(message);
  }
}

socket.addEventListener("open", function () {
  console.log("WebSocket connection established");

  while (messageQueue.length > 0) {
    const message = messageQueue.shift();
    socket.send(message);
  }
});

socket.addEventListener("message", function (event) {
  const message = JSON.parse(event.data);
  if (message.type === "ai_move") {
    const { data: action } = message;
    console.log("Receive AI Move", action);
    handleMarioAIMovement(action);
  }
});

socket.addEventListener("error", function (event) {
  console.error("WebSocket error:", event);
});

socket.addEventListener("close", function (event) {
  console.log("WebSocket connection closed:", event);
});

function getCurrentState() {
  return {
    type: "game_state",
    data: {
      mario: {
        left: parseInt(window.getComputedStyle(mario).getPropertyValue("left")),
        top: parseInt(window.getComputedStyle(mario).getPropertyValue("top")),
      },
      zombies: obstacles.map((zombie) => ({
        left: parseInt(
          window.getComputedStyle(zombie).getPropertyValue("left")
        ),
        top: parseInt(window.getComputedStyle(zombie).getPropertyValue("top")),
      })),
      score,
      collision: isCollision,
    },
  };
}

function getStateAndSendtoAI() {
  const state = getCurrentState();
  console.log("Send State to AI", state);
  sendMessage(socket, JSON.stringify(state));
}

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

const maxZombiesNeeded = Math.ceil(
  calculateMaxZombies(screenWidth, zombieWidth) * 0.66
);

const MIN_ZOMBIES = Math.ceil(maxZombiesNeeded * 0.5);
const MAX_ZOMBIES = Math.ceil(maxZombiesNeeded);
const STEP_MAX_ZOMBIE = Math.ceil(maxZombiesNeeded * 0.1);
const STEP_MIN_ZOMBIE = Math.ceil(maxZombiesNeeded * 0.05);
const ENABLED_END_ON_COLLISION = false;

let isCollision = false;
let score = 0;
let obstacles = [];
let currentZombieSpeed = initialZombieSpeed;
let zombieCounts = { maxZombies: 1, minZombies: 1 };
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
    top: parseInt(window.getComputedStyle(mario).getPropertyValue("top")),
  };

  const roadDimensions = {
    width: road.offsetWidth,
    height: road.offsetHeight,
  };

  switch (event.key) {
    case "ArrowUp":
      moveMarioVertically(marioPosition, -marioSpeed, roadDimensions.height);
      break;
    case "ArrowDown":
      moveMarioVertically(marioPosition, marioSpeed, roadDimensions.height);
      break;
    case "ArrowLeft":
      moveMarioHorizontally(marioPosition, -marioSpeed, roadDimensions.width);
      break;
    case "ArrowRight":
      moveMarioHorizontally(marioPosition, marioSpeed, roadDimensions.width);
      break;
  }
}

function handleMarioAIMovement(action) {

  const marioPosition = {
    left: parseInt(window.getComputedStyle(mario).getPropertyValue("left")),
    top: parseInt(window.getComputedStyle(mario).getPropertyValue("top")),
  };

  const roadDimensions = {
    width: road.offsetWidth,
    height: road.offsetHeight,
  };

  switch (
    action // exécution des actions venant du jeu
  ) {
    case "Up":
      moveMarioVertically(marioPosition, -marioSpeed, roadDimensions.height);
      getStateAndSendtoAI();
      break;
    case "Down":
      moveMarioVertically(marioPosition, marioSpeed, roadDimensions.height);
      getStateAndSendtoAI();
      break;
    case "Left":
      moveMarioHorizontally(marioPosition, -marioSpeed, roadDimensions.width);
      getStateAndSendtoAI();
      break;
    case "Right":
      moveMarioHorizontally(marioPosition, marioSpeed, roadDimensions.width);
      getStateAndSendtoAI();
    case "Stay":
      getStateAndSendtoAI();
  }
}

function moveMarioVertically(position, movement, roadHeight) {
  if (
    (position.top > 50 && movement < 0) ||
    (position.top < roadHeight - (50 + marioSpeed) && movement > 0)
  ) {
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
  zombie.style.left =
    Math.floor(Math.random() * (road.offsetWidth - 50 - marioSpeed * 0.25)) +
    "px";
  zombie.style.top =
    -Math.floor(Math.random() * road.offsetHeight * 0.25) + "px";
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
}

function getRandomZombieCount() {
  return (
    Math.floor(
      Math.random() * (zombieCounts.maxZombies - zombieCounts.minZombies + 1)
    ) + zombieCounts.minZombies
  );
}

function moveZombies() {
  isCollision = false;
  obstacles.forEach((zombie, index) => {
    const zombieTop = parseInt(
      window.getComputedStyle(zombie).getPropertyValue("top")
    );

    if (zombieTop >= road.offsetHeight) {
      removeZombie(zombie, index);
    } else {
      zombie.style.top = zombieTop + currentZombieSpeed + "px";
    }

    if (checkCollision(mario, zombie)) {
      isCollision = true
      handleCollision({ mario, zombie });
    }
  });
  getStateAndSendtoAI();
}

function removeZombie(zombie, index) {
  obstacles.splice(index, 1);
  zombie.remove();
  score++;
  incrementZombieCount();
  updateScore();
  increaseZombieSpeed();
  getStateAndSendtoAI();
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

function handleCollision({ zombie }) {
  isCollision = true;
  score = 0;
  currentZombieSpeed = initialZombieSpeed;
  zombieCounts = { maxZombies: 1, minZombies: 1 };
  if (ENABLED_END_ON_COLLISION) {
    clearInterval(intervalMoveZombieId);
    clearInterval(intervalCreateZombieId);
    document.removeEventListener("keydown", handleMarioMovement);
    const zombieRect = zombie.getBoundingClientRect();
    triggerBoomAnimation(zombieRect.left, zombieRect.top);
    replayButton.style.display = "block";
  }
  getStateAndSendtoAI();
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

function startGame() {
  createMultipleZombies();
  intervalCreateZombieId = setInterval(createMultipleZombies, 2000);
  intervalMoveZombieId = setInterval(moveZombies, 50);
  getStateAndSendtoAI();
}

startGame();
