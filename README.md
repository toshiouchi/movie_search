# movie_search

We report video search system using image captioning and sentence-transformers. 

## Folder

```
--movie_search---movies--- *.mp4 files
               |
               |-make_text_file_english.ipynb // In order to make 00_movie_search.txt file

--client folder---index.html and client.php
                |
                |---movies--- *.mp4 files

--server folder---server.py // Make server.py resident using the '>python server.py' command.
                |
                |---corpus---00_movie_search.txt
```
               
Please put multiple *.mp4 files in movie_search/movies folder. The movie_search folder can be opened with jupyter_notebook.  With jupyter-notebook, please open make_text_file_english.ipynb. If you run cell in order from the top, a 00_movie_search.txt file will be created. In this process, images and text folder is created too.

## Actions

Please, create a folder under the document root of the web server with PHP. Please put index.html and client.php in this folder. In this folder, please make movies forder and put movies same as above. Please make server program folder and put server.py and make corpus folder. The python command can be used in the server program folder. Please put 00_movie_search.txt in corpus folder. Make server.py resident using the '>python server.py' command.

With browser, please access index.html and put "zebra", for example, in the search sentence text field and search.

![fig1](https://github.com/toshiouchi/movie_search/assets/121741811/5ad46ea8-04fc-40b4-91eb-0db883886ed1)

 
Search results are displayed within 1 seconds.

![fig2](https://github.com/toshiouchi/movie_search/assets/121741811/72a620cd-78e0-4b6d-a7dd-7e0d155c57e2)


Click "cue" to the right of "two zebras are eating some hay in a field." at the top of the table.

![fig3](https://github.com/toshiouchi/movie_search/assets/121741811/d7d52d6c-2bf7-45d9-a0b0-b05e4e09f77a)

video "two zebras are eating some hay in a field" is played.

## Mechanisms

### In make_text_file_english.ipynb

Video is converted into images every second with OpenCV, and images that are similar to the previous video are omitted, and only images that are dissimilar are saved. Judgment of similarities and dissimilarities is done using imgsim. The name of the image file includes the time (number of seconds) within the video.  Image captioning is performed to the image files using the Coca model. The OpenAI clip-vit-base-patch32 model evaluates images and captions, and removes inappropriate captions.　00_movei_search.txt is created in this way.

### In server.py

The distance is calculated using sentence-transformers between the previous caption and the current caption, and similar captions are not registered on the search server
