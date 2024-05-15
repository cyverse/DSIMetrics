<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://datascience.arizona.edu/">
    <img src="images/logo.png" alt="Logo">
  </a>

  <h1 align="center">Data Science Institute Metrics System</h1>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#software-architecture">Software Architecture</a></li>
    <ul>
        <li><a href="#system-overview">System Overview</a></li>
        <li><a href="#database-schema">Database Schema</a></li>
    </ul>
    <li><a href="#dsi-metrics-how-to">DSI Metrics How-To</a></li>
      <ul>
        <li><a href="#first-time-access">First Time Access</a></li>
        <li><a href="#accessing-metrics">Accessing Metrics</a></li>
        <li><a href="#exporting-recontact-list">Exporting Recontact List</a></li>
        <li><a href="#series-walkthrough">Series Walkthrough</a></li>
        <ul>
          <li><a href="#adding-a-series">Adding A Series</a></li>
          <li><a href="#modifying-a-series">Modifying A Series</a></li>
          <li><a href="#deleting-a-series">Deleting A Series</a></li>
        </ul>
        <li><a href="#workshops-walkthrough">Workshops Walkthrough</a></li>
        <ul>
          <li><a href="#adding-a-workshop">Adding A Workshop</a></li>
          <li><a href="#modifying-a-workshop">Modifying A Workshop</a></li>
          <li><a href="#deleting-a-workshop">Deleting A Workshop</a></li>
        </ul>
        <li><a href="#users-walkthrough">Users Walkthrough</a></li>
        <ul>
          <li><a href="#adding-a-new-user">Adding A New User</a></li>
          <li><a href="#deleting-a-user">Deleting A User</a></li>
          <li><a href="#authorizing-a-new-zoom-user">Authorizing a New Zoom User</a></li>
        </ul>
      </ul>
    <li><a href="#repository-breakdown">Repository Breakdown</a></li>
    <li><a href="#system-restart">System Restart</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project
The Data Science Institute (DSI) Metrics System is an end-to-end solution for streamlining data collection and workshop management. It automatically fetches registration data from Qualtrics and attendance information from Zoom, cleans and processes the data, and uploads it to a Postgres database. The system offers front-end CRUD and visualization tools hosted using Budibase, allowing authorized users to interact directly with the database. The system is hosted on a virtual machine on the [Cyverse](https://cyverse.org/) network. Access to the system is restricted to authorized users due to University and FERPA regulations.
### Quick Links
* [DSI Metrics System](dsi-metrics.cyverse.org)
* [Zoom API authorization](cerberus.cyverse.org)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Software Architecture
### System Overview
<a href="https://datascience.arizona.edu/">
  <img src="images/DSI Metrics Software Architecture.png" alt="Logo">
</a>

### Database Schema
<a href="https://datascience.arizona.edu/">
  <img src="images/DSI Metrics DB Schema.png" alt="Logo">
</a>

## DSI Metrics How-To
### First Time Access
To access the data visualizations available to authorized users, click on the *DSI Metrics System* link in the quick links above. Before you are able to log in, the admin must add your email to the system, generate a random password for you, and give you access to the app as discussed later. When prompted fill out the login with the temporary password. The system will then prompt you to change your password. Ensure to remember your password as this is the one you will use every time you log into the system.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/3300a9af-67fa-47c0-991b-d05551d173d3)

Once your password is reset, you will once more be prompted to log in using your new password. When you click login, you will be prompted to choose the app you want to access. Select DSI Metrics.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/98b42586-6b17-4a6d-a317-678c4782823a)

### Accessing Metrics
After you click on the app you will be brought to the Metrics Page. On this page, you can select a semester and a year to get attendance information for the selected semester. The first box includes 3 graphs. The first is attendance over time for all workshops in that semester. The second is the total attendance and unique attendance for each workshop in that semester. The unique attendance is for each person who attended a workshop. If someone went to 3 weeks of workshops, they are counted 3 times in the total attendance but not the unique attendance. The final graph is a bar chart for registration information for the semester. The graph breaks down registration into people we were able to identify, not identify, those who registered, those who never attended, etc.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/3be5dcdf-20d4-4deb-9446-9099f9a07dd4)

If you scroll down you will find another drop down. This menu lets you select any workshop and will display the attendance over time and the workshop names/topics for each week.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/6850530b-dce5-4516-8520-0e6a1aca3154)

### Exporting Recontact List
This feature is only available on Chrome browsers due to javascript compatibility issues. At the top of the page, if you click 'Export Recontact Contact List' it will bring you to a table of every person who has listed they want to be recontacted on the registration form. By default, if they attend but never register, they are not considered for recontact. Once on this page, the system will automatically download a CSV file containing all of their emails for easy use.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/b00e93de-7ac9-4d48-807b-e65db969e498)

### Series Walkthrough
Definitions: In this software Series are the overarching collection of workshops. Every workshop will be associated with a series, with the ability for multiple workshops to be connected to one series. Having series' allows us to create one-off workshops, or a weekly workshop all a part of a series. Creating a series is the first step for any new workshop, regardless of the number of workshops occurring.

