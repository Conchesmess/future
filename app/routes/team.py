# These routes are an example of how to use data, forms and routes to create
# a blog where a blogs and comments on those blogs can be
# Created, Read, Updated or Deleted (CRUD)

from app import app, db, confirm_delete 
from flask import render_template, flash, redirect, url_for
from markupsafe import Markup
from flask_login import current_user
from app.classes.data import Team, User, Match, team_challenge
from app.classes.forms import TeamForm, TeamChallengeForm, TeamMatchForm
from flask_login import login_required
#import datetime as dt
from sqlalchemy import or_, and_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from google import genai

@app.route('/team/new', methods=['GET', 'POST'])
@login_required
def teamNew():

    if current_user.team:
        flash(f"You are already a member of the team named {current_user.team.name}.","error")
        return redirect(url_for("profile"))
    
    form = TeamForm()

    if form.validate_on_submit():
        otherUser = db.one_or_404(db.select(User).filter_by(id=form.other_player.data))
        if current_user == otherUser:
            flash("The other member of the team cannot be you!","error")
            return redirect(url_for('teamNew'))
        if otherUser.team:
            flash(f"{otherUser.fname} {otherUser.lname} is already a member of the team named {otherUser.team.name}","error")
            return redirect(url_for('teamNew'))
       
        newTeam = Team(
            name=form.name.data,
            points = 0
        )
        db.session.add(newTeam)
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            if "UNIQUE constraint failed" in str(e.orig):
                flash(f"The team name {form.name.data} has been taken","error")
            else:
                flash(f"Database error {str(e)}","error")
            return redirect(url_for('teamNew'))
        else:
            current_user.team = newTeam
            otherUser.team = newTeam
            db.session.commit()

        return redirect(url_for("team", tid=newTeam.id))
    
    users = User.query.all()
    fullnames = [(user.id,f"{user.fname} {user.lname}") for user in users]
    fullnames.remove((current_user.id,f"{current_user.fname} {current_user.lname}"))
    form.other_player.choices = fullnames
    return render_template("teams/team_new.html", form=form)

@app.route('/team/edit/<id>', methods=['GET', 'POST'])
@login_required
def team_edit(id):
    editTeam = db.one_or_404(db.select(Team).filter_by(id=id))
    if current_user not in editTeam.members:
        flash("You can only edit a team that you are in.")
        return redirect(url_for('team',tid=id))
    
    form = TeamForm()

    if form.validate_on_submit():
        editTeam.name=form.name.data
        db.session.commit()
        return redirect(url_for('team',tid=id))
    
    form.name.data = editTeam.name

    return render_template('teams/team_edit.html',form=form, team=editTeam)
    
@app.route('/team/<tid>')
@login_required
def team(tid):
    team = db.one_or_404(db.select(Team).filter_by(id=tid))
    return render_template("teams/team.html",team=team)

@app.route('/team/delete/<id>')
@login_required
@confirm_delete(Team, redirect_url='/profile', message_fields=['name'])
def team_delete(id):
    deleteTeam = db.one_or_404(db.select(Team).filter_by(id=id))
    if current_user in deleteTeam.members:
        if len(deleteTeam.matches)>0:
            flash("you can't delete a team once you have started to play matches.")
        else:
            db.session.delete(deleteTeam)
            db.session.commit()
    else:
        flash("You can only delete the team if you are a member.")
    return render_template('profile')

@app.route('/team/list')
@login_required
def teams():
    teams = Team.query.order_by(Team.points.desc()).all()
    return render_template('teams/teams.html',teams=teams)

@app.route('/team/challenge/new', methods=['GET', 'POST'])
@login_required
def teach_challenge_new():
    try:
        challenger = db.one_or_404(db.select(Team).filter_by(id=current_user.team.id))
    except:
        flash("You are not currently part of a team.")
        return redirect(url_for('profile'))

    form = TeamChallengeForm()

    teams = Team.query.order_by(Team.points).all()
    teamChoices = [(team.id,team.name) for team in teams]
    teamChoices.remove((current_user.team.id,current_user.team.name))
    form.challenged.choices=teamChoices

    if form.validate_on_submit():
        challenger = db.one_or_404(db.select(Team).filter_by(id=current_user.team.id))
        challenged = db.one_or_404(db.select(Team).filter_by(id=form.challenged.data))
        challenger.challenges.append(challenged)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("You already have a challenge with that team.","error")

        return redirect(url_for('team',tid=current_user.team.id))
    return render_template('teams/team_challenge_new.html',form=form)

@app.route('/team/challenge/delete/<challenged_id>')
@login_required
def team_challenge_delete(challenged_id):
    challenged = db.one_or_404(db.select(Team).filter_by(id=challenged_id))
    if challenged not in current_user.team.challenges:
        flash("Can find that challenge in your team's challenges.")
        return redirect(url_for('team',tid=current_user.team.id))
    current_user.team.challenges.remove(challenged)
    db.session.commit()
    flash('Challenge deleted.')
    return redirect(url_for('team',tid=current_user.team.id))

@app.route('/team/match/new', methods=['GET', 'POST'])
@login_required
def team_match_new():
    form = TeamMatchForm()
    teams = Team.query.order_by(Team.points).all()
    teamChoices = [(team.id,team.name) for team in teams]
    form.winner_id.choices=teamChoices
    form.loser_id.choices=teamChoices
    if form.validate_on_submit():
        if form.winner_id.data == form.loser_id.data:
            flash("You have the same team as the winner and the loser.","error")
            return redirect(url_for('team_match_new'))
        winner = db.one_or_404(db.select(Team).filter_by(id=form.winner_id.data))
        loser = db.one_or_404(db.select(Team).filter_by(id=form.loser_id.data))

        if not winner.points:
            winner.points=0
        if not loser.points:
            loser.points=0

        if (winner.points > loser.points):
            winner.points += 2
            loser.points += 1
        elif loser.points > winner.points:
            winner.points += 3
            loser.points += 1
        else:
            winner.points += 2
            loser.points += 1
        
        db.session.add(winner)
        db.session.add(loser)

        newMatch = Match(
            winner_id=form.winner_id.data,
            loser_id=form.loser_id.data,
            score_winner=form.score_winner.data,
            score_loser=form.score_loser.data,
            teams=[winner,loser]
        )
        db.session.add(newMatch)

        db.session.execute(
            team_challenge.delete().where(
                or_(
                    and_(
                        team_challenge.c.challenger_id == winner.id,
                        team_challenge.c.challenged_id == loser.id
                    ),
                    and_(
                        team_challenge.c.challenger_id == loser.id,
                        team_challenge.c.challenged_id == winner.id
                    )
                )
            )
        )
        db.session.commit()
        return redirect(url_for('team',tid=current_user.team.id))
    return render_template('teams/team_match_new.html',form=form)



