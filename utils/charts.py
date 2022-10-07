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
        margin=dict(l=0, r=0, t=0)
    )

    return fig