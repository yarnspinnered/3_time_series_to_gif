import requests
import pprint
import csv
import pandas as pd
import re
# Make the HTTP request.

def dataset_search(to_find):
    resp = requests.get('https://data.gov.sg/api/action/package_list')
    contents_page = resp.json()["result"]
    #to add regex
    searched = [topic for topic in contents_page if topic.find(to_find) > -1]
    return searched

class dataset():
    def __init__(self, topic):
        resp = requests.get("https://data.gov.sg/api/action/package_show?id=" + topic)
        first_rsrc = resp.json()["result"]["resources"][0]

        self.file_type = first_rsrc.get("format")
        self.url = first_rsrc.get("url")
        self.title = resp.json()["result"]["name"]
        try:
            self.schema = first_rsrc.get("fields",[{"format" : None}])[0]["format"]
        except KeyError:
            self.schema = first_rsrc.get("fields",[{"format" : None}])[1]["format"]
            
        self.summary = {"file_type": self.file_type, "url": self.url, "title": self.title, "schema": self.schema}
        
    # Make the HTTP request.

    def to_dataframe(self):
        data = requests.get(self.url)
        decoded_content = data.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        return pd.DataFrame(my_list[1:], columns=my_list[0])
    
    #to fix the one variable case and add a generic schema to subset relevant data
    def to_gif(self, gif_path):
        fig,ax = plt.subplots()
        ax = plt.axes(xlim=(0, 20), ylim=(0, 120000))
        line, = ax.plot([], [], lw=2)

        def animate_year(frame_num):
            yr = frame_num + 2005
            fig.suptitle(yr)
            temp_series = df[df["year"]==yr]["number"]
            temp_series.index = df[df["year"]==yr]["age_year"].str.split("-").str[0]
            line.set_data(temp_series.index, temp_series.values)
            return line

        ani = animation.FuncAnimation(fig, animate_year, frames=11, interval=25,repeat=True,repeat_delay=1000)
        ani.save("testing.mp4g.mp4", fps=2, extra_args=['-vcodec', 'libx264'])

# print(dataset('price-indices-of-selected-consumer-items-base-year-2014-100-monthly').to_dataframe())
print(dataset_search("car"))


# for index, topic in enumerate(contents_page["result"]):
#     if index == 38:
        
#         print(topic)
#         pprint.pprint(specific.json())
#         pprint.pprint(dict_parser(topic))        
#         break
