document.addEventListener('DOMContentLoaded', function() {
    let playerCount = 1;

    // Copy game code to clipboard
    document.getElementById('copy-game-code')?.addEventListener('click', function() {
        const gameCode = this.getAttribute('data-game-code');
        navigator.clipboard.writeText(gameCode).then(() => {
            // Show success feedback
            const originalText = this.innerHTML;
            this.innerHTML = '<i data-feather="check"></i> Copied!';
            feather.replace();

            // Reset button text after 2 seconds
            setTimeout(() => {
                this.innerHTML = originalText;
                feather.replace();
            }, 2000);
        });
    });

    // Add new player section
    document.getElementById('add-player')?.addEventListener('click', function() {
        const playersContainer = document.getElementById('players-container');
        const playerTemplate = document.querySelector('.player-section').cloneNode(true);

        // Update input names for the new player
        const inputs = playerTemplate.querySelectorAll('input');
        inputs.forEach(input => {
            if (input.name.startsWith('scores_')) {
                input.name = input.name.replace('scores_0', `scores_${playerCount}`);
                input.value = '';
            }
        });

        // Add separator between players
        const separator = document.createElement('hr');
        separator.className = 'my-4';
        playersContainer.appendChild(separator);

        playersContainer.appendChild(playerTemplate);
        playerCount++;

        // Reinitialize Feather icons
        feather.replace();
    });

    // Calculate total for each player
    function calculatePlayerTotal(playerSection) {
        let total = 0;
        const scoreInputs = playerSection.querySelectorAll('.score-input');
        scoreInputs.forEach(input => {
            if (input.value) {
                total += parseInt(input.value);
            }
        });
        return total;
    }

    // Input validation for scores
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('score-input')) {
            const value = e.target.value;
            if (value && (isNaN(value) || value < 1 || value > 20)) {
                e.target.classList.add('is-invalid');
            } else {
                e.target.classList.remove('is-invalid');
            }
        }
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