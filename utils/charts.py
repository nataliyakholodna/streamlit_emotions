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
    """
    Create a vertical bar chart using Plotly.

    :param x: array-like
    :param y: array-like
    :return: plotly Figure object
    """
    fig = go.Figure([go.Bar(x=list(x),
                            y=list(y),
                            text=list(y), textposition='auto')])
    fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0),
                      yaxis=dict(showticklabels=False))
    fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                      marker_line_width=1.5, opacity=0.6)

    return fig


def show_lines(df, x_col, y_cols, text_col, colors):
    fig = go.Figure()

    # preprocess hashtags for each day
    # for hint on hover

    hvr = []
    for i in range(len(df)):
        # split string with hashtags
        txt = df[text_col].loc[i].split(',')
        # clean whitespaces
        txt = [t.strip() for t in txt]
        # create an array of strings for each day
        txt_markup = ''
        for j in txt:
            txt_markup += j + '<br>'
        if txt_markup == '<br>':
            txt_markup = 'None'
        hvr.append(txt_markup)

    hover = 'Date: %{x}' + '<br>Num tweets: %{y}<br>' + \
            '--------------<br>Hashtags:<br>--------------<br><b>%{text}</b>'

    for y_col, color in zip(y_cols, colors):
        fig.add_trace(go.Scatter(x=df[x_col],
                                 y=df[y_col],
                                 name=y_col,
                                 line=dict(color=color),
                                 hovertemplate=hover,
                                 text=hvr, fill='tozeroy'))

    fig.update_layout(hovermode='closest',
                      margin=dict(l=0, r=0, b=10))
    fig.update_layout(paper_bgcolor="white", plot_bgcolor="white")
    fig.update_xaxes(showgrid=True, gridcolor='#d2d7df')
    fig.update_yaxes(showgrid=True, gridcolor='#d2d7df')
    return fig
