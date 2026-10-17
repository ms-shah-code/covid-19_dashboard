import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output

external_stylesheets = [
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
]

patients = pd.read_csv("IndividualDetails.csv")
patients.columns = patients.columns.str.strip()

required_columns = [
    "current_status",
    "diagnosed_date",
    "age",
    "gender",
    "detected_state",
]

missing_columns = [col for col in required_columns if col not in patients.columns]

if missing_columns:
    raise ValueError(f"Missing columns in CSV: {missing_columns}")

for col in ["current_status", "gender", "detected_state"]:
    patients[col] = (
        patients[col]
        .astype("string")
        .fillna("Unknown")
        .str.strip()
        .replace("", "Unknown")
        .fillna("Unknown")
        .astype(str)
    )

patients["diagnosed_date"] = pd.to_datetime(
    patients["diagnosed_date"],
    errors="coerce",
    dayfirst=True
)

patients["age_numeric"] = pd.to_numeric(
    patients["age"],
    errors="coerce"
)

total = len(patients)
hospitalized = patients["current_status"].eq("Hospitalized").sum()
recovered = patients["current_status"].eq("Recovered").sum()
deaths = patients["current_status"].eq("Deceased").sum()

options = [
    {"label": "All Cases", "value": "All"},
    {"label": "Hospitalized", "value": "Hospitalized"},
    {"label": "Recovered", "value": "Recovered"},
    {"label": "Deceased", "value": "Deceased"},
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.title = "COVID-19 Analytics Dashboard"

BG = "#0a0a0a"
PANEL = "#171717"
TEXT = "#f5f5f5"
MUTED = "#a3a3a3"
BORDER = "#333333"

card_style = {
    "backgroundColor": PANEL,
    "border": f"1px solid {BORDER}",
    "borderRadius": "16px",
    "padding": "22px",
    "height": "100%",
    "boxShadow": "0 8px 24px rgba(0,0,0,0.25)",
    "minWidth": "0",
}

number_style = {
    "fontSize": "clamp(25px, 3vw, 34px)",
    "fontWeight": "700",
    "color": TEXT,
    "marginBottom": "0",
    "overflowWrap": "anywhere",
}

def create_card(title, value, accent, icon):
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.P(
                                title,
                                style={
                                    "fontSize": "14px",
                                    "color": MUTED,
                                    "marginBottom": "12px",
                                },
                            ),
                            html.H2(f"{value:,}", style=number_style),
                        ],
                        style={"flex": "1", "minWidth": "0"},
                    ),
                    html.Div(
                        icon,
                        style={
                            "fontSize": "25px",
                            "backgroundColor": "#262626",
                            "color": accent,
                            "borderRadius": "12px",
                            "width": "54px",
                            "height": "54px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "flexShrink": "0",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "gap": "12px",
                },
            ),
            html.Div(
                style={
                    "height": "4px",
                    "backgroundColor": accent,
                    "borderRadius": "5px",
                    "marginTop": "22px",
                }
            ),
        ],
        style=card_style,
    )

def create_chart(title, graph_id, figure, height="420px"):
    return html.Div(
        [
            html.H4(
                title,
                style={
                    "color": TEXT,
                    "fontSize": "19px",
                    "fontWeight": "700",
                    "marginBottom": "15px",
                },
            ),
            dcc.Graph(
                id=graph_id,
                figure=figure,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "responsive": True,
                },
                style={"height": height, "width": "100%"},
            ),
        ],
        style={**card_style, "height": "auto"},
    )

def style_figure(fig, margin=None):
    fig.update_layout(
        template="plotly",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", color="#222222"),
        margin=margin or dict(l=35, r=25, t=65, b=45),
        autosize=True,
    )
    return fig

status_data = (
    patients["current_status"]
    .value_counts()
    .rename_axis("Status")
    .reset_index(name="Patients")
)

pie_fig = px.pie(
    status_data,
    names="Status",
    values="Patients",
    hole=0.48,
    title="Patient Status Distribution",
)

pie_fig.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="<b>%{label}</b><br>Patients: %{value:,}<br>Share: %{percent}<extra></extra>",
)

style_figure(pie_fig, dict(l=20, r=20, t=60, b=30))

