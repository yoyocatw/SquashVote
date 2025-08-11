document.addEventListener("DOMContentLoaded", function () {
    let myChart;

    // Helper function to get the current theme colors
    function getThemeColors() {
        const style = getComputedStyle(document.documentElement);
        return {
            textColor: style.getPropertyValue('--color-base-content').trim(),
            gridColor: style.getPropertyValue('--color-base-300').trim()
        };
    }

    function fetchChartData() {
        const chartElement = document.getElementById("chart");
        if (!chartElement) return;

        const videoId = chartElement.getAttribute("video-id");
        if (!videoId) return;

        fetch(`/chart/${videoId}/`)
            .then(response => response.json())
            .then(data => {
                if (myChart) {
                    myChart.destroy();
                }

                const colors = getThemeColors();
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
                                    color: colors.textColor,
                                    stepSize: 5,
                                    callback: function(value) {
                                        return Number.isInteger(value) ? value : '';
                                    }
                                }
                            },
                            x: {
                                beginAtZero: true,
                                ticks: {
                                    font: { size: 16 },
                                    color: colors.textColor
                                },
                                grid: {
                                    color: colors.gridColor,
                                    lineWidth: 1,
                                    offset: true
                                }
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

    // Re-fetch chart data after a vote
    async function handleVote(event) {
        event.preventDefault();
        const data = new FormData(this);
        const response = await fetch(this.action, {
            method: "POST",
            body: data,
        });
        if (response.ok) {
            const chartContainer = document.getElementById("chart-container");
            const commentSection = document.getElementById("comment-section");
            if (commentSection) {
                commentSection.classList.remove("hidden");
            }
            if (chartContainer) {
                chartContainer.classList.remove("hidden");
            }
            fetchChartData();
        }
    }

    const voteForm = document.getElementById("vote-form");
    if (voteForm) {
        voteForm.addEventListener("submit", handleVote);
    }

 // to check when the theme changes
    const themeObserver = new MutationObserver((mutationsList, observer) => {
        for (const mutation of mutationsList) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
                if (myChart) {
                    const newColors = getThemeColors();
                    myChart.options.scales.x.ticks.color = newColors.textColor;
                    myChart.options.scales.y.ticks.color = newColors.textColor;
                    myChart.options.scales.x.grid.color = newColors.gridColor;
                    myChart.update();
                }
            }
        }
    });

    themeObserver.observe(document.documentElement, { attributes: true });
});