# Mandatory instructions you should follow before running the DAGS
1. You can change all the configurable parameters by editing the **config.json** in the **config** folder. The parameters look like:
  {\
  "homepage_url": "https://news.google.com/home?hl=en-IN&gl=IN&ceid=IN:en",   \
  "smtp_server": "smtp.gmail.com",\
  "smtp_port": 587,\
  "smtp_username": "your_email@example.com", \
  "smtp_password": "your_password",\
  "recipient_email": "your_email@example.com" \
  }
2. You must update this config file with your credentials.
3. 
4. Go to your google account **Settings > Security > Turn-off 2FA > then go to 'Less secure app access' > Turn it ON**. This is crucial for sending an mail to your account on GMAIL.
5. Setup these connections on your **Airflow Webserver**:\
   a. **webserver (http://localhost:8080/home) > Admin > Connections > Add > Enter - {"Connection Id": "fs_default", "Connection Type": "File (path)", "Path": "/opt/airflow/dags/run/"}** \
   b. **webserver (http://localhost:8080/home) > Admin > Connections > Add > Enter - {"Connection Id": "postgress_default", "Connection Type": "Postgres", "Host": "postgres", "Login": "airflow", "Port": 5432}**

# General Instructions to help navigate files and folders
1. There are 2 DAGs inside the dags folder - **pipeline.py** & **send_email_dag.py**
2. You only have to run **pipeline.py** as it triggers **send_email_dag.py** once it has executed successfully or when it notices and update in the status file inside the **run** folder inside **dags**.
3. The pipeline DAG uses 5 custom made operators inside the **plugins** folder to execute 7 tasks in a sequence.
4. When all the tasks are executed successfully, it updates the status file with the number of new articles inserted in the postgres SQL database. It is stored inside 2 tables - **news_images, news_metadata**
5. The **send_email_dag** then triggers to send the new inserted articles via email to the user.
6. Overall, the config file contains the config.json file. The dags folder contains the 2 DAGS to be submitted for the assignment. The plugins folder contains all the required custom operators for the pipeline DAG.
