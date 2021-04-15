import base64
import collections
import os

# Import Python wrapper for or-tools CP-SAT solver.
from ortools.sat.python import cp_model
import datetime
import pandas as pd
import numpy as np

# cannot applied to carton order since the job can be processed by different machine
jobs_data = [  # task = (machine_id, processing_time).
    [(0, 0, 1)],  # Job0
    [(0, 0, 1 )]
]

scheduler_data = []

def is_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def check_file(path):
    try:
        with open(path, "r") as file:
            reader = csv.reader(file)
            next(reader)
            # TODO: Read content
            global jobs_data
            jobs_data = []
            for row in reader:
                job = []
                for i in range(1, len(row) - 1):
                    if is_number(row[i]):
                        if i % 2 == 1:
                            job.append((int(row[i]), int(row[i + 1])))
                # print(job)
                jobs_data.append(job)
    except:
        print("Error! Check the template file")
        return 1
    return 0


def jobshop_scheduler(jobs_data):
    # Create the model.
    model = cp_model.CpModel()

    machines_count = 1 + max(task[0] for job in jobs_data for task in job)
    all_machines = range(machines_count)

    # Computes horizon dynamically as the sum of all durations.
    horizon = sum(task[1] for job in jobs_data for task in job)

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple('task_type', 'start end interval')
    # Named tuple to manipulate solution information.
    assigned_task_type = collections.namedtuple('assigned_task_type',
                                                'start job index duration')

    # Creates job intervals and add to the corresponding machine lists.
    all_tasks = {}
    machine_to_intervals = collections.defaultdict(list)

    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine = task[0]
            duration = task[1]
            suffix = '_%i_%i' % (job_id, task_id)
            start_var = model.NewIntVar(0, horizon, 'start' + suffix)
            end_var = model.NewIntVar(0, horizon, 'end' + suffix)
            interval_var = model.NewIntervalVar(start_var, duration, end_var,
                                                'interval' + suffix)
            all_tasks[job_id, task_id] = task_type(
                start=start_var, end=end_var, interval=interval_var)
            machine_to_intervals[machine].append(interval_var)

    # Create and add disjunctive constraints.
    for machine in all_machines:
        model.AddNoOverlap(machine_to_intervals[machine])

    # Precedences inside a job.
    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job) - 1):
            model.Add(all_tasks[job_id, task_id +
                                1].start >= all_tasks[job_id, task_id].end)

    # Makespan objective.
    obj_var = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(obj_var, [
        all_tasks[job_id, len(job) - 1].end
        for job_id, job in enumerate(jobs_data)
    ])
    model.Minimize(obj_var)

    # Solve model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        # Create one list of assigned tasks per machine.
        assigned_jobs = collections.defaultdict(list)
        for job_id, job in enumerate(jobs_data):
            for task_id, task in enumerate(job):
                machine = task[0]
                assigned_jobs[machine].append(
                    assigned_task_type(
                        start=solver.Value(all_tasks[job_id, task_id].start),
                        job=job_id,
                        index=task_id,
                        duration=task[1]))

        # Create per machine output lines.
        date = datetime.datetime(2020, 1, 1, 6, 0, 0)
        output = []
        for machine in all_machines:
            # Sort by starting time.
            assigned_jobs[machine].sort()

            for assigned_task in assigned_jobs[machine]:
                name = 'job_%i_%i' % (assigned_task.job, assigned_task.index)

                start = date + datetime.timedelta(minutes=assigned_task.start)
                finish = date + datetime.timedelta(minutes=assigned_task.start + assigned_task.duration)

                output.append(dict(Task='Machine ' + str(machine), Start=start, Finish=finish, Name=name,
                                   Job='Job_' + str(assigned_task.job)))

        # Finally print the solution found.
        print('Optimal Schedule Length: %i' % solver.ObjectiveValue())
        print(output)

    return output


