import os
import logging
import locale
from flask import render_template, request, redirect, url_for, flash, abort, g, jsonify
from models import (
    Game, Player, PlayerGame, Score, Course, Hole, 
    ModuleSettings, PurchaseDetails, LocalisationString, StoreSettings
)
from datetime import datetime

# Configure basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def format_date_by_language(date):
    """Format date according to the store language setting"""
    store_settings = StoreSettings.get_settings()
    lang = store_settings.language

    # Set locale based on language
    try:
        if lang == 'fr':
            locale.setlocale(locale.LC_TIME, 'fr_FR.utf8')  # Full UTF-8 locale name
        elif lang == 'de':
            locale.setlocale(locale.LC_TIME, 'de_DE.utf8')
        elif lang == 'es':
            locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
        else:  # Default to English
            locale.setlocale(locale.LC_TIME, 'en_US.utf8')

        # Format date according to language conventions
        if lang == 'fr':
            # French format: day month year (lowercase month)
            formatted_date = date.strftime('%-d %B %Y').lower()
        elif lang == 'de':
            formatted_date = date.strftime('%-d. %B %Y')
        elif lang == 'es':
            formatted_date = date.strftime('%-d de %B de %Y')
        else:  # English
            formatted_date = date.strftime('%B %-d, %Y')

        logger.debug(f"Language: {lang}, Formatted date: {formatted_date}")
        return formatted_date
    except locale.Error as e:
        logger.error(f"Locale error: {str(e)}")
        # Fallback to simple date format if locale fails
        return date.strftime('%Y-%m-%d')
    finally:
        # Reset locale to system default
        try:
            locale.setlocale(locale.LC_TIME, '')
        except:
            pass

def get_localized_text(code, default=''):
    """Get localized text based on store language setting"""
    store_settings = StoreSettings.get_settings()
    string = LocalisationString.query.filter_by(code=code).first()

    if not string:
        return default

    if store_settings.language == 'fr' and string.french_text:
        return string.french_text
    elif store_settings.language == 'de' and string.german_text:
        return string.german_text
    elif store_settings.language == 'es' and string.spanish_text:
        return string.spanish_text

    return string.english_text or default

def register_routes(app):
    # Register the date formatting filter
    app.jinja_env.filters['format_date'] = format_date_by_language

    @app.route('/')
    def home():
        """Display the home page"""
        title = get_localized_text('HomePageTitleLine1', 'Royal Putts Thetford')
        title_line2 = get_localized_text('HomePageTitleLine2', "Scores 'n' More!")
        lead_text = get_localized_text('HomePageTitleLine3', "Track your scores, compare your results and eat, drink & be merry!")

        # Feature box texts
        left_box_title = get_localized_text('HomePageLeftBoxLine1', 'Track Scores')
        left_box_text = get_localized_text('HomePageLeftBoxLine2', 'Record your scores hole by hole as you play.')

        middle_box_title = get_localized_text('HomePageMiddleBoxLine1', 'View Results')
        middle_box_text = get_localized_text('HomePageMiddleBoxLine2', 'Review your past games and progress over time.')

        right_box_title = get_localized_text('HomePageRightBoxLine1', 'Analyze Stats')
        right_box_text = get_localized_text('HomePageRightBoxLine2', 'Get insights into your performance with detailed statistics.')

        return render_template('home.html', 
                            title=title,
                            title_line2=title_line2,
                            lead_text=lead_text,
                            left_box_title=left_box_title,
                            left_box_text=left_box_text,
                            middle_box_title=middle_box_title,
                            middle_box_text=middle_box_text,
                            right_box_title=right_box_title,
                            right_box_text=right_box_text)

    @app.route('/game', methods=['GET', 'POST'])
    @app.route('/game/<game_code>', methods=['GET', 'POST'])
    def game(game_code=None):
        """Handle game creation and editing"""
        # Get all available courses
        courses = Course.query.order_by(Course.name).all()

        # If editing existing game, load it
        existing_game = None
        if game_code:
            existing_game = Game.query.filter_by(game_code=game_code).first_or_404()

        if request.method == 'POST':
            player_names = request.form.getlist('player_names[]')
            course_id = request.form.get('course_id', type=int)

            if not player_names:
                flash('Please add at least one player', 'danger')
                return redirect(url_for('game'))

            if not course_id:
                flash('Please select a course', 'danger')
                return redirect(url_for('game'))

            # Create new game or use existing
            if existing_game:
                game = existing_game
                game.course_id = course_id
                # Get current player names for comparison
                current_player_names = {pg.player.name: pg for pg in game.players}
                new_player_names = {name.strip() for name in player_names if name.strip()}

                # Process player changes
                from app import db

                # Remove players that are no longer in the game
                for player_name, player_game in current_player_names.items():
                    if player_name not in new_player_names:
                        db.session.delete(player_game)

                # Add new players
                for player_name in new_player_names:
                    if player_name not in current_player_names:
                        player = Player.query.filter_by(name=player_name).first()
                        if not player:
                            player = Player(name=player_name)
                            db.session.add(player)
                            db.session.flush()

                        player_game = PlayerGame(player_id=player.id, game_id=game.id)
                        db.session.add(player_game)

                db.session.commit()
                return redirect(url_for('scoring', game_code=game.game_code))
            else:
                # Create a new game
                game = Game(
                    game_code=Game.generate_unique_code(),
                    date=datetime.now(),
                    course_id=course_id
                )
                from app import db
                db.session.add(game)
                db.session.flush()

                # Process each player
                for player_name in player_names:
                    if not player_name.strip():
                        continue

                    player = Player.query.filter_by(name=player_name.strip()).first()
                    if not player:
                        player = Player(name=player_name.strip())
                        db.session.add(player)
                        db.session.flush()

                    player_game = PlayerGame(player_id=player.id, game_id=game.id)
                    db.session.add(player_game)

                db.session.commit()
                return redirect(url_for('scoring', game_code=game.game_code))

        return render_template('game.html', game=existing_game, courses=courses)

    @app.route('/history')
    @app.route('/history/<game_code>')
    def history(game_code=None):
        """Display game history"""
        if game_code:
            games = [Game.query.filter_by(game_code=game_code).first_or_404()]
        else:
            games = Game.query.order_by(Game.date.desc()).all()

        return render_template('history.html', games=games, game_code=game_code)

    @app.route('/find-game', methods=['GET', 'POST'])
    def find_game():
        """Handle game search"""
        if request.method == 'POST':
            game_code = request.form.get('game_code')
            if game_code:
                game = Game.query.filter_by(game_code=game_code).first()
                if game:
                    return redirect(url_for('game', game_code=game.game_code))
                flash('Game not found', 'danger')
        return render_template('find_game.html')

    @app.route('/admin/store/language', methods=['POST'])
    def update_store_language():
        """Update the store's display language"""
        from app import db
        try:
            settings = StoreSettings.get_settings()
            settings.language = request.form.get('language')
            db.session.commit()
            flash('Store language updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating store language: {str(e)}', 'danger')

        return redirect(url_for('localisations'))

    return app