from app import db, mail
from datetime import datetime
import random
from email_validator import validate_email, EmailNotValidError
from flask_login import UserMixin
from flask_mail import Message

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logic = db.Column(db.Text, nullable=False)
    display = db.Column(db.String(1), nullable=False, default='Y')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def calculate_birdies(game):
        """Calculate birdies for all players in a game"""
        player_birdies = {}
        print(f"Calculating birdies for game {game.game_code}")  # Debug log

        for player_game in game.players:
            birdies = []
            print(f"Checking scores for player: {player_game.player.name}")  # Debug log

            for score in player_game.scores:
                # Get the hole for this score
                hole = next((h for h in game.course.holes if str(h.name) == str(score.hole_number)), None)
                print(f"Hole {score.hole_number}: Score={score.strokes}, ", end="")  # Debug log

                if hole:
                    print(f"Par={hole.par}")  # Debug log
                    if score.strokes == hole.par - 1:  # Birdie is one under par
                        print(f"BIRDIE found for {player_game.player.name} on hole {score.hole_number}")  # Debug log
                        birdies.append(score.hole_number)
                else:
                    print("No matching hole found")  # Debug log

            if birdies:
                player_birdies[player_game.player.name] = birdies

        print(f"Final birdie count: {player_birdies}")  # Debug log
        return player_birdies

    @staticmethod
    def format_birdie_details(player_birdies):
        """Format birdie details for display"""
        if not player_birdies:
            return None, None

        # Find players with the most birdies
        max_birdies = max(len(birdies) for birdies in player_birdies.values())
        top_players = [name for name, birdies in player_birdies.items() 
                      if len(birdies) == max_birdies]

        # Format player names
        player_text = " and ".join(top_players)

        # Format details for each top player
        details = []
        for player in top_players:
            holes = player_birdies[player]
            details.append(f"{player}: {len(holes)} birdies (Holes: {', '.join(map(str, sorted(holes)))})")

        return player_text, " | ".join(details)

class User(UserMixin, db.Model):
    __tablename__ = 'admin'  # Map to existing admin table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

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
    image_url = db.Column(db.String(255), nullable=True)  # Store path to uploaded image
    notes = db.Column(db.Text, nullable=True)  # Store hole notes/description
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

class ModuleSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enable_food_drink = db.Column(db.Boolean, default=False)
    auto_disable_games = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_settings():
        """Get the module settings, creating if needed"""
        settings = ModuleSettings.query.first()
        if not settings:
            settings = ModuleSettings()
            db.session.add(settings)
            db.session.commit()
        return settings

    @property
    def should_disable_new_games(self):
        """Check if new games should be disabled based on settings and remaining games"""
        if not self.auto_disable_games:
            return False

        # Get latest purchase details
        purchase_details = PurchaseDetails.get_latest()
        if not purchase_details:
            return False

        return purchase_details.games_remaining < 1

class LocalisationString(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False)
    english_text = db.Column(db.Text, nullable=False)
    french_text = db.Column(db.Text)
    german_text = db.Column(db.Text)
    spanish_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<LocalisationString {self.code}>'

class StoreSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(10), nullable=False, default='en')  # en, fr, de, es
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_settings():
        """Get the store settings, creating if needed"""
        settings = StoreSettings.query.first()
        if not settings:
            settings = StoreSettings()
            db.session.add(settings)
            db.session.commit()
        return settings