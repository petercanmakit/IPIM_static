// Define a plugin to provide data labels
Chart.plugins.register({
    afterDatasetsDraw: function(chart, easing) {
        // To only draw at the end of animation, check for easing === 1
        var ctx = chart.ctx;
        chart.data.datasets.forEach(function (dataset, i) {
            var meta = chart.getDatasetMeta(i);
            if (!meta.hidden) {
                meta.data.forEach(function(element, index) {
                    // Draw the text in rgb(162, 162, 162), with the specified font
                    ctx.fillStyle = 'rgb(162, 162, 162)';
                    var fontSize = 16;
                    var fontStyle = 'normal';
                    var fontFamily = 'Helvetica Neue';
                    ctx.font = Chart.helpers.fontString(fontSize, fontStyle, fontFamily);
                    // Just naively convert to string for now
                    var dataString = dataset.data[index].toString();
                    // Make sure alignment settings are correct
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    var padding = 5;
                    var position = element.tooltipPosition();
                    ctx.fillText(dataString, position.x, position.y - (fontSize / 2) - padding);
                });
            }
        });
    }
});
// default fontSize and color
Chart.defaults.global.defaultFontColor = 'rgb(162, 162, 162)';
Chart.defaults.global.defaultFontSize = 14;


function getMaxOfArray(numArray) {
  return Math.max.apply(null, numArray);
};

/*
 * @dataArray: int[]
 * @label: String, label name
 * @labelArray: String[], of which length is same as dataArray's
 * @barColor: String, string represents bar color like 'rgb(24, 179, 126)'
 * @canvasId: canvasId of bar chart
 */
var drawBarChart = function(dataArray, label, labelArray, barColor, canvasId) {
    var ctx = document.getElementById(canvasId);
    var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labelArray,
        datasets: [{
            label: label,
            data: dataArray,
            backgroundColor: barColor
        }]
    },
    options: {
        scales: {
            yAxes: [{
                afterTickToLabelConversion: function(scaleInstance) {
                    // set the first and last tick to null so it does not display
                    // note, ticks[0] is the last tick and ticks[length - 1] is the first
                    scaleInstance.ticks[0] = null;
                    // scaleInstance.ticks[scaleInstance.ticks.length - 1] = null;

                    // need to do the same thing for this similiar array which is used internally
                    scaleInstance.ticksAsNumbers[0] = null;
                    // scaleInstance.ticksAsNumbers[scaleInstance.ticksAsNumbers.length - 1] = null;
                },
                id: 'y-axis-1',
                ticks: {
                    beginAtZero:true,
                    max: getMaxOfArray(dataArray) * 1.1,

                },
                gridLines: {
                    color: 'rgba(255,255,255,.05)'
                }
            }]
        },
        legend: {
            display: false
        }
    }
});

};
