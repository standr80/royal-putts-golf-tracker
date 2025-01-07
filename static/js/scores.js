document.addEventListener('DOMContentLoaded', function() {
    let currentHole = 1;
    const totalHoles = 18;

    // Initialize feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }

    // Copy game code to clipboard
    document.getElementById('copy-game-code')?.addEventListener('click', function() {
        const gameCode = this.getAttribute('data-game-code');
        navigator.clipboard.writeText(gameCode).then(() => {
            const originalText = this.innerHTML;
            this.innerHTML = '<i data-feather="check"></i> Copied!';
            feather.replace();

            setTimeout(() => {
                this.innerHTML = originalText;
                feather.replace();
            }, 2000);
        });
    });

    // Function to update cumulative scores
    function updateCumulativeScores() {
        const playerRows = document.querySelectorAll(`#players-for-hole-${currentHole} tr`);
        playerRows.forEach((row, playerIndex) => {
            let total = 0;
            for (let hole = 1; hole <= currentHole; hole++) {
                const scoreInput = document.querySelector(`input[name="scores_${playerIndex}_${hole}"]`);
                if (scoreInput && scoreInput.value) {
                    total += parseInt(scoreInput.value);
                }
            }
            row.querySelector('.cumulative-score').textContent = total;
        });
    }

    // Function to sync player names across all holes
    function syncPlayerNames(playerIndex, newName) {
        for (let hole = 1; hole <= totalHoles; hole++) {
            const playerNameInput = document.querySelector(`#players-for-hole-${hole} tr:nth-child(${playerIndex + 1}) input[name="player_names[]"]`);
            if (playerNameInput) {
                playerNameInput.value = newName;
            }
        }
    }

    // Add event listener for player name changes
    document.addEventListener('input', function(e) {
        if (e.target.name === 'player_names[]') {
            const playerRow = e.target.closest('tr');
            const playerIndex = Array.from(playerRow.parentNode.children).indexOf(playerRow);
            syncPlayerNames(playerIndex, e.target.value);
        } else if (e.target.classList.contains('score-input')) {
            const value = e.target.value;
            if (value && (isNaN(value) || value < 1 || value > 20)) {
                e.target.classList.add('is-invalid');
            } else {
                e.target.classList.remove('is-invalid');
                updateCumulativeScores();
            }
        }
    });

    // Add new player
    document.getElementById('add-player')?.addEventListener('click', function() {
        const playerCount = document.querySelectorAll(`#players-for-hole-1 tr`).length;

        // Add player row to each hole's table
        for (let hole = 1; hole <= totalHoles; hole++) {
            const tbody = document.getElementById(`players-for-hole-${hole}`);
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="cumulative-score">0</td>
                <td>
                    <input type="text" 
                           class="form-control" 
                           name="player_names[]" 
                           required>
                </td>
                <td>
                    <input type="number" 
                           class="form-control score-input" 
                           name="scores_${playerCount}_${hole}"
                           min="1" 
                           max="20">
                </td>
            `;
            tbody.appendChild(tr);
        }
    });

    // Navigate between holes
    document.getElementById('next-hole')?.addEventListener('click', function() {
        if (currentHole < totalHoles) {
            document.getElementById(`hole-${currentHole}`).style.display = 'none';
            currentHole++;
            document.getElementById(`hole-${currentHole}`).style.display = 'block';
            document.getElementById('current-hole').textContent = `Hole ${currentHole}`;

            // Show/hide navigation buttons
            document.getElementById('prev-hole').style.display = 'block';
            if (currentHole === totalHoles) {
                this.style.display = 'none';
                document.getElementById('save-game').style.display = 'block';
            }

            updateCumulativeScores();
        }
    });

    document.getElementById('prev-hole')?.addEventListener('click', function() {
        if (currentHole > 1) {
            document.getElementById(`hole-${currentHole}`).style.display = 'none';
            currentHole--;
            document.getElementById(`hole-${currentHole}`).style.display = 'block';
            document.getElementById('current-hole').textContent = `Hole ${currentHole}`;

            // Show/hide navigation buttons
            document.getElementById('next-hole').style.display = 'block';
            document.getElementById('save-game').style.display = 'none';
            if (currentHole === 1) {
                this.style.display = 'none';
            }

            updateCumulativeScores();
        }
    });

    // Input validation for scores (merged with player name listener)

});