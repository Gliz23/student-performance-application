document.addEventListener('DOMContentLoaded', function() {
    // Get the canvas element
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;
    
    // Get data from data attributes
    const chartData = JSON.parse(ctx.getAttribute('data-chart'));
    
    // Only create chart if we have data
    if (chartData.labels.length > 0) {
        const performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [
                    {
                        label: 'Predicted Scores (%)',
                        data: chartData.scores,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Hours Studied',
                        data: chartData.hours,
                        borderColor: 'rgb(255, 159, 64)',
                        backgroundColor: 'rgba(255, 159, 64, 0.2)',
                        tension: 0.1,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Predicted Score (%)'
                        },
                        suggestedMin: 0,
                        suggestedMax: 100
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Hours Studied'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                        suggestedMin: 0
                    }
                }
            }
        });
    } else {
        // Show a message if no data is available
        ctx.parentElement.innerHTML = '<p class="no-chart-data">No historical data available for chart</p>';
    }
});