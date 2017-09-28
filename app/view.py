# -*- coding:utf-8 -*-

from flask import render_template, url_for, redirect, flash, request, abort, session, g, jsonify, Response
from app import app, lm
from sqlalchemy import desc
from app.forms import *
from flask_login import login_user, logout_user, login_required, current_user
from urlparse import urlparse, urljoin
from identifyingcode import drawIdentifyingCode
from PIL import Image
from app.models import *
from datetime import datetime, timedelta
from config import SUCCESS, BAD
import os, base64, math, json, re

# Configs and View for Login

lm.login_view = 'login'
lm.login_message = u'W请先登录!'


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def before_request():
    g.user = current_user


# web views


@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    id = form.id.data
    password = form.password.data
    if form.validate_on_submit():
        u = User.query.filter(User.id == id).first()
        if u is not None:
            if u.testPassword(password):
                login_user(u, form.remember_me.data)
                u.login()
                next = request.args.get('next')
                if u.chpassword == False:
                    return redirect(url_for('info_setpassword'))
                if next is None:
                    return redirect(url_for('index'))
                if not is_safe_url(next):
                    return redirect(url_for('index'))
                return redirect(next or url_for('index'))
            else:
                flash(u'D密码错误!')
        else:
            flash(u'D该学号或工号不存在!')
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/info/setpassword', methods=['GET', 'POST'])
@login_required
def info_setpassword():
    user = current_user
    form = SetPasswordForm()
    if form.validate_on_submit():
        password_old = form.password_old.data
        password_new = form.password_new.data
        identifyingcode = form.identifyingcode.data
        if 'code_text' in session and identifyingcode.upper() == session['code_text']:
            if user.testPassword(password_old):
                user.setPasswordhash(password_new)
                flash(u'S修改成功!')
            else:
                flash(u'D密码错误!')
        else:
            flash(u'D验证码错误!')
    return render_template('info_setpassword.html', form=form)


@app.route('/appointment', methods=['GET'])
@login_required
def appointment():
    if current_user.identify == User.IDENTIFY_MENTOR:
        abort(403)
    return render_template('appointment.html')


@app.route('/appointment/new/<men_id>', methods=['GET', 'POST'])
@login_required
def appointment_new(men_id):
    user = current_user
    if user == User.IDENTIFY_MENTOR:
        abort(403)
    form = AppointmentNewForm()
    if form.validate_on_submit():
        description = form.description.data
        time_date_string = form.time_date_string.data

        men = User.query.filter(User.id == men_id).filter(User.identify == User.IDENTIFY_MENTOR).first()

        match = re.search(r'(\d+)-(\d+)-(\d+)', time_date_string)
        y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
        time_date = date(y, m, d)

        if men_id is not None:
            if time_date >= datetime.now().date():
                appointment = Appointment(user, men, description, time_date)
                appointment.update()
                print 'success!'
                flash(u'S预约成功!')
                return redirect(url_for('appointment_stu'))
            else:
                flash(u'D非法的日期!')
        else:
            flash(u'D该导师不存在!')
    return render_template('appointment_new.html', form=form)


@app.route('/appointment/<aid>/exa', methods=['GET', 'POST'])
@login_required
def appointment_exa(aid):
    user = current_user
    if user.identify == User.IDENTIFY_STUDENT:
        abort(403)
    appointment = Appointment.query.filter(Appointment.id == aid).first()
    if appointment is None:
        abort(404)
    form = AppointmentReplyForm()
    if form.validate_on_submit():
        if appointment.status == Appointment.STATUS_WAITING:
            if appointment.men.id == user.id:
                status = form.status.data
                replytext = form.replytext.data
                appointment.reply(status, replytext, '')
                flash(u'S审批成功!')
            return redirect(url_for('appointment_men'))
    return render_template('appointment_exa.html', appointment=appointment, form=form)


@app.route('/appointment/<aid>/view', methods=['GET', 'POST'])
@login_required
def appointment_view(aid):
    user = current_user
    if user.identify == User.IDENTIFY_MENTOR:
        abort(403)
    appointment = Appointment.query.filter(Appointment.id == aid).first()
    if appointment is None:
        abort(404)
    return render_template('appointment_view.html', appointment=appointment)


@app.route('/appointment/<aid>/delete', methods=['GET'])
@login_required
def appointment_delete(aid):
    user = current_user
    if user.identify == User.IDENTIFY_MENTOR:
        abort(403)
    appointment = Appointment.query.filter(Appointment.id == aid).first()
    if appointment is None:
        abort(404)
    if appointment.stu.id != user.id:
        abort(403)
    appointment.delete()
    flash(u'S删除成功!')
    return redirect(url_for('appointment_stu'))


