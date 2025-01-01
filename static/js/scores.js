document.addEventListener('DOMContentLoaded', function() {
    // Input validation for scores
    const scoreInputs = document.querySelectorAll('.score-input');
    scoreInputs.forEach(input => {
        input.addEventListener('input', function() {
            const value = this.value;
            if (value && (isNaN(value) || value < 1 || value > 20)) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    });

    // Calculate running total
    function updateTotal() {
        let total = 0;
        scoreInputs.forEach(input => {
            if (input.value) {
                total += parseInt(input.value);
            }
        });
        document.getElementById('total-score').textContent = total;
    }

    scoreInputs.forEach(input => {
        input.addEventListener('input', updateTotal);
    });

    // Initialize charts if on stats page
    const statsChart = document.getElementById('statsChart');
    if (statsChart) {
        const ctx = statsChart.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Hole 1', 'Hole 2', 'Hole 3', 'Hole 4', 'Hole 5', 'Hole 6', 'Hole 7', 'Hole 8', 'Hole 9',
                        'Hole 10', 'Hole 11', 'Hole 12', 'Hole 13', 'Hole 14', 'Hole 15', 'Hole 16', 'Hole 17', 'Hole 18'],
                datasets: [{
                    label: 'Average Strokes per Hole',
                    data: Array(18).fill(4),
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
});
