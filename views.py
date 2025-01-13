import os
from flask import render_template, request, redirect, url_for, flash, abort, g, jsonify
from models import Game, Player, PlayerGame, Score, Course, Hole, ModuleSettings, PurchaseDetails, LocalisationString, StoreSettings
from datetime import datetime

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
    @app.route('/')
    def home():
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

    @app.route('/scoring/<game_code>', methods=['GET', 'POST'])
    def scoring(game_code):
        game = Game.query.filter_by(game_code=game_code).first_or_404()

        # Get the number of holes from the course
        max_holes = len(game.course.holes)
        if max_holes == 0:
            flash('This course has no holes configured. Please set up holes first.', 'danger')
            return redirect(url_for('game', game_code=game_code))

        try:
            current_hole = int(request.args.get('hole', '1'))
            if current_hole < 1 or current_hole > max_holes:
                current_hole = 1
        except ValueError:
            current_hole = 1

        # Get current hole information
        current_hole_info = None
        sorted_holes = sorted(game.course.holes, key=lambda x: x.name)
        if 0 <= current_hole - 1 < len(sorted_holes):
            current_hole_info = sorted_holes[current_hole - 1]

        # Create dictionaries for current hole scores and cumulative scores
        current_hole_scores = {}
        cumulative_scores = {}

        for player_game in game.players:
            # Get current hole score
            score = Score.query.filter_by(
                player_game_id=player_game.id,
                hole_number=current_hole
            ).first()
            if score:
                current_hole_scores[player_game.id] = score.strokes

            # Calculate cumulative score for each player
            total_score = 0
            for s in player_game.scores:
                if s.strokes is not None:  # Only add valid scores
                    total_score += s.strokes
            cumulative_scores[player_game.id] = total_score

        if request.method == 'POST':
            try:
                from app import db
                # Process scores for the current hole
                for player_game in game.players:
                    score_key = f'scores_{player_game.id}'
                    try:
                        score_value = request.form.get(score_key, '').strip()
                        if score_value:
                            score_value = int(score_value)
                            if score_value < 1 or score_value > 20:
                                flash('Strokes must be between 1 and 20', 'danger')
                                return redirect(url_for('scoring', game_code=game_code, hole=current_hole))
                        else:
                            continue  # Skip empty scores
                    except ValueError:
                        flash('Invalid score value', 'danger')
                        return redirect(url_for('scoring', game_code=game_code, hole=current_hole))

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

                if current_hole < max_holes:
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
                            current_hole_info=current_hole_info,
                            max_holes=max_holes,
                            current_hole_scores=current_hole_scores,
                            cumulative_scores=cumulative_scores)

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

    @app.route('/admin/course-setup', methods=['GET', 'POST'])
    def course_setup():
        """Admin page for golf course setup and configuration"""
        if request.method == 'POST':
            course_name = request.form.get('course_name', '').strip()
            if course_name:
                from app import db
                try:
                    course = Course(name=course_name)
                    db.session.add(course)
                    db.session.commit()
                    flash(f'Course "{course_name}" has been created successfully.', 'success')
                    return redirect(url_for('course_setup'))
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error creating course: {str(e)}', 'danger')
                    return redirect(url_for('course_setup'))

        courses = Course.query.order_by(Course.name).all()
        return render_template('admin/course_setup.html', courses=courses)

    @app.route('/admin/course/<int:course_id>/settings', methods=['GET', 'POST'])
    def course_settings(course_id):
        """Settings page for a specific course"""
        course = Course.query.get_or_404(course_id)

        if request.method == 'POST':
            course_name = request.form.get('course_name', '').strip()
            if course_name:
                from app import db
                try:
                    course.name = course_name
                    db.session.commit()
                    flash(f'Course name updated successfully to "{course_name}".', 'success')
                    return redirect(url_for('course_settings', course_id=course.id))
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error updating course name: {str(e)}', 'danger')
                    return redirect(url_for('course_settings', course_id=course.id))

        return render_template('admin/course_settings.html', course=course)

    @app.route('/admin/course/<int:course_id>/hole/add', methods=['POST'])
    def add_hole(course_id):
        """Add a new hole to a course"""
        course = Course.query.get_or_404(course_id)
        hole_name = request.form.get('hole_name', '').strip()
        hole_par = request.form.get('hole_par', type=int)

        if hole_name and hole_par:
            from app import db
            try:
                hole = Hole(name=hole_name, par=hole_par, course_id=course.id)
                db.session.add(hole)
                db.session.commit()
                flash(f'Hole "{hole_name}" has been added successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding hole: {str(e)}', 'danger')
        else:
            flash('Please provide a hole name and par value.', 'danger')

        return redirect(url_for('course_settings', course_id=course_id))

    @app.route('/admin/course/<int:course_id>/hole/<int:hole_id>/update', methods=['POST'])
    def update_hole(course_id, hole_id):
        """Update a hole's details"""
        hole = Hole.query.filter_by(id=hole_id, course_id=course_id).first_or_404()

        hole_name = request.form.get('hole_name', '').strip()
        hole_par = request.form.get('hole_par', type=int)

        from app import db
        try:
            if hole_name:
                hole.name = hole_name
            if hole_par is not None:
                hole.par = hole_par
            db.session.commit()
            flash(f'Hole updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating hole: {str(e)}', 'danger')

        return redirect(url_for('course_settings', course_id=course_id))

    @app.route('/admin/course/<int:course_id>/hole/<int:hole_id>/delete', methods=['POST'])
    def delete_hole(course_id, hole_id):
        """Delete a hole"""
        hole = Hole.query.filter_by(id=hole_id, course_id=course_id).first_or_404()
        from app import db
        try:
            db.session.delete(hole)
            db.session.commit()
            flash(f'Hole "{hole.name}" has been deleted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting hole: {str(e)}', 'danger')

        return redirect(url_for('course_settings', course_id=course_id))

    @app.route('/admin')
    def admin():
        """Admin dashboard to view all games with pagination and search"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort', 'date')  # Default sort by date
        order = request.args.get('order', 'desc')  # Default order is descending

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

        # Apply sorting
        if sort_by == 'game_code':
            query = query.order_by(Game.game_code.desc() if order == 'desc' else Game.game_code.asc())
        else:  # Default to date sorting
            query = query.order_by(Game.date.desc() if order == 'desc' else Game.date.asc())

        # Paginate results
        pagination = query.paginate(
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
                             search_term=search_term,
                             sort_by=sort_by,
                             order=order)

    @app.route('/admin/course/<int:course_id>/delete', methods=['POST'])
    def delete_course(course_id):
        """Delete a course"""
        course = Course.query.get_or_404(course_id)
        from app import db
        try:
            db.session.delete(course)
            db.session.commit()
            flash(f'Course "{course.name}" has been deleted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting course: {str(e)}', 'danger')

        return redirect(url_for('course_setup'))

    @app.route('/player-comparison')
    @app.route('/player-comparison/<game_code>')
    def player_comparison(game_code=None):
        """Compare performance metrics between selected players"""
        # Get players based on game code or all players
        if game_code:
            game = Game.query.filter_by(game_code=game_code).first_or_404()
            all_players = [pg.player for pg in game.players]
        else:
            all_players = Player.query.order_by(Player.name).all()

        # Get selected player IDs from query parameters
        selected_player_ids = request.args.getlist('player_ids', type=int)
        selected_players = [p for p in all_players if p.id in selected_player_ids]

        stats = {}
        hole_averages = {}
        max_holes = 0

        if selected_players:
            for player in selected_players:
                # Calculate basic stats
                if game_code:
                    player_games = [pg for pg in player.games if pg.game.game_code == game_code]
                else:
                    player_games = player.games

                games_played = len(player_games)
                if games_played > 0:
                    total_scores = [game.total_score for game in player_games]
                    avg_score = sum(total_scores) / len(total_scores)
                    best_score = min(total_scores)

                    # Calculate hole-by-hole averages
                    hole_scores = {}
                    for pg in player_games:
                        for score in pg.scores:
                            if score.hole_number not in hole_scores:
                                hole_scores[score.hole_number] = []
                            hole_scores[score.hole_number].append(score.strokes)
                            max_holes = max(max_holes, score.hole_number)

                    # Calculate average for each hole
                    hole_avgs = []
                    for hole in range(1, max_holes + 1):
                        scores = hole_scores.get(hole, [])
                        avg = sum(scores) / len(scores) if scores else 0
                        hole_avgs.append(round(avg, 1))

                    stats[player.id] = {
                        'games_played': games_played,
                        'avg_score': avg_score,
                        'best_score': best_score
                    }
                    hole_averages[player.id] = hole_avgs

        return render_template('player_comparison.html',
                             all_players=all_players,
                             selected_players=selected_players,
                             selected_player_ids=selected_player_ids,
                             stats=stats,
                             hole_averages=hole_averages,
                             max_holes=max_holes,
                             game_code=game_code)
    @app.route('/bar-menu')
    def bar_menu():
        """Display the food and drink menu page"""
        return render_template('bar_menu.html')
    @app.route('/admin/account', methods=['GET', 'POST'])
    def account_management():
        """Display and handle the account management page"""
        from models import PurchaseDetails, ModuleSettings
        from datetime import datetime

        if request.method == 'POST':
            from app import db
            try:
                # Get existing record or create new one
                purchase_details = PurchaseDetails.get_latest() or PurchaseDetails()

                # Update contact information
                purchase_details.contact_name = request.form.get('contact_name')
                purchase_details.contact_email = request.form.get('contact_email')
                purchase_details.contact_phone = request.form.get('contact_phone')

                # Validate email if provided
                if purchase_details.contact_email and not purchase_details.validate_email():
                    flash('Invalid email format', 'danger')
                    return redirect(url_for('account_management'))

                if not purchase_details.id:  # If new record
                    db.session.add(purchase_details)
                db.session.commit()
                flash('Contact details saved successfully', 'success')
                return redirect(url_for('account_management'))

            except Exception as e:
                db.session.rollback()
                flash(f'Error saving contact details: {str(e)}', 'danger')
                return redirect(url_for('account_management'))

        # GET request - display form
        purchase_details = PurchaseDetails.get_latest()
        modules = ModuleSettings.get_settings()
        return render_template('admin/account_management.html', 
                             purchase_details=purchase_details,
                             modules=modules)

    @app.route('/superadmin', methods=['GET', 'POST'])
    def superadmin():
        """Display and handle the super admin dashboard page"""
        from models import PurchaseDetails, ModuleSettings
        from datetime import datetime

        if request.method == 'POST':
            from app import db
            try:
                # Get existing record or create new one
                purchase_details = PurchaseDetails.get_latest() or PurchaseDetails()

                # Update fields
                if request.form.get('games_purchased'):
                    purchase_details.games_purchased = int(request.form.get('games_purchased'))

                if request.form.get('purchase_date'):
                    try:
                        purchase_details.purchase_date = datetime.strptime(
                            request.form.get('purchase_date'), 
                            '%d/%m/%Y'
                        ).date()
                    except ValueError:
                        flash('Invalid date format. Please use DD/MM/YYYY', 'danger')
                        return redirect(url_for('superadmin'))

                purchase_details.invoice_number = request.form.get('invoice_number')
                purchase_details.contact_name = request.form.get('contact_name')
                purchase_details.contact_email = request.form.get('contact_email')
                purchase_details.contact_phone = request.form.get('contact_phone')

                # Validate email if provided
                if purchase_details.contact_email and not purchase_details.validate_email():
                    flash('Invalid email format', 'danger')
                    return redirect(url_for('superadmin'))

                if not purchase_details.id:  # If new record
                    db.session.add(purchase_details)
                db.session.commit()
                flash('Purchase details saved successfully', 'success')
                return redirect(url_for('superadmin'))

            except Exception as e:
                db.session.rollback()
                flash(f'Error saving purchase details: {str(e)}', 'danger')
                return redirect(url_for('superadmin'))

        # GET request - display form
        purchase_details = PurchaseDetails.get_latest()
        modules = ModuleSettings.get_settings()
        return render_template('admin/superadmin.html', 
                             purchase_details=purchase_details,
                             modules=modules)

    @app.route('/admin/update-modules', methods=['POST'])
    def update_modules():
        """Handle module settings updates"""
        from app import db
        from models import ModuleSettings

        try:
            settings = ModuleSettings.get_settings()
            settings.enable_food_drink = bool(request.form.get('enable_food_drink'))
            settings.auto_disable_games = bool(request.form.get('auto_disable_games'))
            db.session.commit()
            flash('Module settings updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating module settings: {str(e)}', 'danger')

        return redirect(url_for('superadmin'))

    @app.route('/admin/localisations')
    def localisations():
        """Display and manage localisation strings"""
        from models import LocalisationString, StoreSettings

        # Get sort parameters
        sort_order = request.args.get('order', 'asc')  # Default to ascending

        # Query with sorting
        if sort_order == 'desc':
            strings = LocalisationString.query.order_by(LocalisationString.code.desc()).all()
        else:
            strings = LocalisationString.query.order_by(LocalisationString.code.asc()).all()

        store_settings = StoreSettings.get_settings()
        return render_template('admin/localisations.html', 
                             strings=strings,
                             store_settings=store_settings,
                             current_sort_order=sort_order)

    @app.route('/admin/localisations/add', methods=['POST'])
    def add_localisation_string():
        """Add a new localisation string"""
        from app import db
        from models import LocalisationString
        try:
            string = LocalisationString(
                code=request.form.get('code'),
                english_text=request.form.get('english_text'),
                french_text=request.form.get('french_text'),
                german_text=request.form.get('german_text'),
                spanish_text=request.form.get('spanish_text')
            )
            db.session.add(string)
            db.session.commit()
            flash('Localisation string added successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding localisation string: {str(e)}', 'danger')

        return redirect(url_for('localisations'))

    @app.route('/admin/localisations/edit', methods=['POST'])
    def edit_localisation_string():
        """Edit an existing localisation string"""
        from app import db
        from models import LocalisationString
        try:
            string = LocalisationString.query.get_or_404(request.form.get('string_id', type=int))
            string.english_text = request.form.get('english_text')
            string.french_text = request.form.get('french_text')
            string.german_text = request.form.get('german_text')
            string.spanish_text = request.form.get('spanish_text')
            db.session.commit()
            flash('Localisation string updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating localisation string: {str(e)}', 'danger')

        return redirect(url_for('localisations'))

    @app.route('/admin/store/language', methods=['POST'])
    def update_store_language():
        """Update the store's display language"""
        from app import db
        from models import StoreSettings
        try:
            settings = StoreSettings.get_settings()
            settings.language = request.form.get('language')
            db.session.commit()
            flash('Store language updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating store language: {str(e)}', 'danger')

        return redirect(url_for('localisations'))

    @app.route('/admin/course/<int:course_id>/hole/<int:hole_id>/upload-image', methods=['POST'])
    def upload_hole_image(course_id, hole_id):
        """Upload an image for a specific hole"""
        hole = Hole.query.filter_by(id=hole_id, course_id=course_id).first_or_404()

        if 'hole_image' not in request.files:
            flash('No image file provided', 'danger')
            return redirect(url_for('course_settings', course_id=course_id))

        file = request.files['hole_image']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('course_settings', course_id=course_id))

        if file:
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join('static', 'hole_images')
            os.makedirs(upload_dir, exist_ok=True)

            # Generate unique filename
            filename = f"hole_{hole_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{os.path.splitext(file.filename)[1]}"
            file_path = os.path.join(upload_dir, filename)

            try:
                file.save(file_path)
                from app import db
                hole.image_url = f"/static/hole_images/{filename}"
                db.session.commit()
                flash('Image uploaded successfully', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error uploading image: {str(e)}', 'danger')

        return redirect(url_for('course_settings', course_id=course_id))

    @app.route('/admin/course/<int:course_id>/hole/<int:hole_id>/update-notes', methods=['POST'])
    def update_hole_notes(course_id, hole_id):
        """Update notes for a specific hole"""
        hole = Hole.query.filter_by(id=hole_id, course_id=course_id).first_or_404()

        notes = request.form.get('hole_notes', '').strip()
        from app import db
        try:
            hole.notes = notes
            db.session.commit()
            flash('Hole notes updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating hole notes: {str(e)}', 'danger')

        return redirect(url_for('course_settings', course_id=course_id))

    @app.route('/scoring/<game_code>/save-score', methods=['POST'])
    def save_score(game_code):
        """Save a single score via AJAX"""
        game = Game.query.filter_by(game_code=game_code).first_or_404()

        try:
            player_game_id = request.form.get('player_game_id', type=int)
            hole_number = request.form.get('hole_number', type=int)
            strokes = request.form.get('strokes', type=int)

            if not all([player_game_id, hole_number, strokes]):
                return jsonify({'error': 'Missing required fields'}), 400

            if not (1 <= strokes <= 20):
                return jsonify({'error': 'Invalid score value'}), 400

            existing_score = Score.query.filter_by(
                player_game_id=player_game_id,
                hole_number=hole_number
            ).first()

            from app import db
            if existing_score:
                existing_score.strokes = strokes
            else:
                score = Score(
                    player_game_id=player_game_id,
                    hole_number=hole_number,
                    strokes=strokes
                )
                db.session.add(score)

            db.session.commit()
            return jsonify({'success': True})

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500