date_data = (
    patients.dropna(subset=["diagnosed_date"])
    .groupby(patients["diagnosed_date"].dt.date)
    .size()
    .rename("Cases")
    .reset_index()
)

date_data.columns = ["Date", "Cases"]

trend_fig = px.line(
    date_data,
    x="Date",
    y="Cases",
    markers=True,
    title="Daily Reported Records",
)

trend_fig.update_traces(
    line=dict(width=3),
    hovertemplate="Date: %{x}<br>Records: %{y:,}<extra></extra>",
)

style_figure(trend_fig)
trend_fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Number of Records",
)

monthly_data = (
    patients.dropna(subset=["diagnosed_date"])
    .set_index("diagnosed_date")
    .resample("MS")
    .size()
    .rename("Cases")
    .reset_index()
)

monthly_fig = px.bar(
    monthly_data,
    x="diagnosed_date",
    y="Cases",
    title="Monthly Reported Records",
    labels={
        "diagnosed_date": "Month",
        "Cases": "Number of Records",
    },
)

style_figure(monthly_fig)

age_data = patients.dropna(subset=["age_numeric"]).copy()
age_data = age_data[age_data["age_numeric"].between(0, 120)]

age_data["Age Group"] = pd.cut(
    age_data["age_numeric"],
    bins=[-1, 12, 18, 30, 45, 60, 120],
    labels=["0–12", "13–18", "19–30", "31–45", "46–60", "61+"],
)

age_summary = (
    age_data["Age Group"]
    .value_counts()
    .reindex(["0–12", "13–18", "19–30", "31–45", "46–60", "61+"])
    .fillna(0)
    .rename_axis("Age Group")
    .reset_index(name="Patients")
)

age_fig = px.bar(
    age_summary,
    x="Age Group",
    y="Patients",
    title="Patient Distribution by Age",
    text="Patients",
)

age_fig.update_traces(
    hovertemplate="Age Group: %{x}<br>Patients: %{y:,}<extra></extra>"
)

style_figure(age_fig)
age_fig.update_layout(
    xaxis_title="Age Group",
    yaxis_title="Number of Patients",
)

gender_summary = (
    patients["gender"]
    .value_counts()
    .rename_axis("Gender")
    .reset_index(name="Patients")
)

gender_fig = px.pie(
    gender_summary,
    names="Gender",
    values="Patients",
    hole=0.4,
    title="Gender Distribution",
)

gender_fig.update_traces(
    textinfo="percent+label",
    hovertemplate="<b>%{label}</b><br>Patients: %{value:,}<extra></extra>",
)

style_figure(gender_fig, dict(l=20, r=20, t=60, b=30))

status_state_data = (
    patients.groupby(["detected_state", "current_status"], dropna=False)
    .size()
    .reset_index(name="Patients")
)

status_state_fig = px.bar(
    status_state_data,
    x="detected_state",
    y="Patients",
    color="current_status",
    title="State-wise Patient Status Comparison",
    labels={
        "detected_state": "State",
        "current_status": "Patient Status",
        "Patients": "Number of Records",
    },
    barmode="stack",
)

style_figure(
    status_state_fig,
    dict(l=35, r=20, t=60, b=110),
)