:warning: IMPORTANT PREREQUISITES: BEFORE ANY SERIES CAN BE CREATED THERE MUST BE A QUALTRICS FORM ALREADY CREATED, A ZOOM MEETING ID ASSOCIATED WITH IT, AND A CALANDER PAGE SETUP ON THE DSI WEBSITE. IF NO CALANDER EVENT HAS BEEN CREATED THE WORKSHOPS' WILL NOT BE AUTOMATICALLY CREATED AND YOU WILL HAVE TO MANUALLY ENTER THEM. ANY OF THIS INFORMATION CAN BE CHANGED AT ANY TIME IF NECESSARY.

On the navigation bar click 'Series'. The link will bring you to a page containing a form to create, modify, or delete a series, as well as a table to view all series currently in the system.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/02161c42-c194-4c91-9216-350290bff0b0)

#### Adding A Series
To add a series you will need to fill out the corresponding information on the form
* SeriesID - Ignore, this is automatically generated
* SeriesName - The name that will be displayed on all tables. Must match the Qualtrics name
* Zoom Meeting ID - The meeting ID associated with the meeting
* QualtricsID - The Qualtrics survey ID can be found in the edit link for the survey. For example in this link 'https://uarizona.co1.qualtrics.com/survey-builder/SV_d0aMpul3tB1wJ1Q/edit', the surveyID is SV_d0aMpul3tB1wJ1Q
* SeriesURL - The calendar event for the series, for example, 'https://datascience.arizona.edu/events/navigating-world-data-engineering'
* Start Time - The start time of the workshops in the series. If the workshops do not start at the same time they cannot be a part of the series. Select the appropriate AM or PM time and the system will display it in 24 hour time, that's okay.
* End Time - The end time of the workshop, the same rules apply as the start time
* Start Date - The day of the first workshop in the series
* End Date - The day the last workshop in the series occurs
* Semester - Choose between Spring, Summer, Fall, and Winter
* SeriesYear - The year the workshop series is taking place

Once all of the above information has been entered, select 'Save' and the Series will be added to the database. You should be able to see the new entry in the table below the form.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/2d87b3b3-e9c3-4f08-8f5a-a90c12d2b044)

#### Modifying A Series
To modify a series, first go to the table at the bottom and find the SeriesID for the series you wish to modify. Next, enter the SeriesID to the form, this will automatically populate the form except for the start and end time which you will have to enter manually. Finally, once your modifications are complete, click 'Update'. To verify go to the table at the bottom and the changes should be present.

#### Deleting A Series
If you need to remove a series from the database you can easily do so by first going to the table at the bottom and finding the SeriesID for the series you wish to delete. Next, enter the SeriesID into the form. Finally, click 'Delete Series'. You should be able to see the changes reflected in the table.

### Workshops Walkthrough
Definitions: Workshops are the actual events people will be attending, registering, and getting checked in for. The workshops contain the workshop name, id, and date, and will always be associated with a series. The workshops' time information will be stored in the series. Workshops can be created automatically by inserting a series URL when the series is created in Budibase, which will web scrape the 'When' section of the page and create a workshop for every date present. If the URL is not provided or fails, workshops can be entered manually through the 'Workshops' page on Budibase.

:warning: WARNING: IF ANY OF THE WORKSHOPS ARE DELETED IT WILL ALSO DELETE THE ACCOMPANYING CHECK-IN AND REGISTRATION DATA FOR THE WORKSHOP. MODIFY WORKSHOPS CAREFULLY TO ENSURE NO DATA LOSS.

#### Adding A Workshop
1. First travel to the workshops page using the navigation bar at the top of the app.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/48959515-6b19-423e-a8b9-2dada97f440e)

2. Next click the "+" in the top left corner of the table. This will let you interact directly with the table without the need for a form.
3. Enter the seriesID, workshop name, and workshop date.
4. If you do not know the seriesID, navigate to the series page, scroll to the table at the bottom, and click on the column header for series name. Here you can search for a workshop by name and find its associated ID on the left.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/b31d6d71-76bf-45d8-963d-496386bbcba0)

5. Click the "Save" button to save the workshop into the database.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/998ed150-dcc0-4dfd-a251-2533e56e2ffb)


#### Modifying A Workshop
1. Travel to the workshops page using the navigation bar at the top of the app as described in step 1 of [Adding A Workshop](adding-a-workshop).
2. Find the data item you wish to modify by scrolling through the table or clicking on a column header to search for a specific value.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/1d33f91c-8dca-4347-9151-fb2a96bf119e)

3. Double-click on the cell of the table you wish to modify Note: You cannot modify the workshopID.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/1eac7771-db7f-47c6-97c0-8e9fda71fa41)

4. Modify the contents of the cell as you wish and when done just click away from the table or navigate to a new tab and the information will automatically be updated.

#### Deleting A Workshop
1. Navigate to the workshops page using the navigation bar at the top of the app as described in step 1 of [Adding A Workshop](adding-a-workshop).
2. Find the data item you wish to modify by scrolling through the table or clicking on a column header to search for a specific value.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/1d33f91c-8dca-4347-9151-fb2a96bf119e)

