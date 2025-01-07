from flask import Flask, render_template, request, redirect, url_for, flash, abort, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import logging
import os

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

@app.template_filter('ordinal_date')
def ordinal_date(dt):
    """Format date as '3rd January 2025'"""
    day = dt.day
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f"{day}{suffix} {dt.strftime('%B %Y')}"

@app.before_request
def load_game_details():
    """Load game details for the navigation menu if in game context"""
    path_parts = request.path.split('/')
    if len(path_parts) > 2 and path_parts[1] in ['game', 'history', 'stats']:
        game_code = path_parts[2]
        from models import Game
        g.games = [Game.query.filter_by(game_code=game_code).first()]
    else:
        g.games = []

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
            # First delete scores, then player_games due to foreign key constraint
            for player_game in game.players:
                Score.query.filter_by(player_game_id=player_game.id).delete()
            db.session.commit()  # Commit the score deletions first
            PlayerGame.query.filter_by(game_id=game.id).delete()
        else:
            game = Game(
                game_code=Game.generate_unique_code(),
                date=datetime.now()
            )
            db.session.add(game)
            db.session.flush()

        players = []
        # Process each player
        for player_name in player_names:
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
            players.append(player)

        db.session.commit()
        return redirect(url_for('scoring', game_code=game.game_code))

    return render_template('game.html', game=existing_game)

@app.route('/scoring/<game_code>', methods=['GET', 'POST'])
def scoring(game_code):
    from models import Game, Player, PlayerGame, Score

    game = Game.query.filter_by(game_code=game_code).first_or_404()

    if request.method == 'POST':
        # Clear existing scores for this game
        for player_game in game.players:
            Score.query.filter_by(player_game_id=player_game.id).delete()

        # Add new scores
        for idx, player_game in enumerate(game.players):
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
        flash('Game scores saved successfully!', 'success')
        return redirect(url_for('history', game_code=game.game_code))

    players = [pg.player for pg in game.players]
    return render_template('scoring.html', game=game, players=players)

@app.route('/stats')
@app.route('/stats/<game_code>')
def stats(game_code=None):
    from models import Game, Player, PlayerGame, Score

    if game_code:
        # Get specific game
        game = Game.query.filter_by(game_code=game_code).first_or_404()
        players = [pg.player for pg in game.players]
    else:
        players = Player.query.all()

    player_stats = {}
    hole_averages = {}

    for player in players:
        # Filter games for specific game if game_code provided
        if game_code:
            player_games = [pg for pg in player.games if pg.game.game_code == game_code]
        else:
            player_games = player.games

        games_played = len(player_games)
        if games_played > 0:
            total_scores = [game.total_score for game in player_games]
            avg_score = sum(total_scores) / len(total_scores)
            best_score = min(total_scores)

            # Calculate average strokes per hole
            hole_scores = {i: [] for i in range(1, 19)}
            for game in player_games:
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
                         players=list(hole_averages.keys()),
                         game_code=game_code)

@app.route('/history')
@app.route('/history/<game_code>')
def history(game_code=None):
    from models import Game
    if game_code:
        games = [Game.query.filter_by(game_code=game_code).first_or_404()]
    else:
        games = Game.query.order_by(Game.date.desc()).all()

    return render_template('history.html', games=games, game_code=game_code)

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

@app.route('/admin')
def admin():
    """Admin dashboard to view all games"""
    from models import Game
    games = Game.query.order_by(Game.date.desc()).all()
    return render_template('admin.html', games=games)

@app.context_processor
def inject_games():
    """Make games available in all templates"""
    return dict(games=getattr(g, 'games', []))

with app.app_context():
    import models
    db.create_all()