import os
import requests
from flask import redirect, render_template, abort, send_from_directory, Response, request, jsonify, flash
from flask_login import login_required, current_user
from app import app, db
from app.classes.data import GameResult, User, GameResult


# ── Generic pygbag game hosting ──────────────────────────────────────────────

_CDN_BASE = 'https://pygame-web.github.io/archives/0.9/'
_CDN_PROXY = '/pygbag-cdn/'
_REWRITE_TYPES = {'application/javascript', 'text/javascript', 'text/html', 'text/css'}

# Simple in-memory cache for CDN responses.
# Survives for the lifetime of the container instance — avoids re-fetching
# large files (WASM ~12MB, .data ~7.5MB) on every request.
_cdn_cache = {}  # filename -> (content_type, body_bytes)


@app.route('/games/<game_name>')
@login_required
def pygbag_game_noslash(game_name):
    """Always redirect to the trailing-slash URL so relative assets resolve correctly."""
    return redirect(f'/games/{game_name}/', code=301)


@app.route('/games/<game_name>/')
@login_required
def pygbag_game_landing(game_name):
    """Landing page for a game — opens the game in a popup window."""
    if not all(c.isalnum() or c in '-_' for c in game_name):
        abort(404)
    game_dir = os.path.join(app.static_folder, 'games', game_name)
    if not os.path.isdir(game_dir):
        abort(404)

    display_name = game_name.replace('-', ' ').replace('_', ' ').title()

    # Games that need an opponent selected before launching
    opponent_games = {'connect4', 'mankala'}
    users = []
    if game_name in opponent_games:
        users = User.query.order_by(User.fname, User.lname).all()
        users = [u for u in users if u.id != current_user.id]

    return render_template('game_launch.html', game_name=game_name,
                           display_name=display_name, users=users)


@app.route('/games/<game_name>/play/')
@app.route('/games/<game_name>/play/<path:filename>')
@login_required
def pygbag_game_play(game_name, filename='index.html'):
    """Serve a pygbag game from static/games/<game_name>/.
    Automatically rewrites CDN URLs in index.html so no manual editing is needed.
    """
    if not all(c.isalnum() or c in '-_' for c in game_name):
        abort(404)

    game_dir = os.path.join(app.static_folder, 'games', game_name)
    if not os.path.isdir(game_dir):
        abort(404)

    if filename == 'index.html':
        filepath = os.path.join(game_dir, 'index.html')
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        # Rewrite CDN URLs so all resources go through our proxy.
        # Also collapse any double-slashes (e.g. archives/0.9//browserfs.min.js)
        # that exist in some pygbag-generated index.html files.
        content = content.replace(_CDN_BASE, _CDN_PROXY)
        content = content.replace(_CDN_PROXY + '/', _CDN_PROXY)
        return Response(content, content_type='text/html; charset=utf-8')

    return send_from_directory(game_dir, filename)


@app.route('/pygbag-cdn/<path:filename>')
@login_required
def pygbag_cdn_proxy(filename):
    """Proxy pygame-web CDN resources and add Cross-Origin-Resource-Policy header
    so they satisfy COEP: require-corp. All sub-resource CDN URLs are rewritten
    to keep routing through this proxy. Responses are cached in memory for the
    lifetime of the container to avoid re-fetching large WASM/data files."""
    if filename in _cdn_cache:
        content_type, body = _cdn_cache[filename]
        headers = {
            'Cross-Origin-Resource-Policy': 'cross-origin',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'public, max-age=86400',
        }
        return Response(body, status=200, headers=headers, content_type=content_type)

    # Restricted to the pygbag CDN only — no arbitrary SSRF
    cdn_url = _CDN_BASE + filename
    upstream = requests.get(cdn_url, timeout=60)

    skip = {'transfer-encoding', 'connection', 'content-encoding', 'keep-alive',
            'content-length'}
    headers = {k: v for k, v in upstream.headers.items() if k.lower() not in skip}
    headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Cache-Control'] = 'public, max-age=86400'

    content_type = upstream.headers.get('Content-Type', '')
    base_type = content_type.split(';')[0].strip()

    if base_type in _REWRITE_TYPES:
        body = upstream.text.replace(_CDN_BASE, _CDN_PROXY)
        body = body.replace(_CDN_PROXY + '/', _CDN_PROXY)
        body_bytes = body.encode('utf-8')
    else:
        body_bytes = upstream.content

    _cdn_cache[filename] = (content_type, body_bytes)
    return Response(body_bytes, status=upstream.status_code, headers=headers,
                    content_type=content_type)


# ── Game result API ───────────────────────────────────────────────────────────

VALID_GAMES = {'connect4', 'minesweeper', 'mankala', 'asteroids'}

@app.route('/api/users')
@login_required
def api_users():
    """Return a list of all users (id, name) for opponent selection."""
    users = User.query.order_by(User.lname, User.fname).all()
    return jsonify([
        {'id': u.id, 'name': f"{u.fname} {u.lname}", 'email': u.email_ousd}
        for u in users
        if u.id != current_user.id
    ])


@app.route('/api/games/result', methods=['POST'])
@login_required
def save_game_result():
    """Receive a game result from a pygbag game and save it to the database."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    game = data.get('game', '').strip().lower()
    if game not in VALID_GAMES:
        return jsonify({'error': 'Unknown game'}), 400

    winner = data.get('winner', '').strip()[:50] if data.get('winner') else None
    score = data.get('score')
    if score is not None:
        try:
            score = int(score)
        except (ValueError, TypeError):
            score = None

    opponent_id = data.get('opponent_id')
    if opponent_id is not None:
        try:
            opponent_id = int(opponent_id)
            if not User.query.get(opponent_id):
                opponent_id = None
        except (ValueError, TypeError):
            opponent_id = None

    result = GameResult(
        game=game,
        winner=winner,
        score=score,
        user_id=current_user.id,
        opponent_id=opponent_id,
    )
    db.session.add(result)
    db.session.commit()
    return jsonify({'status': 'ok', 'id': result.id}), 201

@app.route('/gameresults')
def gameresults():
    results = GameResult.query.order_by(GameResult.game, GameResult.score.desc(), GameResult.played_at).all()
    return render_template('game_results.html',results=results)