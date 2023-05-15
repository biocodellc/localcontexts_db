function pieChart(pieDiv, pieTitle, dataInfo) {
    const ctx = document.getElementById(pieDiv);

    Chart.defaults.font.size = 14;

    new Chart(ctx, {
        type: 'pie',
        data: dataInfo,
        options: {
            scales: {
                y: [{
                    gridLines: {display:false}
                }]
            },
            plugins: {
                title: {
                    display: true,
                    text: pieTitle,
                    font: {
                        size: 18
                    }
                },
                legend: {
                    display: false
                },
                tooltip:{
                    displayColors: false,
                }
            }
        }
    });
}