@app.route('/appointment/men', methods=['GET'])
@login_required
def appointment_men():
    user = current_user
    if user.identify == User.IDENTIFY_STUDENT:
        abort(403)
    return render_template('appointment_men.html')


@app.route('/appointment/stu', methods=['GET'])
@login_required
def appointment_stu():
    user = current_user
    if user.identify == User.IDENTIFY_MENTOR:
        abort(403)
    return render_template('appointment_stu.html')


# view old


@app.route('/course', methods=['GET'])
@login_required
def course():
    if current_user.identify == User.IDENTIFY_MENTOR:
        abort(403)
    courses = Course.query.filter(Course.time_deadline > datetime.now()).order_by(Course.time_start).all()
    return render_template('course.html', courses=courses)


@app.route('/result/stu', methods=['GET'])
@login_required
def result_stu():
    return render_template('result_stu.html')


@app.route('/result/men', methods=['GET'])
@login_required
def result_men():
    user = current_user
    if user.identify == User.IDENTIFY_STUDENT:
        abort(403)
    appointments = Appointment.query.filter(Appointment.men == user).order_by(Appointment.time_submit).all()
    return render_template('result_men.html', appointments=appointments)


@app.route('/course/new', methods=['GET', 'POST'])
@login_required
def course_new():
    form = CourseNewForm()
    if current_user.identify == User.IDENTIFY_MENTOR:
        if form.validate_on_submit():
            men = current_user
            name = form.name.data
            capacity = form.capacity.data
            department = form.department.data
            description = form.description.data
            location = form.location.data
            time_start_string = form.time_start.data
            time_end_string = form.time_end.data
            time_deadline_string = form.time_deadline.data

            match = re.search(r'(\d+)-(\d+)-(\d+) (\d+):(\d+)', time_start_string)
            y, m, d, h, i = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), int(
                match.group(5))
            time_start = datetime(y, m, d, h, i)

            match = re.search(r'(\d+)-(\d+)-(\d+) (\d+):(\d+)', time_end_string)
            y, m, d, h, i = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), int(
                match.group(5))
            time_end = datetime(y, m, d, h, i)

            match = re.search(r'(\d+)-(\d+)-(\d+) (\d+):(\d+)', time_deadline_string)
            y, m, d, h, i = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), int(
                match.group(5))
            time_deadline = datetime(y, m, d, h, i)

            course = Course(name, department, men, capacity, description, location, time_start, time_end, time_deadline)
            course.update()
            flash(u'S创建成功!')
    else:
        abort(403)
    return render_template('course_new.html', form=form)


# ajax routes

@app.route('/ajax/getIdentifyingcode', methods=['POST'])
def getIdentifyingcode():
    code_img, code_text = drawIdentifyingCode()
    session['code_text'] = code_text
    code_uri = '/static/tmp/code/' + getSHA256(code_text)
    return jsonify({'code_uri': code_uri})


@app.route('/ajax/mentor/query', methods=['POST'])
@login_required
def ajax_mentor_query():
    user = current_user
    if user.identify == User.IDENTIFY_MENTOR:
        abort(403)
    form = MentorQueryForm()
    if form.validate_on_submit():
        department = int(form.department.data)
        if department == 0:
            mentors = User.query.filter(User.identify == User.IDENTIFY_MENTOR).all()
        else:
            mentors = user.query.filter(User.identify == User.IDENTIFY_MENTOR).filter(
                User.department == department).all()
        mentors_dict = [mentor.toDict() for mentor in mentors]
        return jsonify({'status': SUCCESS, 'content': mentors_dict})
    else:
        return jsonify({'status': BAD})


