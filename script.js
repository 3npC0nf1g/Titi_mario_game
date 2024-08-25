function calculateMaxZombies({ screenWidth, zombieWidth }) {
  const maxZombies = Math.floor(screenWidth / zombieWidth);
  return maxZombies;
}

const gameData = []; // Tableau pour stocker les données d'entraînement
const mario = document.getElementById("mario");
const road = document.getElementById("road");
const scoreDisplay = document.getElementById("score");
let score = 0;
let obstacles = [];
let speed = 5;
let marioSpeed = 50;
let zombieSpeed = 0.3;

const needMax =
  calculateMaxZombies({ screenWidth: window.innerWidth, zombieWidth: 50 }) *
  0.66;

const MIN_Z = Math.ceil(needMax * 0.25);
const MAX_Z = Math.ceil(needMax * 1);

let stepMaxZombie = 5;
let stepMinZombie = 3;

const maxSpeed = 5;
let intervalId;
const nb = { maxZombies: 1, minZombies: 1 };

document.addEventListener("keydown", moveMario);

function incrementZombie() {
  const { minZombies, maxZombies } = nb;
  if (minZombies < MIN_Z) {
    nb.minZombies = nb.minZombies + stepMinZombie;
  }
  if (maxZombies < MAX_Z) {
    nb.maxZombies = nb.maxZombies + stepMaxZombie;
  }
}

function moveMario(event) {
  const marioLeft = parseInt(
    window.getComputedStyle(mario).getPropertyValue("left")
  );
  const marioTop = parseInt(
    window.getComputedStyle(mario).getPropertyValue("top")
  );
  const roadWidth = road.offsetWidth;
  const roadHeight = road.offsetHeight;

  if (event.key === "ArrowUp" && marioTop > 50) {
    mario.style.top = marioTop - marioSpeed + "px";
  }

  if (event.key === "ArrowDown" && marioTop < roadHeight - (50 + marioSpeed)) {
    mario.style.top = marioTop + marioSpeed + "px";
  }

  if (event.key === "ArrowLeft" && marioLeft > 50) {
    mario.style.left = marioLeft - marioSpeed + "px";
  }
  if (event.key === "ArrowRight" && marioLeft < roadWidth - 50) {
    mario.style.left = marioLeft + marioSpeed + "px";
  }
}

function createZombie() {
  const zombie = document.createElement("div");
  zombie.classList.add("zombie");
  zombie.style.left =
    Math.floor(Math.random() * (road.offsetWidth - 50)) + "px";
  zombie.style.top =
    -Math.floor(Math.random() * road.offsetHeight * 0.25) + "px";
  road.appendChild(zombie);
  if (zombie instanceof HTMLElement) {
    // Vérification avant ajout
    obstacles.push(zombie);
  }
}

function createMultipleZombies() {
  const { maxZombies, minZombies } = nb;
  const numberOfZombies =
    Math.floor(Math.random() * (maxZombies - minZombies + 1)) + minZombies;
  for (let i = 0; i < numberOfZombies; i++) {
    createZombie();
  }
}

function moveZombies() {
  obstacles.forEach((zombie, index) => {
    const zombieTop = parseInt(
      window.getComputedStyle(zombie).getPropertyValue("top")
    );

    if (zombieTop >= road.offsetHeight) {
      obstacles.splice(index, 1);
      zombie.remove();
      score++;

      incrementZombie();

      scoreDisplay.textContent = "Score : " + score;
      if (speed < maxSpeed) {
        speed += zombieSpeed;
      }
      return false; // exclure le zombie du tableau obstacles
    } else {
      zombie.style.top = zombieTop + speed + "px";
      return true; // garder le zombie
    }
  });
  obstacles.forEach(zombie => {
    if (checkCollision(mario, zombie)) {
      triggerBoomAnimation(mario, zombie, score);
      saveGameData(); // Sauvegarder les données du jeu à ce moment
      clearInterval(intervalId);
      score = 0;
    }
  });
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

function triggerBoomAnimation(mario, zombie, score) {
  const boom = document.createElement("div");
  boom.classList.add("boom");
  boom.style.left = mario.style.left;
  boom.style.top = mario.style.top;
  boom.innerHTML = `<p class="boom-score">Score: ${score}</p>`;
  road.appendChild(boom);

  setTimeout(() => {
    boom.remove();
  }, 1500);
}

function startGame() {
  createMultipleZombies();
  setInterval(createMultipleZombies, 2000);
  intervalId = setInterval(moveZombies, 20);
  setInterval(collectGameData, 2000);
}

//////////

function calculateMove(marioLeft, marioTop, zombies) {
  // Trouver le meilleur déplacement en fonction de tous les zombies
  let totalMoveX = 0;
  let totalMoveY = 0;

  zombies.forEach(zombie => {
    if (zombie instanceof HTMLElement) {
      const zombieLeft = parseInt(
        window.getComputedStyle(zombie).getPropertyValue("left")
      );
      const zombieTop = parseInt(
        window.getComputedStyle(zombie).getPropertyValue("top")
      );

      // Calculer la distance euclidienne
      const distance = Math.sqrt(
        Math.pow(marioLeft - zombieLeft, 2) + Math.pow(marioTop - zombieTop, 2)
      );

      // Facteur de danger basé sur la distance (les zombies plus proches ont plus d'impact)
      const dangerFactor = 1 / (distance + 0.1); // Ajout de 0.1 pour éviter la division par zéro

      // Ajouter la contribution de ce zombie au mouvement total
      totalMoveX += (marioLeft - zombieLeft) * dangerFactor;
      totalMoveY += (marioTop - zombieTop) * dangerFactor;
    }
  });

  // Normaliser les mouvements pour obtenir une direction unitaire
  const magnitude = Math.sqrt(
    totalMoveX * totalMoveX + totalMoveY * totalMoveY
  );
  const move_x = magnitude > 0 ? totalMoveX / magnitude : 0;
  const move_y = magnitude > 0 ? totalMoveY / magnitude : 0;

  return { move_x, move_y };
}

function collectGameData() {
  const marioLeft = parseInt(
    window.getComputedStyle(mario).getPropertyValue("left")
  );
  const marioTop = parseInt(
    window.getComputedStyle(mario).getPropertyValue("top")
  );

  // Obtenir les positions des zombies valides
  const zombiesData = obstacles
    .filter(zombie => zombie instanceof HTMLElement) // Filtrer les éléments non DOM
    .map(zombie => {
      return {
        left: parseInt(
          window.getComputedStyle(zombie).getPropertyValue("left")
        ),
        top: parseInt(window.getComputedStyle(zombie).getPropertyValue("top")),
      };
    });

  // Calculer le mouvement optimal pour Mario (pour l'entraînement)
  const { move_x, move_y } = calculateMove(marioLeft, marioTop, zombiesData);

  // Convertir les données des zombies en un tableau plat
  const zombiesFlat = zombiesData.flatMap(z => [z.left, z.top]);

  // Ajouter les données collectées au tableau gameData
  gameData.push([marioLeft, marioTop, ...zombiesFlat, move_x, move_y]);

  console.log("Données collectées :", [
    marioLeft,
    marioTop,
    ...zombiesFlat,
    move_x,
    move_y,
  ]); // Debug
}

function saveGameData() {
  console.log("Données avant sauvegarde :", gameData); // Debug
  if (gameData.length === 0) {
    console.error("Le tableau de données est vide !");
    return;
  }

  const blob = new Blob([JSON.stringify(gameData)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "game_data.json";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
/////

startGame();
