from flask import render_template, request, redirect, url_for, flash, abort, g
from models import Game, Player, PlayerGame, Score
from datetime import datetime

def register_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/game', methods=['GET', 'POST'])
    @app.route('/game/<game_code>', methods=['GET', 'POST'])
    def game(game_code=None):
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
                    date=datetime.now()
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

        return render_template('game.html', game=existing_game)

    @app.route('/scoring/<game_code>', methods=['GET', 'POST'])
    def scoring(game_code):
        game = Game.query.filter_by(game_code=game_code).first_or_404()

        try:
            current_hole = int(request.args.get('hole', '1'))
            if current_hole < 1 or current_hole > 18:
                current_hole = 1
        except ValueError:
            current_hole = 1

        # Create a dictionary of current hole scores
        current_hole_scores = {}
        for player_game in game.players:
            score = Score.query.filter_by(
                player_game_id=player_game.id,
                hole_number=current_hole
            ).first()
            if score:
                current_hole_scores[player_game.id] = score.strokes

        if request.method == 'POST':
            try:
                from app import db
                # Process scores for the current hole
                for player_game in game.players:
                    score_key = f'scores_{player_game.id}'
                    score_value = request.form.get(score_key, '').strip()

                    try:
                        score_value = int(score_value) if score_value else 0
                        if score_value < 0 or score_value > 20:
                            score_value = 0
                    except ValueError:
                        score_value = 0

                    existing_score = Score.query.filter_by(
                        player_game_id=player_game.id,
                        hole_number=current_hole
                    ).first()

                    if existing_score:
                        existing_score.strokes = score_value
                    else:
                        score_entry = Score(
                            player_game_id=player_game.id,
                            hole_number=current_hole,
                            strokes=score_value
                        )
                        db.session.add(score_entry)

                db.session.commit()

                if current_hole < 18:
                    return redirect(url_for('scoring', game_code=game_code, hole=current_hole + 1))
                else:
                    flash('Game scores saved successfully!', 'success')
                    return redirect(url_for('history', game_code=game_code))

            except Exception as e:
                db.session.rollback()
                flash('Error saving scores. Please try again.', 'danger')
                return redirect(url_for('scoring', game_code=game_code, hole=current_hole))

        return render_template('scoring.html', 
                            game=game, 
                            current_hole=current_hole, 
                            current_hole_scores=current_hole_scores)

    @app.route('/stats')
    @app.route('/stats/<game_code>')
    def stats(game_code=None):
        if game_code:
            game = Game.query.filter_by(game_code=game_code).first_or_404()
            players = [pg.player for pg in game.players]
        else:
            players = Player.query.all()

        player_stats = {}
        hole_averages = {}

        for player in players:
            if game_code:
                player_games = [pg for pg in player.games if pg.game.game_code == game_code]
            else:
                player_games = player.games

            games_played = len(player_games)
            if games_played > 0:
                total_scores = [game.total_score for game in player_games]
                avg_score = sum(total_scores) / len(total_scores)
                best_score = min(total_scores)

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
        if game_code:
            games = [Game.query.filter_by(game_code=game_code).first_or_404()]
        else:
            games = Game.query.order_by(Game.date.desc()).all()

        return render_template('history.html', games=games, game_code=game_code)

    @app.route('/find-game', methods=['GET', 'POST'])
    def find_game():
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
        """Admin dashboard to view all games with pagination and search"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Ensure per_page is one of the allowed values
        allowed_per_page = [10, 20, 30, 40, 50]
        if per_page not in allowed_per_page:
            per_page = 10

        # Get base query
        query = Game.query

        # Apply search filters if provided
        search_term = request.args.get('search', '').strip()
        if search_term:
            # Search in game codes and player names
            from app import db
            query = query.join(PlayerGame).join(Player).filter(
                db.or_(
                    Game.game_code.ilike(f'%{search_term}%'),
                    Player.name.ilike(f'%{search_term}%'),
                    # Search for date components (day, month, year)
                    db.func.to_char(Game.date, 'DD').ilike(f'%{search_term}%'),
                    db.func.to_char(Game.date, 'Month').ilike(f'%{search_term}%'),
                    db.func.to_char(Game.date, 'YYYY').ilike(f'%{search_term}%'),
                    # Search for formatted date strings
                    db.func.to_char(Game.date, 'DD Month YYYY').ilike(f'%{search_term}%'),
                    db.func.to_char(Game.date, 'DDth Month YYYY').ilike(f'%{search_term}%')
                )
            ).distinct()

        # Order and paginate results
        pagination = query.order_by(Game.date.desc()).paginate(
            page=page, 
            per_page=per_page,
            error_out=False
        )

        games = pagination.items
        return render_template('admin.html', 
                             games=games,
                             pagination=pagination,
                             per_page=per_page,
                             allowed_per_page=allowed_per_page,
                             search_term=search_term)