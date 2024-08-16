const canvas = document.getElementById("board");

const backbutton = document.getElementById("back");
const forwardbutton = document.getElementById("forward");

const ctx = canvas.getContext("2d");

const backgroundImage = document.getElementById("goban-image");
const whiteStoneImage = document.getElementById("white-stone");
const blackStoneImage = document.getElementById("black-stone");

const BOARDSIZE = 19;
const STARPOINTS = [4, 10, 16];
const STARPOINTSCALEFACTOR = 0.1;
const SCALEFACTORS = { W: 1.16, B: 1.19 };

const mouse = { x: null, y: null };

let canvasSize = Math.min(window.innerWidth, window.innerHeight);
canvas.width = canvasSize;
canvas.height = canvasSize;

let cellSize = canvasSize / (BOARDSIZE + 1);
let starPointSize = cellSize * STARPOINTSCALEFACTOR;
let color = "B";
const board = Array(BOARDSIZE)
  .fill()
  .map(() => Array(BOARDSIZE).fill(0));
const lastMove = { x: null, y: null };
let visited = [];

const adjacentStones = new Array(BOARDSIZE)
  .fill(0)
  .map(() => new Array(BOARDSIZE).fill(0).map(() => []));

for (let y = 0; y < BOARDSIZE; y++) {
  for (let x = 0; x < BOARDSIZE; x++) {
    const directions = [
      { x: x, y: y - 1 }, // top
      { x: x - 1, y: y }, // left
      { x: x + 1, y: y }, // right
      { x: x, y: y + 1 }, // bottom
    ].filter(
      (dir) =>
        dir.x >= 0 &&
        dir.x <= BOARDSIZE - 1 &&
        dir.y >= 0 &&
        dir.y <= BOARDSIZE - 1,
    );
    adjacentStones[y][x] = directions;
  }
}

window.addEventListener("resize", function () {
  canvasSize = Math.min(window.innerWidth, window.innerHeight);
  canvas.width = canvasSize;
  canvas.height = canvasSize;

  cellSize = canvasSize / (BOARDSIZE + 1);
  starPointSize = cellSize * STARPOINTSCALEFACTOR;
  mouse.x = null;
  mouse.y = null;
});

canvas.addEventListener("mousemove", (e) => {
  mouse.x = e.x;
  mouse.y = e.y;
});

canvas.addEventListener("click", function (e) {
  let [x, y, exists] = getXY();

  if (exists) {
    //validate move

    board[y][x] = color;
    lastMove.x = x;
    lastMove.y = y;

    removeCaptures();
    swapPlayers();
  }
});

canvas.addEventListener("contextmenu", function (event) {
  let [x, y, exists] = getXY();
  // add some nice analysis tool

  event.preventDefault();
});

// Helper functions

function getXY() {
  if (mouse.x === null || mouse.y === null) return [null, null, false];

  x = Math.round(mouse.x / cellSize);
  y = Math.round(mouse.y / cellSize);

  const distance =
    Math.pow(mouse.x - cellSize * x, 2) + Math.pow(mouse.y - cellSize * y, 2);
  const maxDistance = Math.pow(cellSize / 2, 2);

  if (distance > maxDistance) return [null, null, false];
  if (x == 0 || x == BOARDSIZE + 1 || y == 0 || y == BOARDSIZE + 1)
    return [null, null, false];
  if (!board[y - 1][x - 1] == 0) return [null, null, false];

  return [x - 1, y - 1, true];
}

function removeCaptures() {
  for (let y = 0; y < BOARDSIZE; y++) {
    for (let x = 0; x < BOARDSIZE; x++) {
      visited = [];
      hasLibs = hasLiberties(x, y);
      if (!hasLibs) {
        for (const move of visited) {
          board[move[1]][move[0]] = 0;
        }
      }
    }
  }
}

function hasLiberties(x, y) {
  neighbors = adjacentStones[y][x];

  for (const n of neighbors) {
    if (board[n.y][n.x] === 0) {
      return true;
    }
  }

  visited.push([x, y]);
  console.log(visited);
  for (const n of neighbors) {
    if (
      board[n.y][n.x] != color &&
      !visited.some(([oldX, oldY]) => oldX === n.x && oldY === n.y)
    ) {
      console.log("checking " + n.x, n.y);
      hasLibs = hasLiberties(n.x, n.y);
      console.log(hasLibs);
      if (hasLibs) {
        return true;
      }
    }
  }

  return false;
}

function swapPlayers() {
  color = color == "B" ? "W" : "B";
}

// Drawing functions

function drawBoard() {
  ctx.drawImage(backgroundImage, 0, 0, canvasSize, canvasSize);
  // Draw verticle lines
  for (let i = 1; i <= BOARDSIZE; i++) {
    ctx.beginPath();
    ctx.moveTo(cellSize, i * cellSize);
    ctx.lineTo(canvasSize - cellSize, i * cellSize);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(i * cellSize, cellSize);
    ctx.lineTo(i * cellSize, canvasSize - cellSize);
    ctx.stroke();
  }
  // Draw Star points
  for (const x of STARPOINTS) {
    for (const y of STARPOINTS) {
      ctx.fillStyle = "black";
      ctx.beginPath();
      ctx.arc(x * cellSize, y * cellSize, starPointSize, 0, 2 * Math.PI);
      ctx.fill();
    }
  }
}

function drawPlacedStones() {
  for (let y = 0; y < BOARDSIZE; y++) {
    for (let x = 0; x < BOARDSIZE; x++) {
      const color = board[y][x];
      if (color != 0) {
        drawCircle(x, y, color);
      }
    }
  }
}

function drawCircle(x, y, color, opacity = 1.0) {
  stoneImage = color == "B" ? blackStoneImage : whiteStoneImage;
  scaledCellSize = cellSize * SCALEFACTORS[color];
  ctx.globalAlpha = opacity;
  ctx.drawImage(
    stoneImage,
    (x + 1) * cellSize - scaledCellSize / 2,
    (y + 1) * cellSize - scaledCellSize / 2,
    scaledCellSize,
    scaledCellSize,
  );
  ctx.globalAlpha = 1.0;
  if (lastMove.x == x && lastMove.y == y) {
    ctx.fillStyle = "red";
    ctx.beginPath();
    ctx.arc(
      (x + 1) * cellSize,
      (y + 1) * cellSize,
      cellSize / 7,
      0,
      2 * Math.PI,
    );
    ctx.fill();
  }
}

function animate() {
  ctx.clearRect(0, 0, canvasSize, canvasSize);
  drawBoard();
  drawPlacedStones();

  let [x, y, exists] = getXY();
  if (exists) {
    drawCircle(x, y, color, (opacity = 0.5));
  }

  // ----------------------
  for (s of visited) {
    ctx.fillStyle = "purple";
    ctx.beginPath();
    ctx.arc(
      (s.x + 1) * cellSize,
      (s.y + 1) * cellSize,
      cellSize / 7,
      0,
      2 * Math.PI,
    );
  }

  requestAnimationFrame(animate);
}

animate();