@app.route('/ajax/appointment/query/<type>', methods=['POST'])
@login_required
def ajax_appointment_query(type):
    user = current_user
    appointments = []
    identify = user.identify
    type = int(type)
    if type == 0:
        if user.identify == User.IDENTIFY_MENTOR:
            appointments = sorted(user.appointments_men, key=lambda appointment: appointment.time_date, reverse=True)
        elif user.identify == User.IDENTIFY_STUDENT:
            appointments = sorted(user.appointments_stu, key=lambda appointment: appointment.time_date, reverse=True)
    elif type == 1:
        form = AppointmentQueryByStatusForm()
        if form.validate_on_submit():
            status = form.status.data
            if user.identify == User.IDENTIFY_MENTOR:
                appointments = Appointment.query.filter(Appointment.men_id == user.id).filter(
                    Appointment.status == status).order_by(desc(Appointment.time_date)).all()
            elif user.identify == User.IDENTIFY_STUDENT:
                appointments = Appointment.query.filter(Appointment.stu_id == user.id).filter(
                    Appointment.status == status).order_by(desc(Appointment.time_date)).all()
        else:
            return jsonify({'status': BAD})
    elif type == 2:
        form = AppointmentQueryByDepartmentForm()
        if form.validate_on_submit():
            department = form.department.data
            if user.identify == User.IDENTIFY_MENTOR:
                appointments = Appointment.query.filter(Appointment.men_id == user.id).join(
                    User.appointments_men).filter(User.department == department).order_by(
                    desc(Appointment.time_submit)).all()
            elif user.identify == User.IDENTIFY_STUDENT:
                appointments = Appointment.query.filter(Appointment.stu_id == user.id).join(
                    User.appointments_stu).filter(User.department == department).order_by(
                    desc(Appointment.time_submit)).all()
        else:
            return jsonify({'status': BAD})
    elif type == 3:
        form = AppointmentQueryByDateForm()
        if form.validate_on_submit():
            time_date_string = form.time_date_string.data
            match = re.search(r'(\d+)-(\d+)-(\d+)', time_date_string)
            y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
            time_date = date(y, m, d)
            if user.identify == User.IDENTIFY_MENTOR:
                appointments = Appointment.query.filter(Appointment.men_id == user.id).filter(
                    Appointment.time_date == time_date).order_by(desc(Appointment.time_date)).all()
            elif user.identify == User.IDENTIFY_STUDENT:
                appointments = Appointment.query.filter(Appointment.stu_id == user.id).filter(
                    Appointment.time_date == time_date).order_by(desc(Appointment.time_date)).all()
        else:
            return jsonify({'status': BAD})
    appointments_dict = [appointment.toDict() for appointment in appointments]
    return jsonify({'status': SUCCESS, 'content': appointments_dict})


@app.route('/ajax/appointment/<aid>/score', methods=['POST'])
@login_required
def ajax_appointment_score(aid):
    user = current_user
    appointment = Appointment.query.filter(Appointment.id == aid).first()
    if appointment is not None:
        if appointment.stu.id == user.id:
            score = request.form.get('score', 0)
            score = int(score)
            appointment.setScore(score)
            return jsonify({'status': SUCCESS})
        else:
            return jsonify({'status': BAD})
    else:
        return jsonify({'status': BAD})


# ajax old
@app.route('/ajax/appointment/list/<offset>', methods=['GET', 'POST'])
@login_required
def ajax_appointment_list(offset):
    '''
    用来获取预约列表。自动检测身份，学生返回预约列表，门特返回被预约列表。每次10条。
    :param offset:起始条目。
    :return:json：{'status':状态代码（SUCCESS or BAD 详见config.py）,'data':[json列表，包含字典格式的预约信息，信息都是字符串，详见Appointment.toDict()函数]}
    '''
    user = current_user
    app_list = []
    app_dict_list = []
    if user.identify == User.IDENTIFY_MENTOR:
        app_list = Appointment.query.filter(Appointment.men == user).order_by(
            desc(Appointment.submit_time)).offset(offset).limit(10).all()
    elif user.identify == User.IDENTIFY_STUDENT:
        app_list = Appointment.query.filter(Appointment.stu == user).order_by(
            desc(Appointment.submit_time)).offset(offset).limit(10).all()
    for appointment in app_list:
        app_dict_list.append(appointment.toDict())
    return jsonify({'status': SUCCESS, 'data': app_dict_list})


@app.route('/ajax/course/list/<offset>', methods=['GET', 'POST'])
@login_required
def ajax_course_list(offset):
    '''
    用来获取预约列表。自动检测身份，学生返回预约列表，门特返回被预约列表。每次10条。
    :param offset:起始条目。
    :return:json：{'status':状态代码（SUCCESS or BAD 详见config.py）,'data':[json列表，包含字典格式的预约信息，信息都是字符串，详见Appointment.toDict()函数]}
    '''
    user = current_user
    app_list = []
    app_dict_list = []
    if user.identify == User.MENTOR:
        app_list = Appointment.query.filter(Appointment.men == user).order_by(
            desc(Appointment.submit_time)).offset(offset).limit(10).all()
    elif user.identify == User.STUDENT:
        app_list = Appointment.query.filter(Appointment.stu == user).order_by(
            desc(Appointment.submit_time)).offset(offset).limit(10).all()
    for appointment in app_list:
        app_dict_list.append(appointment.toDict())
    return jsonify({'status': SUCCESS, 'data': app_dict_list})


