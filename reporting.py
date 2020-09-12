from pdf_reports import write_report, pug_to_html
from pdf_reports.tools import figure_data
import matplotlib.pyplot as plt

#%%

class Report:
    """A simple reporting class"""

    html = ""
    
    def __init__(self, title):
          self.html += pug_to_html(string="h1 {{ title }}", title = title)

    def add_section(self, title = "", text = "", plot = None):
          self.html += pug_to_html(string="h2 {{ title }}", title = title)
          self.html += pug_to_html(string="p {{ text }}", text = text)

          if plot:
                try:
                      for p in plot:
                            self.html += '<img src="'+figure_data(p, size=(10,2.5), fmt = "png")+'"/>'
                except:
                      self.html += '<img src="'+figure_data(plot, fmt = "png")+'"/>'

                

    def write(self, path):
        write_report(self.html, path)
