# These routes are an example of how to use data, forms and routes to create
# a blog where a blogs and comments on those blogs can be
# Created, Read, Updated or Deleted (CRUD)

from app import app, db, confirm_delete 
from flask import render_template, flash, redirect, url_for
from markupsafe import Markup
from flask_login import current_user
from app.classes.data import Project, Milestone, ProjPost, User
from app.classes.forms import ProjectForm, MilestoneForm, ProjPostForm, SearchDatesForm
from flask_login import login_required
import datetime as dt
from sqlalchemy.orm.exc import NoResultFound
from google import genai

# def get_gemini_feedback(student_text,post_type):
#     # api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
#     GEMINI_API_KEY = "AIzaSyBwAdlInY_os7APTvjuakeKWJHCcNrYmKg"
#     # headers = {"Content-Type": "application/json"}
#     client = genai.Client(api_key=GEMINI_API_KEY)
#     if post_type == "intention":
#         prompt = f"Evaluate the level of detail in this student intention. The student intention \
#             does not need to be long but it does need to include specific and measurable outcomes \
#             that the student can reflect on in a second post at the end of the day. Here is an \
#             example of a good student intention 'I will watch a youtube video for beginners on \
#             Freecad - https://www.youtube.com/watch?v=jULWgMV9_TM - I hope to be able to make \
#             something simple that I can actually print. The video is an hour long and class is \
#             two hours so I should be able to do it.' Keep the response short and give the \
#             student feedback on a red, yellow, green scale where red is bad and green is good. \
#             The response text should use HTML markup for formatting. The response should \
#             begin with the word 'red', 'yellow', or 'green'.  Please markup these words \
#             with the color they describe and wrapped in h3 tags. : '{student_text}'. \
#             Give feedback for improvement."
#     elif post_type == "reflection":
#         prompt = student_text
#     response = client.models.generate_content(
#         model="gemini-2.5-flash", 
#         contents=prompt
#         )
#     return response.text


@app.route('/project/post/new/<pid>/<mid>', methods=['GET','POST'])
@login_required
def projectPostNew(pid=None,mid=None):
    form = ProjPostForm()

    project = Project.query.get(pid)
    if not project:
        flash('That project does not exist.')
        return redirect(url_for('projectMy'))
    
    milestones = project.milestones
    if len(milestones) > 0:
        form.milestone.choices = [(m.oid, m.name) for m in milestones]
    else:
        flash("You need a milstone before you can make a Reflection, Intention or Discussion")
        return redirect(url_for('project',pid=pid))
    
    i = -1
    # This is the most recently added milestone
    thisMilestone = milestones[-1]

    while True:
        # if there are more than 0 posts on this milestone check to see what is the last post that was not a discussion
        if len(thisMilestone.posts) > 0:
            if thisMilestone.posts[i].post_type.lower()!='discussion':
                post = thisMilestone.posts[i]
                if post.post_type.lower()=='intention':
                    thisIntention = post.intention
                    thisReflection = None
                elif post.post_type.lower()=='reflection':
                    thisReflection = post.reflection
                    thisIntention=None
                break
            else:
                i = i - 1
        else:
            thisIntention=None
            thisReflection=None
            break

    fail = 0

    if thisIntention == None:
        form.post_type.choices = [("Intention","Intention"),("Discussion","Discussion")]
    elif thisReflection == None:
        form.post_type.choices = [("Reflection","Reflection"),("Discussion","Discussion")]

    if form.validate_on_submit():
        now = dt.datetime.now()
        thisMilestone = Milestone.query.get(mid)

        if form.post_type.data != "Discussion":
            # find all post made today that are the same post type as the submitted form
            posts = ProjPost.query.filter_by(project_id=project.id, post_type=form.post_type.data).filter(db.func.date(ProjPost.createDateTime) == now.date()).all()

            if len(posts) > 0:
                flash(f'You already have a {form.post_type} post for today. Either delete one or make a different type of post','danger')
                return redirect(url_for('project',pid=pid))
            # if the last 
            elif (thisIntention and form.post_type.data.lower() == "intention") or (thisReflection and form.post_type.data.lower() == "intention"):
                flash(f"Your last post was a {form.post_type.data.lower()} and so is this new post. Delete or edit the last post or change the type of the new post.",'danger')
                return redirect(url_for('project',pid=pid))
            elif not thisIntention and not thisReflection and form.post_type.data.lower() == "reflection":
                flash("You can't create a reflection until you have an intention.","danger")
                return redirect(url_for('project',pid=pid))

        if form.post_type.data.lower() == "reflection" and thisReflection != None:
            flash("You can't post a reflection until you have posted an intention to reflect on.","danger")
            return redirect(url_for('project',pid=pid))




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
            milestone_id = mid,
        )
        db.session.add(newPost)
        if form.image.data:
            newPost.image = form.image.data.read()
        db.session.commit()
        return redirect(url_for("project", pid=pid))
    if thisIntention is not None:
        thisIntention = Markup(thisIntention)
    if thisReflection is not None:
        thisReflection = Markup(thisReflection)

    return render_template("projects/project_post_form.html", form=form, project=project, thisReflection=thisReflection, thisIntention=thisIntention)