@app.route('/ajax/appointment/new', methods=['POST'])
@login_required
def ajax_appointment_new():
    '''
    创建预约。使用Ajax提交表单，注意再headers加入X-CSRF-TOKEN，详见app/templates/examples/appointment_new.html中的form_submit方法。
    （所有的表单都在app.forms.py中，详见里面的类，类名都很直白hhhhh）
    :return:json:{'status':状态码} 注意除了需要处理状态码还要处理请求失败（error函数）。
    '''
    form = AppointmentNewForm()
    if current_user.identify == User.IDENTIFY_STUDENT:
        if form.validate_on_submit():
            men_id = form.men_id.data
            description = form.description.data
            men = User.query.filter(User.id == men_id).first()
            if men is not None:
                if men.identify == User.IDENTIFY_MENTOR:
                    appointment = Appointment(current_user, men, description)
                    appointment.update()
                    return jsonify({'status': SUCCESS})
                else:
                    return jsonify({'status': BAD})
            else:
                return jsonify({'status': BAD})
        else:
            return jsonify({'status': BAD})
    else:
        return jsonify({'status': BAD})


@app.route('/ajax/appointment/<aid>/pass', methods=['GET', 'POST'])
@login_required
def ajax_appointment_pass(aid):
    '''
    教师通过学生预约请求。
    :param aid:预约id。
    :return:json：{'status':状态代码（SUCCESS or BAD 详见config.py）}
    '''
    form = AppointmentReplyPassForm()
    if form.validate_on_submit():
        user = current_user
        appointment = Appointment.query.filter(Appointment.id == aid).first()
        if user.identify == User.IDENTIFY_MENTOR:
            if (appointment is not None) and (appointment.status == Appointment.STATUS_WAITING) and (
                        appointment.men.id == user.id):
                replytext = form.replytext.data
                location = form.location.data
                status = Appointment.STATUS_PASS
                time_start_string = form.time_start.data
                time_end_string = form.time_end.data

                match = re.search(r'(\d+)-(\d+)-(\d+) (\d+):(\d+)', time_start_string)
                y, m, d, h, i = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), int(
                    match.group(5))
                time_start = datetime(y, m, d, h, i)

                match = re.search(r'(\d+)-(\d+)-(\d+) (\d+):(\d+)', time_end_string)
                y, m, d, h, i = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), int(
                    match.group(5))
                time_end = datetime(y, m, d, h, i)

                appointment.replytext = replytext
                appointment.location = location
                appointment.status = status
                appointment.time_start = time_start
                appointment.time_end = time_end
                appointment.time_reply = datetime.now()

                appointment.update()
                return jsonify({'status': SUCCESS})
            else:
                return jsonify({'status': BAD})
        else:
            return jsonify({'status': BAD})
    else:
        return jsonify({'status': BAD})


@app.route('/ajax/appointment/<aid>/deny', methods=['GET', 'POST'])
@login_required
def ajax_appointment_deny(aid):
    '''
    教师拒绝学生预约请求。
    :param aid:预约id。
    :return:json：{'status':状态代码（SUCCESS or BAD 详见config.py）}
    '''
    form = AppointmentReplyDenyForm()
    if form.validate_on_submit():
        user = current_user
        appointment = Appointment.query.filter(Appointment.id == aid).first()
        if user.identify == User.IDENTIFY_MENTOR:
            if (appointment is not None) and (appointment.status == Appointment.STATUS_WAITING) and (
                        appointment.men.id == user.id):
                replytext = form.replytext.data
                appointment.replytext = replytext
                appointment.time_reply = datetime.now()
                appointment.status = Appointment.STATUS_DENY

                appointment.update()
                return jsonify({'status': SUCCESS})
            else:
                return jsonify({'status': BAD})
        else:
            return jsonify({'status': BAD})
    else:
        return jsonify({'status': BAD})


@app.route('/ajax/appointment/<aid>/delete', methods=['GET', 'POST'])
@login_required
def ajax_appointment_delete(aid):
    '''
    学生撤销预约。
    :param aid:预约id。
    :return:json：{'status':状态代码（SUCCESS or BAD 详见config.py）}
    '''

    user = current_user
    appointment = Appointment.query.filter(id == aid).first()

    if user.identify == User.MENTOR:
        if (appointment is not None) and (appointment.stu == user):
            appointment.delete()
            return jsonify({'statis': SUCCESS})
        else:
            return jsonify({'status': BAD})
    else:
        return jsonify({'status': BAD})


@app.route('/ajax/course/<cid>/sign', methods=['GET', 'POST'])
@login_required
def ajax_course_sign(cid):
    '''
    学生选课
    :param cid:课程id。
    :return: json：{'status':状态代码（SUCCESS or BAD 详见config.py）}
    '''
    user = current_user
    if user.identify == User.IDENTIFY_STUDENT:
        course = Course.query.filter(Course.id == cid).first()
        if course is not None:
            if (not course.full()) and (course.time_deadline > datetime.now()):
                course.addStu(user)
                return jsonify({'status': SUCCESS})
            else:
                return jsonify({'status': BAD})
        else:
            return jsonify({'status': BAD})
    else:
        return jsonify({'status': BAD})