3. On the left side of the table select the checkbox of the item(s) you wish to delete and click the trash icon. ⚠️ THE ITEM WILL PERMANENTLY BE DELETED AND ALL REGISTRATION AND CHECK-IN DATA WITH IT.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/15f3b06d-3046-4491-a899-e46d119fc08e)

### Users Walkthrough
#### Adding A New User
1. As an admin, traversing to the metrics website will take you to the following page:
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/5a0ce7c7-90c5-470f-a003-440ff2b1b347)

3. On this page select the users tab in the top left.
4. On the users page click 'Add users'.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/c7984a9d-c089-489b-a16d-731e0182bdf7)

5. Enter the email for the user you wish to add. You can add multiple by clicking '+ Add email'.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/254ae6ad-3e84-4fab-bb5f-99b78bbaa1e0)

6. For each user, select the appropriate access level. Currently, all pages can be accessed by basic users.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/6e412dd1-c7d1-41f4-8cec-507518a8fe73)

7. Once all emails have been added click the blue 'Add users' button.
8. On the onboarding page select 'Generate passwords for each user.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/368ece87-5432-41a7-b4fb-49154648c48a)

9. Distribute the passwords either by copying them or downloading the CSV.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/86431f39-b557-4aeb-b15b-290ca405e44b)

10. Next navigate back to the apps page and select 'DSI Metrics'.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/f30de6e1-e2fa-4512-83b6-5748f8bbda2f)

11. In the top right select 'Users'. If you click the dropdown for each email, you can change their permissions for the DSI Metrics App. You need to select at least "Can use as Basic" for the user to be able to use the app.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/3b1ce3d3-447e-4702-bb2b-c98a6a491bdc)

12. The user is all set to access the DSI Metrics App.
    
#### Deleting A User
1. To remove a user, navigate to the 'Users' page as an admin.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/02e997a4-7911-477c-b4a4-182e70d8aea4)

3. Select the user using the checkbox on the left of the table and on the top right of the table click 'Delete User'.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/8916e7d9-b928-42cf-9607-4c8092ad3723)

4. Confirm the deletion by clicking 'Delete' in the popup window and the user will be deleted from the system, and no longer have access to the DSI Metrics website.

#### Authorizing a New Zoom User
1. While logged into UofA Wifi or the UofA VPN navigate to [Zoom OAUTH](https://cerberus.cyverse.org)
2. Click on the button to allow OAuth

&emsp;&emsp;![image](https://github.com/cyverse/DSIMetrics/assets/146140831/9894f178-6540-4583-91c3-eea86b88ec6b)

3. This button will redirect you to the Zoom website where you will need to authorize the system to access your Zoom information.
4. Sign into your Zoom account as normal and click 'Allow'.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/ac818663-38c6-44a6-b64a-c0e7add6a328)

6. Once you have clicked allow, you will be redirected to a page that will allow you to enter the Zoom Meeting IDs that you have access to, and wish for the software to be able to fetch participants from. These should be the Zoom meeting IDs for series that have already been created.
![image](https://github.com/cyverse/DSIMetrics/assets/146140831/62cc53e7-41c1-4456-bc21-3c65e0523c1a)

8. You can enter as many meeting IDs as you wish. Enter them one at a time and click 'Submit' after each.
9. Once done, exit the page and the keys for each meeting ID will be saved into the database.

## Repository Breakdown

The repo consists of 7 main folders:
* **budibaseDocker** - Holds the docker image for Budibase along with all other supporting files for Budibase to function
* **initialUploads** - Single run scripts used to reinitialize the database with data manually grabbed from Spring 2024
* **postgreSQLScripts** - Used in initial uploads to create functions used in the system and create the tables used in the database. Also includes common queries used in Budibase visualizations
* **productionScripts** - Scripts that are automatically run by Cron Jobs on Linux. These scripts are responsible for the main automation of the system including fetching qualities and zoom data and listening from new series to be entered through Budibase
* **readMeImages** - The images used in this README
* **unitTesting** - Initial testing and exploration code when first creating this system. Kept in the repo for future developers to use as a reference
* **zoomApp** - Holds the files for a Flask app which allows a user to authorize the system to access their Zoom meeting information and then prompts the user to enter the Zoom meeting IDs they wish the system to access

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- System Restart -->
## System Restart
If there are any issues accessing the Zoom App or the DSI Metrics page, perform the following steps to relaunch the software:
1. SSH into cyverse vm
2. The following command will stop all python processes
   ```bash
   pkill python
   ```
3. Next stop the docker container running Budibase
   ```bash
   cd budibaseDocker
   docker compose down
   ```
4. Restart the budibase docker image
   ```bash
   docker compose up
   ```
5. Return to the root directory for the project and start up the Zoom app and Postgres listener
   ```bash
   cd ../
   python productionScripts/seriesListener.py &
   python zoomApp/zoomOAUTH.py
   ```
6. Ensure you are on the UofA Wifi or VPN before attempting to access
