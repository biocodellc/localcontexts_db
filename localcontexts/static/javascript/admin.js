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

const pieLabelsLine = {
    id: 'pieLabelsLine',
    afterDraw(chart, args, options) {
        const { ctx, chartArea: { top, bottom, left, right, width, height} } = chart;

        const canvasWidth = chart.width - 10

        const cx = chart._metasets[0].data[0].x;
        const cy = chart._metasets[0].data[0].y;

        const sum = chart.data.datasets[0].data.reduce((a, b) => a + b, 0);

        chart.data.datasets.forEach((dataset, i) => {
            chart.getDatasetMeta(i).data.forEach((datapoint, index) => {
                const { x: a, y: b } = datapoint.tooltipPosition();

                const x = 2 * a - cx;
                const y = 2 * b - cy;

                // draw line
                const halfwidth = width/2 + left;
                const halfheight = height/2 + top;

                const xLine = x >= halfwidth ? x + 10 : x - 10;
                const yLine = y >= halfheight ? y + 10 : y - 10;
                const extraLine = x >= halfwidth ? 10 : -10;

                // line
                ctx.beginPath();
                ctx.moveTo(x,y);
                ctx.lineTo(xLine, yLine);
                ctx.lineTo(xLine + extraLine, yLine);
                ctx.strokeStyle = dataset.backgroundColor[index];
                ctx.stroke();

                // text style
                const textWidth = ctx.measureText(chart.data.labels[index]).width;
                ctx.font = 'bolder 12px Arial';

                // control the text position
                const textXPosition = x >= halfwidth ? 'left' : 'right';
                const plusFivePx = x >= halfwidth ? 5 : -5;
                ctx.textAlign = textXPosition;
                ctx.textBaseline = 'middle';

                // add label text, wrapping lines when needed
                var tooltipText = `${chart.data.labels[index]}`;
                var tooltipValue = `\n${dataset.data[index]}`;
                var lineHeight = 15;
                var numOfLines = 0

                ctx.fillStyle = dataset.backgroundColor[index];
                let wrappedText = wrapText(ctx, tooltipText, xLine + extraLine + plusFivePx, yLine, 80, lineHeight);

                wrappedText.forEach(function(item) {
                    ctx.fillText(item[0], item[1], item[2]);
                    numOfLines += 1
                })
                ctx.fillText(tooltipValue, xLine + extraLine + plusFivePx, yLine + (numOfLines*lineHeight))
            })
        })
    }
}

function pieChart(pieDiv, pieTitle, dataInfo) {
    const ctx = document.getElementById(pieDiv);

    Chart.defaults.font.size = 14;

    new Chart(ctx, {
        type: 'pie',
        data: dataInfo,
        plugins: [pieLabelsLine],
        aspectRatio:2,
        options: {
            layout: {
                padding: {
                    left: 80,
                    right: 80,
                    top: 0,
                    bottom: 0
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: pieTitle,
                    font: {
                        size: 18,
                    }
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
