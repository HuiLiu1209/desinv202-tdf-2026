// ============================================================
// Expressive Mechanics — Face Expression Detection
// Uses ml5 FaceMesh to detect eye closure, eyebrow raise,
// and mouth opening, then sends the three expression states
// to Arduino through Web Serial.
//
// Serial format:
// eyesClosed,browsRaised,mouthOpen
// Example: 1,0,1
// ============================================================


//Face tracking setup

let faceMesh;
let video;
let faces = [];

let options = { maxFaces: 1, refineLandmarks: true, flipHorizontal: false };

// Calibration stores my neutral facial measurements.
// Expression detection is based on changes relative to this baseline.
let calibrated = false;
let baseEye, baseMouth, baseBrow;

//Arduino Web Serial connection
let smoothEye = null, smoothMouth = null, smoothBrow = null;

let currentEye = 0, currentMouth = 0, currentBrow = 0;

// Arduino protocol: eyesClosed,browsRaised,mouthOpen + newline.
let arduinoPort = null;
let arduinoWriter = null;
let serialBusy = false;
let serialConnecting = false;
let lastSerialSend = 0;
let serialButton, serialStatus;

// Camera and FaceMesh setup
async function setup() {
  createCanvas(640, 480);
  serialButton = createButton("Connect Arduino");
  serialButton.mousePressed(connectArduino);
  serialStatus = createP("Arduino: not connected");
  video = createCapture(VIDEO);
  video.size(640, 480);
  video.hide();
  faceMesh = await ml5.faceMesh(options);
  faceMesh.detectStart(video, gotFaces);
  textSize(18);
}

// Detect facial expressions
function draw() {
  background(0);
  image(video, 0, 0, width, height);
  if (faces.length === 0) {
    drawText("No face detected", 20, 30);
    browRaisedState = false;
    browBelowSince = null;
    sendExpression(false, false, false);
    return;
  }
  let kp = faces[0].keypoints;
  let eye1Vertical = pointDistance(kp[159], kp[145]);
  let eye1Width = pointDistance(kp[33], kp[133]);
  let eye1Ratio = eye1Vertical / eye1Width;
  let eye2Vertical = pointDistance(kp[386], kp[374]);
  let eye2Width = pointDistance(kp[362], kp[263]);
  let eye2Ratio = eye2Vertical / eye2Width;
  currentEye = (eye1Ratio + eye2Ratio) / 2;
  let mouthVertical = pointDistance(kp[13], kp[14]);
  let mouthWidth = pointDistance(kp[61], kp[291]);
  currentMouth = mouthVertical / mouthWidth;
  let brow1Ratio = pointDistance(kp[105], kp[159]) / eye1Width;
  let brow2Ratio = pointDistance(kp[334], kp[386]) / eye2Width;
  currentBrow = (brow1Ratio + brow2Ratio) / 2;
  if (smoothEye === null) {
    smoothEye = currentEye;
    smoothMouth = currentMouth;
    smoothBrow = currentBrow;
  } else {
    smoothEye = lerp(smoothEye, currentEye, 0.45);
    smoothMouth = lerp(smoothMouth, currentMouth, 0.25);
    smoothBrow = lerp(smoothBrow, currentBrow, 0.65);
  }
  let eyesClosed = false, mouthOpen = false, browsRaised = false;
  if (calibrated) {
    eyesClosed = smoothEye < baseEye * 0.75;
    mouthOpen = smoothMouth > max(baseMouth * 1.8, baseMouth + 0.035);
    browsRaised = updateBrowState(smoothBrow, baseBrow);
  }
  sendExpression(eyesClosed, browsRaised, mouthOpen);
  drawImportantPoints(kp);
  noStroke();
  fill(0, 180);
  rect(10, 10, 420, 150);
  fill(255);
  if (!calibrated) {
    text("Relax face + press C", 20, 35);
  } else {
    text("EYES: " + (eyesClosed ? "CLOSED" : "OPEN"), 20, 40);
    text("BROW: " + (browsRaised ? "RAISED" : "NORMAL"), 20, 70);
    text("MOUTH: " + (mouthOpen ? "OPEN" : "CLOSED"), 20, 100);
    textSize(12);
    text("eye: " + nf(smoothEye, 1, 3), 20, 125);
    text("brow: " + nf(smoothBrow, 1, 3), 115, 125);
    text("mouth: " + nf(smoothMouth, 1, 3), 210, 125);
    textSize(18);
  }
}

function gotFaces(results) { faces = results; }

