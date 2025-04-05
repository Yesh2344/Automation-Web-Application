from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired

class TaskForm(FlaskForm):
    name = StringField('Task Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        (1, 'Low'), 
        (2, 'Medium'), 
        (3, 'High')
    ], coerce=int, default=1)
    task_type = SelectField('Task Type', choices=[
        ('general', 'General'),
        ('email', 'Email'),
        ('file', 'File Processing'),
        ('api', 'API Call')
    ], default='general')
    submit = SubmitField('Create Task')
