from app import db, mail
from datetime import datetime
import random
from email_validator import validate_email, EmailNotValidError
from flask_mail import Message

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    holes = db.relationship('Hole', backref='course', lazy=True, cascade="all, delete-orphan")
    games = db.relationship('Game', backref='course', lazy=True)

class Hole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    par = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    games = db.relationship('PlayerGame', backref='player', lazy=True, cascade="all, delete-orphan")

    @property
    def average_score(self):
        scores = [game.total_score for game in self.games]
        return sum(scores) / len(scores) if scores else 0

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_code = db.Column(db.String(6), unique=True, nullable=False, index=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    players = db.relationship('PlayerGame', backref='game', lazy=True, cascade="all, delete-orphan")

    @staticmethod
    def generate_unique_code():
        while True:
            code = str(random.randint(100000, 999999))
            if not Game.query.filter_by(game_code=code).first():
                return code

class PlayerGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    scores = db.relationship('Score', backref='player_game', lazy=True, cascade="all, delete-orphan")

    @property
    def total_score(self):
        return sum(score.strokes for score in self.scores)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_game_id = db.Column(db.Integer, db.ForeignKey('player_game.id'), nullable=False)
    hole_number = db.Column(db.Integer, nullable=False)
    strokes = db.Column(db.Integer, nullable=False)

class PurchaseDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    games_purchased = db.Column(db.Integer, nullable=True)
    purchase_date = db.Column(db.Date, nullable=True)
    invoice_number = db.Column(db.String(50), nullable=True)
    contact_name = db.Column(db.String(100), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    notification_sent = db.Column(db.Boolean, default=False)

    @staticmethod
    def get_latest():
        """Get the latest purchase details record"""
        return PurchaseDetails.query.order_by(PurchaseDetails.id.desc()).first()

    def validate_email(self):
        """Validate email format"""
        if self.contact_email:
            try:
                validate_email(self.contact_email)
                return True
            except EmailNotValidError:
                return False
        return True

    @property
    def total_games_used(self):
        """Calculate total number of games used"""
        return Game.query.count()

    @property
    def games_remaining(self):
        """Calculate number of games remaining"""
        games_purchased = self.games_purchased or 0
        remaining = max(0, games_purchased - self.total_games_used)

        # Send notification if games remaining is zero and notification hasn't been sent
        if remaining == 0 and not self.notification_sent and self.contact_name:
            self.send_no_games_notification()
            self.notification_sent = True
            db.session.commit()

        return remaining

    def send_no_games_notification(self):
        """Send email notification when games remaining reaches zero"""
        try:
            subject = f"{self.contact_name} - No Games Left"
            msg = Message(
                subject=subject,
                recipients=['richard@eventstuff.ltd'],
                body=f"""
                Hello,

                This is an automated notification to inform you that the number of games remaining has reached zero.

                Details:
                Contact Name: {self.contact_name}
                Contact Email: {self.contact_email}
                Contact Phone: {self.contact_phone}
                Last Invoice: {self.invoice_number}
                Last Purchase Date: {self.purchase_date}

                Please take necessary action.

                Best regards,
                Golf Score Tracker System
                """
            )
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email notification: {str(e)}")