Add here [Livable Streets logo](https://livablestreets.herokuapp.com/)

[Livablestreets](https://livablestreets.herokuapp.com/) is co-created by [Carlos H. Vieira e Vieira](https://github.com/chvieira2), [Laia Grobe](https://github.com/Laiagdla), [Ieva Bidermane](https://github.com/ievabi) and [Nicolas Quiroga](https://github.com/nicoquiroga941) as conclusion project for the data science bootcamp at Le Wagon (batch 871) on June 2022.


Not into reading? Watch our project on YouTube [here](www.youtube.com).


# Find the Neighborhood You Love
Moving to a new city can be tough. How do you decide which neighborhood to live? Livablestreets is a web tool for exploring city livability at street level, and around the world.

Besides helping you and I finding our next homes, we envision livablestreets as a virtual laboratory for Urbanists. In the future, users will be able to add and remove features (roads, buildings, parks, businesses, etc) to evaluate the impact on livability around cities. Interested? Get in contact!



## What is livability?
In Urbanism, livability is a measurement of life quality and how good it feels to live in a place.

In livablestreets, we assess the livability scores at street level in cities all over the world by aggregating information on four main categories of living standards: access to Activities/Services, Comfort, Mobility, and Social Life.

## Behind the curtains
1. Livablestreets is a Python application doing the hard work for you. It uses [Streamlit](https://streamlit.io/) for visualization and is hosted on [Heroku](https://www.heroku.com).
2. Once the user inputs the name of the city of interest (and clicks on "Calculate Livability"), the app collects the geographical boundaries of the city of interest and information on ~200 features (bus stops, parks, trees, etc) from [OpenStreetsMap](www.openstreetmap.org) using the [Overpass API](http://overpass-api.de/).
3. The city map is virtually fragmented into squared grids. The grid dimensions define the spacial resolution of livability score and is set to 100m.
4. Features are then groupped in four pillars of living standards (Activities/Services, Comfort, Mobility, and Social Life).
5. To calculate livability scores according to the user own needs, we apply the weights for each pillar of living standards.
6. Finally, livability scores are displayed on the map of the city of interest as a heatmap, where warmer colors indicate higher livability score.

## Running it locally
To run the app locally, simply download and install it. If you are on a linux and use pip, simply run "pip install -e ." (without the quote signs, and don't ignore the dot at the end) from the app folder in your terminal. Start it on streamlit by running "streamlit run app.py", and open the indicated Network URL.

## Why can I only select from handful of cities?
The app works for any city, however the whole process can take several hours. Therefore, we pre-calculated livability scores for several cities and uploaded it for you. Feel free to change the weights according to your own needs.

Want more? Don't panic. You can add more cities!

## Can I add more cities?
Yes. However, we use a free service with limited capacity to host our application (Heroku). The easiest ways to add a city are: 1) to contact us; or 2) to run the app locally.

If you run livablestreets locally, you are now free to add all cities of your interest. For that you should:
1. Open to livablestreets/params.py, and include it in the list of preloaded cities ("preloaded_cities" variable). City name must be spelled in the local language (several language accent markers are supported). Save the file.
2. Run livablestreets/generator.py file and wait. The calculation may take several hours for larger cities. We recommend you to do it overnight.
3. Once done, reload the app and your cities will be included as a choice in the drop down menu.