def gantt_fig(data):
    # Generate random color for each job
    df = pd.DataFrame(data)
    all_jobs = df['Job'].unique()
    colors = []
    for job in all_jobs:
        colors.append((job, 'rgb' + str(tuple(np.random.choice(range(256), size=3)))))

    colors = dict(colors)
    # print(colors)

    fig = ff.create_gantt(data, colors=colors, index_col='Job',
                          group_tasks=True, show_colorbar=True,
                          showgrid_x=True, title='Gantt Chart')
    # fig.show()
    fig['layout'].update(margin=dict(l=310))
    return fig


# Using external stylesheet
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app = dash.Dash(__name__)

app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1('Job Shop Scheduler')
        ], className="nine columns"),
        html.Div([
            html.Img(src=app.get_asset_url('ArtcLogoNewNoAlpha.png'))
        ], className='two columns')
    ], style={'color': 'white', 'backgroundColor': 'DarkBlue', "height": "125px"}),

    html.Div([
        html.Div([
            html.H3('Upload a Schedule'),
            dcc.Upload(
                id="upload-data",
                children=html.Div(
                    ["Click to select a file to upload."]
                ),
                style={
                    "width": "80%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                multiple=True,
            ),
            html.Div(id='status-upload'),

            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),

            html.Div([
                html.H3('Run the Scheduler'),
                html.Button('Run Scheduler', id='schedule-run', className="button-primary"),
                html.Div(id='status-run'),

                html.Br(),
                html.Br(),

                html.Button('View Gantt', id='view-gantt', className="button-primary", disabled=True),

            ]),
        ], className="three columns"),

        html.Div([
            dcc.Graph(id='gantt-chart'),
        ], className="eight columns"),
    ], className="row"),

    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),

    html.H3('Download Template and Samples'),
    html.A(
        'Template File',
        id='download-link',
        download="template.csv",
        href="/download/template",
        target="_blank"
    ),
    html.Br(),
    html.A(
        'Sample File 1',
        id='sample-link',
        download="sample_1.csv",
        href="/download/sample1",
        target="_blank"
    ),
    html.Div(id='down-status'),

])


# Handle download request
@app.server.route('/download/template')
def download_template():
    return send_file(os.path.join(TEMPLATE_DIR, TEMPLATE_NAME),
                     mimetype='text/csv',
                     attachment_filename='template.csv',
                     as_attachment=True
                     )


@app.server.route('/download/sample1')
def download_sample():
    return send_file(os.path.join(TEMPLATE_DIR, SAMPLE_NAME),
                     mimetype='text/csv',
                     attachment_filename='sample1.csv',
                     as_attachment=True
                     )


# Callback for viewing the gantt chart
@app.callback(
    dash.dependencies.Output('gantt-chart', 'figure'),
    [dash.dependencies.Input('view-gantt', 'n_clicks')]
)
def view_gantt(n):
    if n is None:
        raise PreventUpdate
    else:
        return gantt_fig(scheduler_data)


# Run the scprit when click the button and return the running status and enable view button
@app.callback(
    [
        dash.dependencies.Output('status-run', 'children'),
        dash.dependencies.Output('view-gantt', 'disabled')
    ],
    [dash.dependencies.Input('schedule-run', 'n_clicks')]
)
def run_scheduler(n):
    if n is None:
        return "Click the button to run the scheduler!", True
    else:
        global scheduler_data
        scheduler_data = jobshop_scheduler(jobs_data)
        return "The Gantt is ready for viewing", False


# Callback for uploading file
@app.callback(
    dash.dependencies.Output("status-upload", "children"),
    [
        dash.dependencies.Input("upload-data", "filename"),
        dash.dependencies.Input("upload-data", "contents")
    ],
)
def upload_file(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""
    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            status = save_file(name, data)
        # TODO: Check file
        if status:
            return "Check the format of uploaded file"
        else:
            return "File Uploaded!"
    else:
        return "No File Selected!"


if __name__ == '__main__':
    # Test check_file
    # check_file("/scheduler/template/workordersTemplate.csv")

    app.run_server(debug=True)
