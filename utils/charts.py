import plotly.graph_objects as go


def show_table(df):
    fig = go.Figure(data=[go.Table(
        columnwidth=[200, 1200],
        header=dict(values=list(df.columns),
                    # fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df[col] for col in df.columns],
                   # fill_color='lavender',
                   align='left',
                   font_size=14))
    ])
    fig.update_layout(
        width=1400,
        height=500,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig


def show_bar(x, y):
    fig = go.Figure([go.Bar(x=list(x),
                            y=list(y),
                            text=list(y), textposition='auto')])
    fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0),
                      yaxis=dict(showticklabels=False))
    fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                      marker_line_width=1.5, opacity=0.6)

    return fig