// Calibrate neutral face
function keyPressed() {
  if ((key === "c" || key === "C") && faces.length > 0 && smoothEye !== null) {
    baseEye = smoothEye;
    baseMouth = smoothMouth;
    baseBrow = smoothBrow;
    browRaisedState = false;
    browBelowSince = null;
    calibrated = true;
    console.log("CALIBRATED", baseEye, baseMouth, baseBrow);
  }
}
function pointDistance(a, b) { return dist(a.x, a.y, b.x, b.y); }
function drawImportantPoints(kp) {
  let important = [33, 133, 159, 145, 362, 263, 386, 374, 105, 334, 13, 14, 61, 291];
  fill(0, 255, 0);
  noStroke();
  for (let index of important) circle(kp[index].x, kp[index].y, 7);
}
function drawText(t, x, y) { fill(255); noStroke(); text(t, x, y); }

// Connect to Arduino
async function connectArduino() {
  if (serialConnecting || arduinoWriter) return;
  if (!("serial" in navigator)) {
    serialStatus.elt.textContent = "Web Serial unavailable. Open this sketch in Chrome.";
    return;
  }
  serialConnecting = true;
  serialButton.attribute("disabled", "");
  try {
    arduinoPort = await navigator.serial.requestPort();
    await arduinoPort.open({ baudRate: 115200 });
    serialStatus.elt.textContent = "Arduino: connected, waiting for board restart...";
    // UNO may reset when its serial port opens.
    await new Promise(resolve => setTimeout(resolve, 2000));
    arduinoWriter = arduinoPort.writable.getWriter();
    serialButton.html("Arduino connected");
    serialStatus.elt.textContent = "Arduino: ready. Relax your face, click the video and press C.";
    console.log("Arduino connected at 115200 baud");
  } catch (error) {
    await releaseArduino();
    serialStatus.elt.textContent = error.name === "NotFoundError"
      ? "No port selected. Click Connect Arduino to retry."
      : "Connection failed: " + error.message + " Close Arduino Serial Monitor/Plotter, then retry.";
    console.error(error);
  } finally {
    serialConnecting = false;
    if (!arduinoWriter) serialButton.removeAttribute("disabled");
  }
}

// Send expression states to Arduino
async function sendExpression(eyesClosed, browsRaised, mouthOpen) {
  if (!arduinoWriter || serialBusy || millis() - lastSerialSend < 100) return;
  serialBusy = true;
  lastSerialSend = millis();
  const message = [Number(eyesClosed), Number(browsRaised), Number(mouthOpen)].join(",") + "\n";
  try {
    await writeSerialWithTimeout(arduinoWriter, new TextEncoder().encode(message));
    serialStatus.elt.textContent = "Arduino connected | Sent: " + message.trim() +
      (calibrated ? " | calibrated" : " | click video + press C to calibrate");
  } catch (error) {
    await releaseArduino();
    serialStatus.elt.textContent = "Arduino disconnected: " + error.message + " Reconnect to retry.";
    console.error(error);
  } finally {
    serialBusy = false;
  }
}

async function releaseArduino() {
  if (arduinoWriter) {
    try { arduinoWriter.releaseLock(); } catch (error) { console.warn(error); }
    arduinoWriter = null;
  }
  if (arduinoPort) {
    try { await closeSerialWithTimeout(arduinoPort); } catch (error) { console.warn(error); }
    arduinoPort = null;
  }
  serialButton.html("Connect Arduino");
  serialButton.removeAttribute("disabled");
}

// Separate raise/release thresholds prevent flicker around a single boundary.
let browRaisedState = false;
let browBelowSince = null;

// Stabilize eyebrow detection
function updateBrowState(value, baseline) {
  const raiseThreshold = baseline * 1.018;
  const releaseThreshold = baseline * 1.008;
  if (!browRaisedState) {
    if (value > raiseThreshold) browRaisedState = true;
    browBelowSince = null;
  } else if (value < releaseThreshold) {
    if (browBelowSince === null) browBelowSince = millis();
    if (millis() - browBelowSince >= 220) {
      browRaisedState = false;
      browBelowSince = null;
    }
  } else {
    browBelowSince = null;
  }
  return browRaisedState;
}

// Handle Serial connection errors
// A stalled USB write must not freeze all subsequent expression commands.
async function serialDeadline(operation, ms, label) {
  let timer;
  try {
    return await Promise.race([
      operation,
      new Promise((resolve, reject) => {
        timer = setTimeout(() => reject(new Error(label)), ms);
      })
    ]);
  } finally { clearTimeout(timer); }
}
async function writeSerialWithTimeout(writer, bytes) {
  try {
    await serialDeadline(writer.write(bytes), 1500, "USB write timed out. Unplug/replug USB, then Connect Arduino.");
  } catch (error) {
    // Do not wait indefinitely for the stalled stream to abort.
    writer.abort(error).catch(() => {});
    throw error;
  }
}
async function closeSerialWithTimeout(port) {
  await serialDeadline(port.close(), 700, "USB close timed out; unplug/replug USB before reconnecting.");
}
