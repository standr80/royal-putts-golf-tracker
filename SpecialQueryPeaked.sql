-- SpecialQueryPeaked.sql
-- This query analyzes a specific game to identify players who led for the most holes
-- but ultimately did not win the game.
-- Parameters:
--   game_code: The specific game code to analyze

WITH hole_cumulative_scores AS (
    SELECT 
        p.name as player_name,
        s.hole_number,
        s.strokes,
        SUM(s.strokes) OVER (PARTITION BY pg.id ORDER BY s.hole_number) as cumulative_score
    FROM score s
    JOIN player_game pg ON pg.id = s.player_game_id
    JOIN player p ON p.id = pg.player_id
    JOIN game g ON g.id = pg.game_id
    WHERE g.game_code = :game_code  -- Parameter to be replaced with specific game code
),
hole_rankings AS (
    SELECT 
        player_name,
        hole_number,
        cumulative_score,
        RANK() OVER (PARTITION BY hole_number ORDER BY cumulative_score) as rank
    FROM hole_cumulative_scores
),
leader_counts AS (
    SELECT 
        player_name,
        COUNT(*) as times_leading
    FROM hole_rankings
    WHERE rank = 1
    GROUP BY player_name
),
final_scores AS (
    SELECT 
        player_name,
        cumulative_score as final_score,
        RANK() OVER (ORDER BY cumulative_score) as final_rank
    FROM hole_cumulative_scores
    WHERE hole_number = (
        SELECT MAX(hole_number) 
        FROM hole_cumulative_scores
    )
),
detailed_scores AS (
    SELECT 
        hole_number,
        player_name,
        strokes,
        cumulative_score
    FROM hole_cumulative_scores
    ORDER BY hole_number, cumulative_score
)

-- Main result showing players who led but didn't win
SELECT 
    l.player_name,
    l.times_leading as holes_led,
    f.final_score,
    f.final_rank,
    CASE 
        WHEN f.final_rank > 1 AND l.times_leading > 0 
        THEN 'Led for ' || l.times_leading || ' holes but finished ' || f.final_rank || 'th'
        WHEN f.final_rank = 1 
        THEN 'Winner'
        ELSE 'Never led'
    END as analysis
FROM leader_counts l
JOIN final_scores f ON f.player_name = l.player_name
ORDER BY l.times_leading DESC;

-- Detailed hole-by-hole progression
SELECT 
    hole_number,
    player_name,
    strokes,
    cumulative_score
FROM detailed_scores
ORDER BY hole_number, cumulative_score;
