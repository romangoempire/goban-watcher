const canvas = document.getElementById("goban");
const ctx = canvas.getContext("2d");
const socket = new WebSocket("ws://localhost:8765");
// images
const BACKGROUNDIMAGE = document.getElementById("goban-image");
const WHITESTONEIMAGE = document.getElementById("white-stone");
const BLACKSTONEIMAGE = document.getElementById("black-stone");
const BOARDSIZE = 19;
const ANALYSISCOLORS = {
  1: "#8ac926",
  2: "#ffca3a",
  4: "#ff595e",
  6: "#f3722c",
  10: "#f94144",
};

const STARPOINTS = [4, 10, 16];
const STARPOINTSCALEFACTOR = 15;
const SCALEFACTORS = { W: 1.16, B: 1.19 }; // Correction factor for stone images

const mouse = { x: null, y: null };
const placedStones = [];
let analysedPositions = [];

let canvasSize = Math.min(window.innerWidth, window.innerHeight);
canvas.width = canvasSize;
canvas.height = canvasSize;

let cellSize = canvasSize / (BOARDSIZE + 1);
let starPointSize = cellSize / STARPOINTSCALEFACTOR;
let stoneColor = "B";
// Event listener

window.addEventListener("resize", function () {
  canvasSize = Math.min(window.innerWidth, window.innerHeight);
  canvas.width = canvasSize;
  canvas.height = canvasSize;
  cellSize = canvasSize / (BOARDSIZE + 1);
  starPointSize = cellSize / STARPOINTSCALEFACTOR;
  mouse.x = null;
  mouse.y = null;
});

canvas.addEventListener("click", function (event) {
  let [x, y] = getXY();
  if (!(isMouseOnBoard(x, y) && isFreePosition(x, y))) {
    return;
  }

  placedStones.push([stoneColor, x, y]);
  stoneColor = stoneColor == "B" ? "W" : "B";
  analysedPositions = [];
});

canvas.addEventListener("mousemove", (e) => {
  mouse.x = e.x;
  mouse.y = e.y;
});

socket.addEventListener("message", (event) => {
  analysis = event.data;
});

// Utils

function getXY() {
  x = Math.round(mouse.x / cellSize);
  y = Math.round(mouse.y / cellSize);
  return [x, y];
}

function isMouseOnBoard(x, y) {
  return x >= 1 && x <= 19 && y >= 1 && y <= 19;
}

function isFreePosition(newX, newY) {
  return !placedStones.some(([color, x, y]) => x == newX && y == newY);
}

function coordinateToXY(coordinate) {
  return [
    "ABCDEFGHJKLMNOPQRST".indexOf(coordinate[0]) + 1,
    20 - parseInt(coordinate.slice(1)),
  ];
}

function xyToCoordinate(x, y) {
  return `${"ABCDEFGHJKLMNOPQRST"[x - 1]}${20 - y}`;
}

function getNextLargestColor(num) {
  smallest = Math.min(...Object.keys(ANALYSISCOLORS).filter((k) => -k < num));
  if (smallest == Infinity) {
    return 10;
  }
  return smallest;
}

// api request
function analyse() {
  fetch("http://localhost:8000/analyse", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(placedStones),
  })
    .then((response) => response.json())
    .then((data) => analysedPositions.push(data))
    .catch((error) => console.error("Error:", error));
}

// canvas drawing

function drawBoard() {
  // Draw verticle lines
  for (let i = 1; i <= 19; i++) {
    ctx.beginPath();
    ctx.moveTo(cellSize, i * cellSize);
    ctx.lineTo(canvasSize - cellSize, i * cellSize);
    ctx.stroke();
  }
  // Draw horizontal lines
  for (let i = 1; i <= 19; i++) {
    ctx.beginPath();
    ctx.moveTo(i * cellSize, cellSize);
    ctx.lineTo(i * cellSize, canvasSize - cellSize);
    ctx.stroke();
  }

  // Draw Star points
  for (const x of STARPOINTS) {
    for (const y of STARPOINTS) {
      ctx.beginPath();
      ctx.arc(x * cellSize, y * cellSize, starPointSize, 0, 2 * Math.PI);
      ctx.fillStyle = "black";
      ctx.fill();
    }
  }
}

function drawPlacedStones() {
  for ([color, x, y] of placedStones) {
    drawCircle(x, y, color);
  }
}

function drawAnalysis() {
  moves;
  for (const move of moves) {
    console.log(moves);
    let [x, y] = coordinateToXY(move["move"]);
    //let scoreLead = move["scoreLead"];
    // if (placedStones.length == 0) {
    //   scoreDifference = scoreLead;
    // } else {
    //   scoreDifference = move["scoreLead"] - initialScoreLead;
    //   if (stoneColor == "W") {
    //     scoreDifference *= -1;
    //   }
    // }
    // if (scoreDifference < -4) {
    //   continue;
    // }

    ctx.globalAlpha = 1;
    // ctx.fillStyle = ANALYSISCOLORS[getNextLargestColor(scoreDifference)];
    ctx.fillStyle = "green";
    ctx.beginPath();
    ctx.arc(x * cellSize, y * cellSize, cellSize / 2, 0, 2 * Math.PI);
    ctx.fill();

    // Write the move number inside the circle
    // ctx.font = "12px Arial";
    // ctx.fillStyle = "white";
    // ctx.textAlign = "center";
    // ctx.textBaseline = "middle";
    // ctx.fillText(
    //   Math.round(scoreDifference * 10) / 10,
    //   x * cellSize,
    //   y * cellSize,
    // );
  }
  // ctx.globalAlpha = 1.0;
}

function drawCircle(x, y, color, opacity = 1.0) {
  stoneImage = color == "B" ? BLACKSTONEIMAGE : WHITESTONEIMAGE;
  scaledCellSize = cellSize * SCALEFACTORS[color];
  ctx.globalAlpha = opacity;
  ctx.drawImage(
    stoneImage,
    x * cellSize - scaledCellSize / 2,
    y * cellSize - scaledCellSize / 2,
    scaledCellSize,
    scaledCellSize,
  );
  ctx.globalAlpha = 1.0;
}

function animate() {
  ctx.clearRect(0, 0, canvasSize, canvasSize);
  ctx.drawImage(BACKGROUNDIMAGE, 0, 0, canvasSize, canvasSize);

  drawBoard();
  drawAnalysis();
  let [x, y] = getXY();

  if (!(x === null || y === null)) {
    if (isMouseOnBoard(x, y) && isFreePosition(x, y)) {
      drawCircle(x, y, stoneColor);
    }
    drawPlacedStones();
  }

  requestAnimationFrame(animate);
}

animate();
