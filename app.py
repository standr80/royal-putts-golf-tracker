import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
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
def game():
    from models import Game, Player, PlayerGame, Score
    if request.method == 'POST':
        player_names = request.form.getlist('player_names[]')
        if not player_names:
            flash('Please add at least one player', 'danger')
            return redirect(url_for('game'))

        # Create new game
        new_game = Game(date=datetime.now())
        db.session.add(new_game)
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
            player_game = PlayerGame(player_id=player.id, game_id=new_game.id)
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
        flash('Game saved successfully!', 'success')
        return redirect(url_for('history'))

    return render_template('game.html')

@app.route('/history')
def history():
    from models import Game
    games = Game.query.order_by(Game.date.desc()).all()
    return render_template('history.html', games=games)

@app.route('/stats')
def stats():
    from models import Player, PlayerGame, Score
    players = Player.query.all()

    player_stats = {}
    for player in players:
        games_played = len(player.games)
        if games_played > 0:
            avg_score = player.average_score
            best_score = min((game.total_score for game in player.games), default=0)

            player_stats[player.name] = {
                'games_played': games_played,
                'avg_score': round(avg_score, 1),
                'best_score': best_score
            }

    return render_template('stats.html', player_stats=player_stats)

with app.app_context():
    import models
    db.create_all()