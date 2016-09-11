import requests
import pprint
import csv
import pandas as pd
import re
import matplotlib.pyplot as plt
from matplotlib import animation
import os
import numpy as np
# Make the HTTP request.

def dataset_search(to_find):
    resp = requests.get('https://data.gov.sg/api/action/package_list')
    contents_page = resp.json()["result"]
    #to add regex
    searched = [topic for topic in contents_page if topic.find(to_find) > -1]
    print(searched)
    return searched

class NonUniqueTimesError(Exception):
    pass

class dataset():
    def __init__(self, topic):
        resp = requests.get("https://data.gov.sg/api/action/package_show?id=" + topic)
        first_rsrc = resp.json()["result"]["resources"][0]
        self.file_type = first_rsrc.get("format")
        self.url = first_rsrc.get("url")
        self.title = resp.json()["result"]["name"]
        time_series = False
        for field in first_rsrc["fields"]:
            if field["type"] =="datetime":
                self.date_var = field["name"]
                time_series = True
                break
                
        #Raise error if time data cannot be found
        assert time_series == True, "Could not find time series data"
        self.df = self.to_dataframe()
        self.time_as_list = self.df[self.date_var].unique().tolist()
        
        #Check whether it is data where the same time period appears multiple times. Currently, this
        #script does not support making these kinds of data sets gifs
        #Good test case would be distribution data sets
        if len(self.time_as_list) != self.df[self.date_var].shape[0]:
            raise NonUniqueTimesError
        self.summary = {"file_type": self.file_type, "url": self.url, "title": self.title}
        
    # Make the HTTP request.

    def to_dataframe(self):
        data = requests.get(self.url)
        decoded_content = data.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        return pd.DataFrame(my_list[1:], columns=my_list[0])
    
    #to fix the one variable case and add a generic schema to subset relevant data
    def to_gif(self):
        df_Y = self.df.drop(self.date_var, axis=1).astype(float)
        biggest_Y = max(pd.DataFrame.max(df_Y))
        biggest_X = len(df_Y.columns)
        fig = plt.figure()
        ax = plt.axes(xlim=(0,biggest_X), ylim=(0,biggest_Y))
        line, = ax.plot([], [], lw=2)
        
        def animate_year(frame_num):
            plt.clf()
            
            time_as_list = self.df[self.date_var].unique().tolist()
            yr = time_as_list[frame_num]
            fig.suptitle(yr)
            df = self.df
            
            df_Y = df[df[self.date_var] == yr].drop(self.date_var, axis=1).astype(float)
            
            Y = df_Y.as_matrix()[0]
            X = np.array(range(df_Y.shape[1]))
            ax = plt.axes(xlim=(0,biggest_X), ylim=(0,biggest_Y))
            x_tick_name = df_Y.columns.tolist()
            x_tick_loc = [float(x)+0.5 for x in range(df_Y.shape[1])]
            plt.xticks( x_tick_loc, x_tick_name)
            
            line = plt.bar(X, Y)
            return line

        ani = animation.FuncAnimation(fig, animate_year, frames=len(self.time_as_list), interval=25,repeat=True,repeat_delay=1000)
#         ani.save("testing.mp4", fps=2, extra_args=['-vcodec', 'libx264'])
        plt.show()

dataset_search("car")
dataset('air-cargo-discharged-loaded').to_gif()