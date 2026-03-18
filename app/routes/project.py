# These routes are an example of how to use data, forms and routes to create
# a blog where a blogs and comments on those blogs can be
# Created, Read, Updated or Deleted (CRUD)

from app import app, db
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Project, Milestone, ProjPost, User
from app.classes.forms import ProjectForm, MilestoneForm, ProjPostForm, SearchDatesForm
from flask_login import login_required
import datetime as dt
from sqlalchemy.orm.exc import NoResultFound


@app.route('/project/post/new/<pid>/<mid>', methods=['GET','POST'])
@login_required
def projectPostNew(pid=None,mid=None):
    form = ProjPostForm()


    project = Project.query.get(pid)
    if not project:
        flash('That project does not exist.')
        return redirect(url_for('projectMy'))
    
    milestones = project.milestones
    form.milestone.choices = [(m.oid, m.name) for m in milestones]

    fail = 0

    if form.validate_on_submit():
        now = dt.datetime.now(dt.timezone.utc)
        nowdate = now.replace(hour=0, minute=0)
        # if form.post_type.data != "Discussion":
        #     posts = ProjPost.query.filter_by(project_id=project.id, post_type=form.post_type.data).filter(ProjPost.createDateTime < nowdate).all()
        #     if len(posts) > 1:
        #         flash(f'You have more than one post for this day, this project and {form.post_type.data}. This should not happen. Please delete one')
        #     elif len(posts) == 1:
        #         flash(f"You already have a post for this day, this project and {form.post_type.data}. Delete or edit that post.")
        #         return redirect(url_for('projectMy'))
            

        # if form.post_type.data.lower() == "reflection":
        #     post = ProjPost.query.filter_by(project_id=project.id, post_type='intention').filter(ProjPost.createDateTime < nowdate).first()
        #     if not post:
        #         flash("You can't post a reflection if you haven't posted today's intention.")
        #         return redirect(url_for('projectMy'))

        if form.post_type.data.lower() == "intention":
            if int(form.confidence.data) == 0:
                form.confidence.errors.append("Confidence is required if your post type is Intention.")
                fail=1
            if len(form.intention.data) == 0:
                form.intention.errors.append("Intention is required if your post type is Intention.")
                fail=1
        elif form.post_type.data.lower() == "reflection":
            if int(form.satisfaction.data) == 0:
                form.satisfaction.errors.append("Satisfaction is required if your post type is Reflection.")
                fail=1
            if len(form.reflection.data) == 0:
                form.reflection.errors.append("Reflection is required if your post type is Reflection.")
                fail=1
        elif form.post_type.data.lower() == "discussion":
            if len(form.discussion.data) == 0:
                form.discussion.errors.append("This field is required.")
                fail=1
        if fail == 1:
            return render_template("projects/project_post_form.html", form=form, project=project)

        newPost = ProjPost(
            post_type = form.post_type.data,
            confidence = form.confidence.data,
            intention = form.intention.data,
            discussion = form.discussion.data,
            satisfaction = form.satisfaction.data,
            reflection = form.reflection.data,
            author_id = current_user.id,
            project_id = pid,
            milestone_id = mid
        )
        db.session.add(newPost)
        db.session.commit()
        return redirect(url_for("project", pid=pid))
    return render_template("projects/project_post_form.html", form=form, project=project)


@app.route('/project/post/delete/<postID>')
@login_required
def projectPostDelete(postID):
    delPost = ProjPost.query.get(postID)
    if not delPost:
        flash("That post doesn't exist.")
        return redirect(url_for('projectMy'))

    if current_user.id != delPost.author_id:
        flash("You can't delete a post you didn't write.")
        return redirect(url_for('projectMy'))


    db.session.delete(delPost)
    db.session.commit()

    flash("Post deleted")
    return redirect(url_for('project',pid=delPost.project_id))

@app.route('/project/definition')
def projectDef():
    return render_template('projects/project_def.html')

@app.route('/project/list')
@login_required
def projectList():
    projects = Project.query.all()
    for proj in projects:
        posts = ProjPost.query.all()
        if proj.milestones:
            for ms in proj.milestones:
                ms.posts = []
                for post in posts:
                    if post.milestone_id == str(ms.oid):
                        ms.posts.append(post)

    return render_template('projects/project_list.html',projects=projects)

@app.route('/project/delete/<pid>')
@login_required
def projectDelete(pid):


    try:
        projDel = Project.query.filter_by(id=pid).one()
    except NoResultFound:
        flash("That project doesn't exist")
        return render_template('index.html')

    if current_user not in projDel.contributors and projDel.owner != current_user:
        flash("You can't delete that project." )
        return redirect(url_for('projectMy'))
    
    if len(projDel.milestones) > 0:
        flash("You can't delete a project that has Milestones.")
        return redirect(url_for('project',pid=projDel.id))

    projDel.delete()
    flash('Project has been deleted')

    return redirect(url_for('projectList'))    

