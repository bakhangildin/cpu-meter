var layout = {
  title: "Процент загрузки CPU",
  xaxis: {
    title: "Время",
    type: "date",
  },
  yaxis: {
    title: "Загрузка, %",
  },
};

x = new Array(20).fill(new Date());
y = new Array(20).fill(0);

var trace = {
  x: x,
  y: y,
  mode: "line",
};

var data = [trace];

Plotly.newPlot("plot", data, layout);

let interval_id = null;

const handleIntervalChange = (interval) => {
  window.clearInterval(interval_id);

  interval_id = setInterval(() => {
    fetch("http://localhost:8000/get-cpu-load").then((r) => {
      r.json().then((data) => {
        Plotly.extendTraces(
          "plot",
          {
            x: [[new Date()]],
            y: [[data.cpu_load]],
          },
          [0]
        );
      });
    });
  }, interval);
};

const handelIntervalSelectChange = (event) => {
  const interval = parseInt(event.target.value);
  handleIntervalChange(interval);
};

const intervalSelectElm = document.querySelector("select");
intervalSelectElm.addEventListener("change", handelIntervalSelectChange);
handleIntervalChange(1000);
