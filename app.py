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
    from models import Game, Score
    if request.method == 'POST':
        new_game = Game(date=datetime.now())
        db.session.add(new_game)
        db.session.flush()
        
        for hole in range(1, 19):
            score = request.form.get(f'hole_{hole}')
            if score:
                score_entry = Score(
                    game_id=new_game.id,
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
    from models import Game, Score
    games = Game.query.order_by(Game.date.desc()).all()
    return render_template('history.html', games=games)

@app.route('/stats')
def stats():
    from models import Game, Score
    games = Game.query.all()
    scores = Score.query.all()
    
    total_games = len(games)
    avg_score = sum(score.strokes for score in scores) / len(scores) if scores else 0
    best_score = min((score.strokes for score in scores), default=0) if scores else 0
    
    stats_data = {
        'total_games': total_games,
        'avg_score': round(avg_score, 1),
        'best_score': best_score
    }
    
    return render_template('stats.html', stats=stats_data)

with app.app_context():
    import models
    db.create_all()
