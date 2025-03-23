document.addEventListener("DOMContentLoaded", function () {
    let myChart; 

    function fetchChartData() {
        const chartElement = document.getElementById("chart");
        if (!chartElement) return;

        const videoId = chartElement.getAttribute("video-id");
        if (!videoId) return;

        fetch(`/chart/${videoId}/`)
            .then(response => response.json())
            .then(data => {
               // console.log("Chart Data:", data);

                if (myChart) {
                    myChart.destroy();
                    myChart = null;
                }

                const chartContext = chartElement.getContext("2d");
                myChart = new Chart(chartContext, {
                    type: "bar",
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
                        elements: { bar: { borderSkipped: false } },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { 
                                    font: { size: 16 }, 
                                    color: "#ffffff", 
                                    stepSize: 5,
                                    callback: function(value) {
                                        return Number.isInteger(value) ? value : '';
                                  } 
                                }
                            },
                            x: {
                                beginAtZero: true,
                                ticks: { font: { size: 16 }, color: "#ffffff" },
                                grid: { color: "#4D4D4D", lineWidth: 1, offset: true }
                            }
                        },
                        borderRadius: 5,
                        plugins: { legend: { display: false } }
                    }
                });
            })
            .catch(error => console.error("Error fetching chart data:", error));
    }

    fetchChartData();

    async function handleVote(event) {
        event.preventDefault();
        const data = new FormData(this);
        const response = await fetch(this.action, {
            method: "POST",
            body: data,
        });
        if (response.ok) {
            const chartContainer = document.getElementById("chart-container");
            if (chartContainer) {
                chartContainer.style.display = "block";
                chartContainer.classList.remove("hidden");
            }
            fetchChartData();
        }
    }

    const voteForm = document.getElementById("vote-form");
    if (voteForm) {
        voteForm.addEventListener("submit", handleVote);
    }

});
