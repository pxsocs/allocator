from highcharts import Highchart

CHART_DEFAULTS = {
    "colors":
    ["#2C6A3E", "#09654E", "#005F5A", "#00585F", "#1D505F", "#2F4858"],
    "chart": {
        "backgroundColor": "#FFFFFF",
        "style": {
            "fontFamily": "Dosis, sans-serif"
        }
    },
    "title": {
        "style": {
            "fontSize": "12px",
            "fontWeight": "bold",
            "textTransform": "uppercase"
        }
    },
    "tooltip": {
        "borderWidth": 0,
        "backgroundColor": 'rgba(219,219,216,0.8)',
        "shadow": False,
        "valueDecimals": 2
    },
    "legend": {
        "itemStyle": {
            "fontWeight": 'bold',
            "fontSize": '10px'
        }
    },
    "xAxis": {
        "gridLineWidth": 1,
        "tickInterval": 1,
        "minPadding": 0,
        "maxPadding": 0,
        "startOnTick": True,
        "endOnTick": True,
        "labels": {
            "style": {
                "fontSize": '10px'
            }
        }
    },
    "yAxis": {
        "minorTickInterval": 'auto',
        "title": {
            "style": {
                "textTransform": 'uppercase'
            }
        },
        "labels": {
            "style": {
                "fontSize": '10px'
            }
        }
    }
}


def plot_chart(x,
               y,
               x_label='',
               y_label='',
               type='spline',
               label='data',
               title='',
               subtitle='',
               dt=True):
    # SAMPLE USAGE BELOW
    # from highcharts import Highchart
    # from chart_builder import CHART_DEFAULTS, plot_chart
    # x = [0, 10, 20, 30, 40]
    # y = [1, 3, -3, 7, 10]
    # plot_chart(x, y, 'spline', 'Temperature', 'This is a title')
    data = []
    for index, item in enumerate(x):
        data.append([item, y[index]])
    chart = Highchart()
    # Get Defaults from above
    chart.set_dict_options(CHART_DEFAULTS)
    chart.set_options('title', {'text': title})
    chart.set_options('subtitle', {'text': subtitle})
    if dt is True:
        chart.set_options('xAxis', {'type': 'datetime'})
    chart.set_options('xAxis', {'title': {'text': x_label}})
    chart.set_options('yAxis', {'title': {'text': y_label}})
    chart.add_data_set(data, type, label)
    return (chart)
