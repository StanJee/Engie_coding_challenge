How to run the script:

$> ./run

OR

$> python3 -m venv venv             ---> creating a virtual environment
$> source venv/bin/activate         ---> activate this virtual environment 
$> pip install Flask                ---> install flask on the virtual environment
$> python3 my_app.py            OR export   $> FLASK_APP=my_app.py         ---> launch the application
                                            $> flask_run -p 8888

then use postman to send payload.json on : http://127.0.0.1:8888/productionplan


[optionnal]
When finished

$> deactivate     ---> exit virtual environment
$> rm -rd venv    ---> delete the virtual environment