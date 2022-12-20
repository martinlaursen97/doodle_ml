// Brush colour and size
const colour = "#000000";
const strokeWidth = 10;

// Drawing state
let latestPoint;
let drawing = false;

// Set up our drawing context
const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");

let brush;

// Initial predict
predict()

// Drawing functions
const continueStroke = newPoint => {
  context.beginPath();
  context.moveTo(latestPoint[0], latestPoint[1]);
  context.strokeStyle = colour;
  context.lineWidth = strokeWidth;
  context.lineCap = "round";
  context.lineJoin = "round";
  context.lineTo(newPoint[0], newPoint[1]);
  context.stroke();

  latestPoint = newPoint;

};

// Event helpers

const startStroke = point => {
  drawing = true;
  latestPoint = point;
};

const getTouchPoint = evt => {
  if (!evt.currentTarget) {
    return [0, 0];
  }
  const rect = evt.currentTarget.getBoundingClientRect();
  const touch = evt.targetTouches[0];
  return [touch.clientX - rect.left, touch.clientY - rect.top];
};

const BUTTON = 0b01;
const mouseButtonIsDown = buttons => (BUTTON & buttons) === BUTTON;


// Event handlers

const mouseMove = evt => {
  if (!drawing) {
    return;
  }
  continueStroke([evt.offsetX, evt.offsetY]);
};

const mouseDown = evt => {
  if (drawing) {
    return;
  }
  evt.preventDefault();
  canvas.addEventListener("mousemove", mouseMove, false);
  startStroke([evt.offsetX, evt.offsetY]);
};

const mouseEnter = evt => {
  if (!mouseButtonIsDown(evt.buttons) || drawing) {
    return;
  }
  mouseDown(evt);
};

const endStroke = async evt => {

  if (!drawing) {
    return;
  }
  await predict()
  drawing = false;
  evt.currentTarget.removeEventListener("mousemove", mouseMove, false);
};

const touchStart = evt => {
  if (drawing) {
    return;
  }
  evt.preventDefault();
  startStroke(getTouchPoint(evt));
};

const touchMove = evt => {
  if (!drawing) {
    return;
  }
  continueStroke(getTouchPoint(evt));
};

const touchEnd = evt => {
  drawing = false;
};

// Register event handlers
canvas.addEventListener("touchstart", touchStart, false);
canvas.addEventListener("touchend", touchEnd, false);
canvas.addEventListener("touchcancel", touchEnd, false);
canvas.addEventListener("touchmove", touchMove, false);

canvas.addEventListener("mousedown", mouseDown, false);
canvas.addEventListener("mouseup", endStroke, false);
canvas.addEventListener("mouseout", endStroke, false);
canvas.addEventListener("mouseenter", mouseEnter, false);

const ctx = document.getElementById("myChart").getContext("2d");

const chart = new Chart(ctx, {
  type: "bar",
  data: {
    labels: [],
    datasets: [
      {
        backgroundColor: [],
        data: [],
      },
    ],
  },
  options: {
    scales: {
      yAxes: [
        {
          ticks: {
            max: 1,
            min: 0.0,
          },
        },
      ],
    },
    legend: {
      display: false,
      labels: {
        font: {
          size: 14,
        },
      },
    },
    title: {
      display: true,
      text: "Predictions",
    },
  },
});

async function predict() {
  const imgData = context.getImageData(0, 0, 400, 400);

  const input = [];

  for (let i = 3; i < imgData.data.length; i += 4) {
    input.push(imgData.data[i]);
  }

  const fetchOptions = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: input,
  };

  const res = await fetch("http://127.0.0.1:5000/predict", fetchOptions);
  const text = await res.text();
  const obj = JSON.parse(text);
  const pred = obj.predictions;

  const xValues = [];
  const yValues = [];
  const barColors = [];

  Object.keys(pred).forEach((key) => {
    result = pred[key]
    xValues.push(key);
    yValues.push(result);

    RGB = Math.max(0, 255 - result * 3 * 255);

    barColors.push(`rgb(${RGB}, ${RGB}, ${RGB})`)
  });

  chart.data.labels = xValues;
  chart.data.datasets[0].data = yValues;
  chart.data.datasets[0].backgroundColor = barColors
  chart.update();
}

function clear() {
  context.clearRect(0, 0, canvas.width, canvas.height);
}
