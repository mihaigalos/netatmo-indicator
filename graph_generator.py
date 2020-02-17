from collections import OrderedDict
import plotly, os
import plotly.plotly as py
import json
from plotly.graph_objs import *
import time

class MakePlot:
    def __init__(self):
        with open(os.path.join(os.path.expanduser('~'), 'netatmo_data.json')) as f:
            try:
                self.data = json.load(f)
                self.data = OrderedDict(sorted(self.data.items(), key=lambda t: t[0]))
            except Exception, err:
                print(err)
            f.close()

    def read_data(self):
        x= []
        y= [ [] for i in range(len(self.data.values()[1]))]

        captions = [key for (key, value) in self.data.values()[0].items()]

        i = 0
        for k,v in self.data.items():
            x.append(k.split(" ")[1])
            i=0
            for location, value in v.items():
                y[i].append(value)
                i=i+1
        return (x, y, captions)

    def construct_trace(self, x, y, caption):
        return {
          "x": x,
          "y": y,
          "line": {"shape": "spline"},
          "mode": "lines+markers",
          "type": "scatter",
          "name": caption
        }

    def draw(self):

        x, y, captions = self.read_data()

        traces = []
        i = 0
        for y_value in y:
            trace = self.construct_trace(x, y_value, captions[i])
            traces.append(trace)
            i +=1

        data = Data(traces)

        layout = {
            "showlegend":False,
            "xaxis" : {"nticks":10}
        }
        fig = Figure(data=data, layout=layout)
        plot_url = plotly.offline.plot(fig)

MakePlot().draw()
