# TRA
Special thanks to Mr. Yo Mizutani for the visual.py, enabling visualization through pyvis: https://users.cs.utah.edu/~yos/2021/02/02/plotly-python.html.

Install all dependencies using pip install -r requirements.txt
This has worked under windows using a fresh virtual enviroment, however the kaleido package used to convert the htmls to pngs is dodgy, perhaps there is a better solution.

Update the customization at the top of nx_scraper.py to use the correct filepaths. The path for the png folder has to end with either a trailing \ or / on Linux.

Running the python file should then give you the complete graph and either the full neighbour graph or pngs of the graphs for every person depending on your selection.
