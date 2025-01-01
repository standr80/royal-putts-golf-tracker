from app import db
from datetime import datetime

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    games = db.relationship('PlayerGame', backref='player', lazy=True)

    @property
    def average_score(self):
        scores = [game.total_score for game in self.games]
        return sum(scores) / len(scores) if scores else 0

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    players = db.relationship('PlayerGame', backref='game', lazy=True)

class PlayerGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    scores = db.relationship('Score', backref='player_game', lazy=True)

    @property
    def total_score(self):
        return sum(score.strokes for score in self.scores)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_game_id = db.Column(db.Integer, db.ForeignKey('player_game.id'), nullable=False)
    hole_number = db.Column(db.Integer, nullable=False)
    strokes = db.Column(db.Integer, nullable=False)