@app.route('/project/post/delete/<postID>')
@login_required
def projectPostDelete(postID):
    delPost = ProjPost.query.get(postID)
    if not delPost:
        flash("That post doesn't exist.")
        return redirect(url_for('projectMy'))

    if current_user.id != delPost.author_id:
        flash("You can't delete a post you didn't write.")
        return redirect(url_for('projectList'))

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

    return render_template('projects/project_list.html',projects=projects)

@app.route('/project/delete/<pid>')
@login_required
#@confirm_delete(Project, redirect_url='/project/my', message_fields=['name'], message_date_field = 'createdate')
def projectDelete(pid):

    try:
        projDel = Project.query.filter_by(id=pid).one()
    except NoResultFound:
        flash("That project doesn't exist")
        return render_template('index.html')

    if projDel.owner != current_user:
        flash("You can't delete that project." )
        return redirect(url_for('projectMy'))
    
    if len(projDel.milestones) > 0:
        flash("You can't delete a project that has Milestones.")
        return redirect(url_for('project',pid=projDel.id))

    db.session.delete(projDel)
    db.session.commit()
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

        projEdit.course = form.course.data
        projEdit.name = form.name.data
        projEdit.status = form.status.data
        projEdit.product = form.product.data
        projEdit.learning_materials = form.learning_materials.data
        projEdit.createDateTime = dt.datetime.now(dt.timezone.utc)
        db.session.commit()
        return redirect(url_for('project',pid=pid))
    
    form.name.data = projEdit.name
    form.course.data = projEdit.course
    form.status.data = projEdit.status
    form.product.process_data(projEdit.product)
    form.learning_materials.process_data(projEdit.learning_materials)
    
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

@app.route('/project/milestone/new/<pid>', methods=['GET','POST'] )
@login_required
def milestoneNew(pid):
    project = Project.query.filter_by(id=pid).one()
    if project.milestones[-1].status.lower() != "completed":
        flash("You can't add a new milestone until you make the last milestone as 'Completed'.","danger")
        return redirect(url_for('project', pid=pid))

    form = MilestoneForm()

    if form.validate_on_submit():
        newMS = Milestone(
            name = form.name.data,
            description = form.description.data,
            status = form.status.data,
            project_id = pid,
            owner_id = current_user.id
            )
        db.session.add(newMS)
        db.session.commit()
        return redirect(url_for('project', pid=pid))

    return render_template('projects/project.html',proj=project,form=form,edit=True)


@app.route('/project/milestone/delete/<pid>/<mid>')
@login_required
def projectMsDel(pid,mid):
    
    try:
        milestone = Milestone.query.filter_by(oid=mid,project_id=pid).one()
    except NoResultFound:
        flash("That Milestone does not exist.")
        return redirect(url_for('project', pid=pid))


    if milestone.owner_id == None or milestone.owner_id == current_user.id:
        # Check if this is the last milestone and its status is 'Delete'
        if milestone.status == 'Delete':
            db.session.delete(milestone)
            db.session.commit()
        else:
            flash('You can only delete a milestone that has status marked as "Delete".')
    else:
        flash("You can't delete that milestone because you don't own it.")
    flash("Milestone Deleted.")
    return redirect(url_for('project', pid=pid))

@app.route('/project/milestone/edit/<pid>/<mid>', methods=['GET','POST'])
@login_required
def projectMsEdit(pid,mid):

    try:
        proj = Project.query.filter_by(id=pid).one()
    except NoResultFound:
        flash("That project doesn't exist")
        return redirect(url_for('project', pid=pid))
    try:
        ms = Milestone.query.filter_by(oid=mid, project_id=proj.id).one()
    except NoResultFound:
        flash("That milestone doesn't exist.")
        return redirect(url_for('project', pid=pid))

    if ms.owner_id != None and ms.owner_id != current_user.id:
        flash(f"{ms.owner_id} and {current_user.id}")
        flash("You have to own the milestone to edit it.")
        return redirect(url_for('project', pid=pid))

    form = MilestoneForm()

    if form.validate_on_submit():
        ms.name = form.name.data
        ms.description = form.description.data
        ms.status = form.status.data
        ms.owner_id = current_user.id
        db.session.commit()
        return redirect(url_for('project', pid=pid))
    
    form.name.process_data(ms.name)
    form.description.process_data(ms.description)
    form.status.process_data(ms.status)

    return render_template('projects/project.html',proj=proj,form=form,edit=True)