@app.route('/project/my')
@login_required
def projectMy():

    #query = Q(status='In Progress') & (Q(owner=current_user) | Q(contributors__contains = current_user))
    #query = (Q(owner=current_user) | Q(contributors__contains = current_user))

    projects = Project.query.filter(
        (Project.owner_id == current_user.id),
        Project.status == 'In Progress'
    ).all()

    if len(projects)==0:
        flash("You don't have a project that is set to 'In Progress'. You should make one!")
        return render_template('index.html')
    else:
        return render_template('projects/project_list.html',projects=projects)

@app.route('/project/new', methods=['GET', 'POST'])
@login_required
def projectNew():
    form = ProjectForm()

    if form.validate_on_submit():

        newProj = Project(
            owner_id = current_user.id,
            name = form.name.data,
            course = form.course.data,
            description = form.product.data,
            status = "In Progress",
            createDateTime = dt.datetime.now(dt.timezone.utc),
            product = form.product.data,
            learning_materials = form.learning_materials.data
        )
        db.session.add(newProj)
        db.session.commit()
        return redirect(url_for('project',pid=newProj.id))
    
    return render_template('projects/project_form.html', form=form)

@app.route('/project/edit/<pid>', methods=['GET', 'POST'])
@login_required
def projectEdit(pid):
    form = ProjectForm()
    try:
        projEdit = Project.query.filter_by(id=pid).one()
    except NoResultFound:
        flash('That project does not exist')
        return render_template('index.html')

    if current_user != projEdit.owner:
        flash("You can only edit the project if you own it")
        return redirect(url_for('project',pid=pid))

    if form.validate_on_submit():

        projEdit.update(
            course = form.course.data,
            name = form.name.data,
            status = form.status.data,
            product = form.product.data,
            learning_materials = form.learning_materials.data,
            createDateTime = dt.datetime.utcnow(),
            open_to_contributors = form.open_to_contributors.data
        )

        return redirect(url_for('project',pid=pid))
    
    form.name.data = projEdit.name
    form.course.data = projEdit.course
    form.status.data = projEdit.status
    form.product.process_data(projEdit.product)
    form.learning_materials.process_data(projEdit.learning_materials)
    form.open_to_contributors.data = projEdit.open_to_contributors
    
    return render_template('projects/project_form.html', form=form)


@app.route('/project/<pid>', methods=['POST','GET'])
@login_required
def project(pid):

    form = MilestoneForm()

    try:
        proj = Project.query.filter_by(id=pid).one()
    except NoResultFound:
        flash("That project doesn't exist")
        return redirect(url_for('project', pid=pid))
    
    if form.validate_on_submit():
        if len(proj.milestones) == 0:
            num = 1
        else:
            num = proj.milestones[-1].number + 1
        new_milestone = Milestone(
            name=form.name.data,
            description=form.description.data,
            status="In Progress",
            project_id=proj.id,
            owner_id = current_user.id
        )
        db.session.add(new_milestone)
        db.session.commit()

    return render_template('projects/project.html', proj=proj, form=form)

@app.route('/project/milestone/delete/<pid>/<mid>')
@login_required
def projectMsDel(pid,mid):

    try:
        proj = Project.query.filter_by(id=pid).one()
    except NoResultFound:
        flash("That project doesn't exist")
        return redirect(url_for('project', pid=pid))

    milestone = Milestone.query.filter_by(oid=mid, project_id=proj.id).first()
    if not milestone:
        flash("That milestone doesn't exist.")
        return redirect(url_for('project', pid=pid))

    if milestone.owner_id == current_user.id:
        # Check if this is the last milestone and its status is 'Delete'
        last_milestone = Milestone.query.filter_by(project_id=proj.id).order_by(Milestone.oid.desc()).first()
        if last_milestone and last_milestone.status == 'Delete' and last_milestone.id == milestone.id:
            db.session.delete(milestone)
            db.session.commit()
        else:
            flash('You can only delete a milestone that has status marked as "Delete" and that you own.')
    else:
        flash("You can't delete that milestone because you don't own.")
    
    return redirect(url_for('project',pid=pid))

@app.route('/project/milestone/edit/<pid>/<mid>', methods=['GET','POST'])
@login_required
def projectMsEdit(pid,mid):

    try:
        proj = Project.query.filter_by(id=pid).one()
    except NoResultFound:
        flash("That project doesn't exist")
        return redirect(url_for('project', pid=pid))

    ms = Milestone.query.filter_by(oid=mid, project_id=proj.id).first()
    if not ms:
        flash("That milestone doesn't exist.")
        return redirect(url_for('project', pid=pid))

    if ms.owner_id != current_user.id:
        flash("You have to own the milestone to edit it.")
        return redirect(url_for('project', pid=pid))

    form = MilestoneForm()

    if form.validate_on_submit():
        ms.title = form.name.data
        ms.description = form.description.data
        ms.status = form.status.data
        db.session.commit()
        return redirect(url_for('project', pid=pid))
    
    form.name.process_data(ms.name)
    form.description.process_data(ms.description)
    form.status.process_data(ms.status)

    return render_template('projects/project.html',proj=proj,form=form,edit=True)



