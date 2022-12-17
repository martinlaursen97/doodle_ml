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

async function predict() {
    let imgData = context.getImageData(0, 0, 400, 400);

    let input = []

    for (let i = 3; i < imgData.data.length; i += 4) {
        input.push(imgData.data[i])
    }

    let data = {
        'data': input
    }

    const fetchOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: input
    };

    const res = fetch("http://127.0.0.1:5000/predict", fetchOptions).then(function (response) {
        return response.text();
    }).then(function (text) {
        obj = JSON.parse(text)
        pred = obj.predictions

        var xValues = [];
        var yValues = [];
        var barColors = [];

        for (const key in pred) {
            if (pred.hasOwnProperty(key)) {
                xValues.push(key)
                yValues.push(pred[key])


                barColors.push("black");
            }
        }

        new Chart("myChart", {
            type: "bar",
            data: {
                labels: xValues,
                datasets: [{
                    backgroundColor: barColors,
                    data: yValues
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            max: 1,
                            min: 0.0
                        }
                    }]
                },
                legend: {
                    display: false,
                    labels: {

                        font: {
                            size: 14

                        }
                    }
                },
                title: {
                    display: true,
                    text: "Predictions"
                }
            }
        });
    });
}

function clear() {
    location.reload();
}