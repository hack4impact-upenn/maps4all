from flask import render_template
from flask.ext.login import login_required
from . import admin_dashboard

@admin_dashboard.route('/manage-resources')
@login_required
def manage_resources():
    return render_template('admin_dashboard/manage_resources.html')

@admin_dashboard.route('/suggestions')
@login_required
def suggestions():
    return render_template('admin_dashboard/suggestions.html')

@admin_dashboard.route('/analytics')
@login_required
def analytics():
    return render_template('admin_dashboard/analytics.html')