status_state_fig.update_layout(
    xaxis_title="State",
    yaxis_title="Number of Records",
    xaxis_tickangle=-45,
)

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    "COVID-19 Analytics Dashboard",
                    style={
                        "fontSize": "clamp(26px, 4vw, 38px)",
                        "fontWeight": "800",
                        "marginBottom": "8px",
                    },
                ),
                html.P(
                    "Patient records and statistical analysis",
                    style={"color": MUTED, "fontSize": "15px"},
                ),
            ],
            style={"padding": "35px 0 25px"},
        ),

        html.Div(
            [
                html.Div(
                    create_card("Total Cases", total, "#60a5fa", "▦"),
                    className="col-12 col-sm-6 col-xl-3 mb-4",
                ),
                html.Div(
                    create_card("Hospitalized", hospitalized, "#fbbf24", "✚"),
                    className="col-12 col-sm-6 col-xl-3 mb-4",
                ),
                html.Div(
                    create_card("Recovered", recovered, "#34d399", "✓"),
                    className="col-12 col-sm-6 col-xl-3 mb-4",
                ),
                html.Div(
                    create_card("Deaths", deaths, "#f87171", "✕"),
                    className="col-12 col-sm-6 col-xl-3 mb-4",
                ),
            ],
            className="row",
        ),

        html.Div(
            [
                html.Div(
                    create_chart(
                        "Patient Status Distribution",
                        "pie",
                        pie_fig,
                    ),
                    className="col-12 col-xl-6 mb-4",
                ),
                html.Div(
                    create_chart(
                        "Daily Reported Records",
                        "trend",
                        trend_fig,
                    ),
                    className="col-12 col-xl-6 mb-4",
                ),
                html.Div(
                    create_chart(
                        "Monthly Reported Records",
                        "monthly",
                        monthly_fig,
                    ),
                    className="col-12 col-xl-6 mb-4",
                ),
                html.Div(
                    create_chart(
                        "Age Group Analysis",
                        "age",
                        age_fig,
                    ),
                    className="col-12 col-xl-6 mb-4",
                ),
                html.Div(
                    create_chart(
                        "Gender Distribution",
                        "gender",
                        gender_fig,
                    ),
                    className="col-12 col-xl-6 mb-4",
                ),
                html.Div(
                    create_chart(
                        "State-wise Patient Status Comparison",
                        "status_state",
                        status_state_fig,
                        "500px",
                    ),
                    className="col-12 col-xl-6 mb-4",
                ),

                html.Div(
                    [
                        html.H4(
                            "State-wise Case Distribution",
                            style={
                                "color": TEXT,
                                "fontSize": "19px",
                                "fontWeight": "700",
                                "marginBottom": "15px",
                            },
                        ),
                        html.Label(
                            "FILTER BY STATUS",
                            style={
                                "color": MUTED,
                                "fontSize": "12px",
                                "fontWeight": "700",
                                "marginBottom": "8px",
                            },
                        ),
                        dcc.Dropdown(
                            id="picker",
                            options=options,
                            value="All",
                            clearable=False,
                            searchable=False,
                            style={
                                "color": "#171717",
                                "maxWidth": "350px",
                                "marginBottom": "20px",
                            },
                        ),
                        dcc.Graph(
                            id="bar",
                            config={
                                "displayModeBar": True,
                                "displaylogo": False,
                                "responsive": True,
                            },
                            style={"height": "480px", "width": "100%"},
                        ),
                    ],
                    style={**card_style, "height": "auto"},
                    className="col-12 mb-4",
                ),
            ],
            className="row",
        ),

        html.P(
            "COVID-19 Data Analysis | Python, Pandas, Plotly and Dash",
            style={
                "color": MUTED,
                "textAlign": "center",
                "padding": "20px 0 30px",
                "fontSize": "13px",
            },
        ),
    ],
    style={
        "backgroundColor": BG,
        "color": TEXT,
        "minHeight": "100vh",
        "padding": "0 4%",
        "fontFamily": "Arial, sans-serif",
    },
)

@app.callback(
    Output("bar", "figure"),
    Input("picker", "value"),
)
def update_graph(selected_status):
    if selected_status == "All":
        selected = patients
        chart_title = "Total Cases by State"
    else:
        selected = patients[
            patients["current_status"].eq(selected_status)
        ]
        chart_title = f"{selected_status} Cases by State"

    temp = (
        selected.groupby("detected_state")
        .size()
        .rename("Cases")
        .reset_index()
        .sort_values("Cases", ascending=True)
    )

    fig = px.bar(
        temp,
        x="Cases",
        y="detected_state",
        orientation="h",
        text="Cases",
        title=chart_title,
        labels={
            "detected_state": "State",
            "Cases": "Number of Records",
        },
    )

    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Records: %{x:,}<extra></extra>",
    )

    style_figure(
        fig,
        dict(l=20, r=60, t=65, b=40),
    )

    fig.update_layout(
        font=dict(family="Arial, sans-serif", color="#222222"),
        xaxis_title="Number of Records",
        yaxis_title="",
        showlegend=False,
        yaxis=dict(automargin=True),
    )

    if temp.empty:
        fig.add_annotation(
            text="No records available for this selection",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )

    return fig

if __name__ == "__main__":
    app.run(debug=True)
