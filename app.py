import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "golf-tracker-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/game', methods=['GET', 'POST'])
@app.route('/game/<game_code>', methods=['GET', 'POST'])
def game(game_code=None):
    from models import Game, Player, PlayerGame, Score

    # If editing existing game, load it
    existing_game = None
    if game_code:
        existing_game = Game.query.filter_by(game_code=game_code).first_or_404()

    if request.method == 'POST':
        player_names = request.form.getlist('player_names[]')
        if not player_names:
            flash('Please add at least one player', 'danger')
            return redirect(url_for('game'))

        # Create new game or use existing
        if existing_game:
            game = existing_game
            # Clear existing scores to update them
            for player_game in game.players:
                Score.query.filter_by(player_game_id=player_game.id).delete()
            PlayerGame.query.filter_by(game_id=game.id).delete()
        else:
            game = Game(
                game_code=Game.generate_unique_code(),
                date=datetime.now()
            )
            db.session.add(game)
            db.session.flush()

        # Process each player's scores
        for idx, player_name in enumerate(player_names):
            if not player_name.strip():
                continue

            # Get or create player
            player = Player.query.filter_by(name=player_name.strip()).first()
            if not player:
                player = Player(name=player_name.strip())
                db.session.add(player)
                db.session.flush()

            # Create player game record
            player_game = PlayerGame(player_id=player.id, game_id=game.id)
            db.session.add(player_game)
            db.session.flush()

            # Add scores for each hole
            for hole in range(1, 19):
                score = request.form.get(f'scores_{idx}_{hole}')
                if score:
                    score_entry = Score(
                        player_game_id=player_game.id,
                        hole_number=hole,
                        strokes=int(score)
                    )
                    db.session.add(score_entry)

        db.session.commit()
        flash(f'Game saved successfully! Game Code: {game.game_code}', 'success')
        return redirect(url_for('game', game_code=game.game_code))

    return render_template('game.html', game=existing_game)

@app.route('/history')
@app.route('/history/<game_code>')
def history(game_code=None):
    from models import Game
    if game_code:
        games = Game.query.filter_by(game_code=game_code).all()
        if not games:
            flash('Game not found', 'danger')
            return redirect(url_for('find_game'))
    else:
        games = Game.query.order_by(Game.date.desc()).all()

    return render_template('history.html', games=games)

@app.route('/stats')
def stats():
    from models import Player, PlayerGame, Score
    players = Player.query.all()

    player_stats = {}
    hole_averages = {}

    for player in players:
        games_played = len(player.games)
        if games_played > 0:
            avg_score = player.average_score
            best_score = min((game.total_score for game in player.games), default=0)

            # Calculate average strokes per hole
            hole_scores = {i: [] for i in range(1, 19)}
            for game in player.games:
                for score in game.scores:
                    hole_scores[score.hole_number].append(score.strokes)

            hole_averages[player.name] = [
                round(sum(hole_scores[hole])/len(hole_scores[hole]), 1)
                if hole_scores[hole] else 0
                for hole in range(1, 19)
            ]

            player_stats[player.name] = {
                'games_played': games_played,
                'avg_score': round(avg_score, 1),
                'best_score': best_score
            }

    return render_template('stats.html', 
                         player_stats=player_stats, 
                         hole_averages=hole_averages,
                         players=list(hole_averages.keys()))

@app.route('/find-game', methods=['GET', 'POST'])
def find_game():
    from models import Game
    if request.method == 'POST':
        game_code = request.form.get('game_code')
        if game_code:
            game = Game.query.filter_by(game_code=game_code).first()
            if game:
                return redirect(url_for('game', game_code=game.game_code))
            flash('Game not found', 'danger')
    return render_template('find_game.html')

with app.app_context():
    import models
    db.create_all()