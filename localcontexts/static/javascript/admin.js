// Wrap text function if label is too long
const wrapText = function(ctx, text, x, y, maxWidth, lineHeight) {
    let words = text.split(' ');
    let line = '';
    let testLine = ''; // This will store the text when we add a word, to test if it's too long
    let lineArray = [];
    let metrics = ctx.measureText(text);
    let testWidth = metrics.width

    if (testWidth > maxWidth) {
        for(var n = 0; n < words.length; n++) {
            // Create a test line, and measure it..
            testLine += `${words[n]}`;
    
            if (testWidth > maxWidth && n > 0) {
                lineArray.push([line, x, y]);
                y += lineHeight;
                line = `${words[n]}`;
                testLine = `${words[n]}`;
            }
            else {
                line += `${words[n]}`;
            }
            if(n === words.length - 1) {
                lineArray.push([line, x, y]);
            }
        }
    }
    else{
        lineArray.push([text, x, y]);
    }

    return lineArray;
}

// pieLabelsLine plugin, add outside labels to pie chart
const pieLabelsLine = {
    id: "pieLabelsLine",
    afterDraw(chart) {
      const {
        ctx,
        chartArea: { width, height },
      } = chart;

      const cx = chart._metasets[0].data[0].x;
      const cy = chart._metasets[0].data[0].y;

      const sum = chart.data.datasets[0].data.reduce((a, b) => a + b, 0);

      chart.data.datasets.forEach((dataset, i) => {
        chart.getDatasetMeta(i).data.forEach((datapoint, index) => {
          const { x: a, y: b } = datapoint.tooltipPosition();

          const x = 2 * a - cx;
          const y = 2 * b - cy;

          // set line variables
          const halfwidth = width / 2;
          const halfheight = height / 2;
          const xLine = x >= halfwidth ? x + 20 : x - 20;
          const yLine = y >= halfheight ? y + 20 : y - 20;

          const extraLine = x >= halfwidth ? 10 : -10;
          
          // set text variables
          const textWidth = ctx.measureText(chart.data.labels[index]).width;
          ctx.font = "bold 12px Arial";
          const value = chart.data.datasets[0].data[index];

          // Check if the value is above the threshold to display the label
          const threshold = 1; // Adjust the threshold value as needed
          if (value > threshold) {
            // draw line
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.fill();
            ctx.moveTo(x, y);
            ctx.lineTo(xLine, yLine);
            ctx.lineTo(xLine + extraLine, yLine);
            ctx.strokeStyle = dataset.backgroundColor[index];
            ctx.stroke();

            // control the position
            const textXPosition = x >= halfwidth ? "left" : "right";
            const plusFivePx = x >= halfwidth ? 5 : -5;
            ctx.textAlign = textXPosition;
            ctx.textBaseline = "middle";
            ctx.fillStyle = dataset.backgroundColor[index];

            ctx.fillText(chart.data.labels[index] + "", xLine + extraLine + plusFivePx, yLine)
            ctx.font = "12px Arial";
            ctx.fillText(value, xLine + extraLine + plusFivePx, yLine+13);
          }
        });
      });
    },
  };

function pieChart(pieDiv, dataInfo) {
  console.log(pieDiv, dataInfo)
    const ctx = document.getElementById(pieDiv);

    Chart.defaults.font.size = 14;

    new Chart(ctx, {
        type: 'pie',
        data: dataInfo,
        // plugins: [pieLabelsLine],
        options: {
            maintainAspectRatio: false,
            layout: {
                padding: {
                    top:30,
                    bottom:40,
                    left:30,
                    right:30
                }
            },
            scales: {
                y: {
                  display: false,
                  beginAtZero: true,
                  ticks: {
                    display: false,
                  },
                  grid: {
                    display: false,
                  },
                },
                x: {
                  display: false,
                  ticks: {
                    display: false,
                  },
                  grid: {
                    display: false,
                  },
                },
              },
            plugins: {
                title: {
                    display: false,
                },
                legend: {
                    display: false
                },
                tooltip:{
                    displayColors: false
                }
            }
        }
    });
}

function barChart(chartDiv, dataInfo){
    const ctx = document.getElementById(chartDiv);

    Chart.defaults.font.size = 14;

    new Chart(ctx, {
      type: 'line',
      data: dataInfo,
      options:{
        aspectRatio: 2,
        maintainAspectRatio: false,
        plugins: {
          title: {
              display: false,
          },
          legend: {
              display: false
          },
          tooltip:{
              displayColors: false
          }
        },
        scales: {
          x: {
            beginAtZero: true
          }
        }
      }
    });
}