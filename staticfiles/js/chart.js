document.addEventListener("DOMContentLoaded", function() {

    const chartElement = document.getElementById('chart');
    const videoId = chartElement.getAttribute('video-id'); 
    fetch(`/chart/${videoId}/`)  
    .then(response => response.json())
    .then(data => {
        // console.log("Chart Data:", data);
        const chart = document.getElementById('chart').getContext('2d');
        new Chart(chart, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: '',
                    data: data.data,
                    backgroundColor: ['#EC6B56', '#FFC154', '#6CA0DC'],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                elements: {
                    bar: {
                      borderWidth: 4,
                    }
                  },
                scales: { 
                    y: 
                    { 
                        beginAtZero: true, 
                        ticks:{
                            stepSize: 1,
                            font:{
                                size: 16,
                            },
                            color: '#ffffff'
                        },
                        grid: {
                            color: '#4D4D4D',
                            lineWidth: 1
                        }
                    },
                    x: 
                    {
                        ticks: {
                            font: {
                                size: 16
                            },
                            color: '#ffffff'
                        },
                        
                    } 
                },
                borderRadius: 5,
                plugins: {
                    legend: {
                            display: false
                    },
                }
            }
        });
    });
});