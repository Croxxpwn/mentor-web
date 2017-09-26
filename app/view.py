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


@app.route('/appointment')
@login_required
def appointment():
    user = User.query.filter(User.id == 16210001).first()
    form = AppointmentNewForm()
    mens = User.query.filter(User.identify == User.IDENTIFY_MENTOR).all()
    return render_template('appointment.html', mens=mens, form=form)


@app.route('/course', methods=['GET'])
@login_required
def course():
    return render_template('course.html')


@app.route('/result/stu', methods=['GET'])
@login_required
def result_stu():
    return render_template('result_stu.html')


@app.route('/result/men', methods=['GET'])
@login_required
def result_men():
    return render_template('result_men.html')


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


@app.route('/ajax/appointment/<aid>/reply', methods=['GET', 'POST'])
@login_required
def ajax_appointment_reply(aid):
    '''
    教师回复学生预约请求。
    :param aid:预约id。
    :return:json：{'status':状态代码（SUCCESS or BAD 详见config.py）}
    '''
    form = AppointmentReplyForm()
    if form.validate_on_submit():
        user = current_user
        appointment = Appointment.query.filter(id == aid).first()

        if user.identify == User.MENTOR:
            if (appointment is not None) and (appointment.men == user):
                replytext = form.replytext.data
                status = Appointment.PASS if form.status.data else Appointment.DENY
                appointment.replytext = replytext
                appointment.status = status
                appointment.update()
                return jsonify({'statis': SUCCESS})
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


@app.route('/ajax/course/new', methods=['POST'])
@login_required
def ajax_course_new():
    '''
    创建团体课。使用Ajax提交表单，注意再headers加入X-CSRF-TOKEN，详见app/templates/examples/appointment_new.html中的form_submit方法。
    （所有的表单都在app.forms.py中，详见里面的类，类名都很直白hhhhh）
    :return:json:{'status':状态码} 注意除了需要处理状态码还要处理请求失败（error函数）。
    '''
    form = CourseNewForm()
    if current_user.identify == User.IDENTIFY_MENTOR:
        if form.validate_on_submit():
            men = current_user
            name = form.name.data
            capacity = form.capacity.data
            department = form.department.data
            description = form.description.data
            location = form.location.data
            time_start = form.time_start.data
            time_end = form.time_end.data
            time_deadline = form.time_deadline.data

            course = Course(name, department, men, capacity, description, location, time_start, time_end, time_deadline)
            course.update()

            return jsonify({'status': SUCCESS})

        else:
            return jsonify({'status': BAD})
    else:
        return jsonify({'status': BAD})
