---
title: My Learning Analytics Depersonalizer
layout: default
---

# My Learning Analytics DePersonalizer

## Project Overview
This project was written to depersonalize the [My Learning Analytics](https://github.com/tl-its-umich-edu/my-learning-analytics) (MyLA) Database "in-place". Startup MyLA based on the instructions on that tool and load a course data via the cron. Then configure the .env file here (based on the .env.sample) to populate that data. You will need to supply the ID_ADDITION (which will match the one used in MyLA) as well as a FFX_SECRET which is the password used for some of the encryption routines.

The default mode will not update the database, you need to set the value to UPDATE_DATABASE to be True in this file and it will process all tables (unless changed with the TABLES environment variable). This script runs on the local host and connects into a database and was tested with Python 3.6.6.

## Algorithms used and configuration

All configuration for this project is done in the config.json file. The current structure is a json array defining a table, the columns and the methods with which to depersonalize the data. All methods from [Python Faker](https://faker.readthedocs.io/en/stable/) are available and some additional methods. The columns will run in the order they are defined, as some columns rely on other columns being processed first. The following are the methods used.


### FFX Methods FFX encrypts the source data based on a 16+ character key
* ffx.encrypt
  * [Format Preserving Encryption](https://en.wikipedia.org/wiki/Format-preserving_encryption) referred to as FFX is used on many columns of this data to encrypt things like ID's while making them be able to retain foreign key constraits across tables. 
  * If the value is a string, it will retain the upper, lowercase or mixed case of the original string. The length will remain the same
  * If the value is numeric there may be leading or trailing zeroes dropped in the return value. It will attempt to retain all special characters encoding each part individually.
  * It breaks on special characters so you can have mixed strings, and numeric characters as a value and it will be returned.

### Faker Methods. These generate completely random fake data
* faker.file_name
  * This returns a completely fake file name, currently nothing from the input is retained (such as extension)
  * Return example: `assignment.mp4`
* faker.name
   * This returns a completely fake name (first and last name)
   * Return example: `Adaline Reichel`
* faker.assignment
   * This generates a fake assignment name based on similar named assignments used in Canvas. 
   * Return example: `Practice Assignment #196`
* faker.date_time_on_date
   * This returns a new timestamp which is still on the original date. The columns that use this could be improved via redistribution methods
* faker.user_name
   * This returns a completely random username
   * Return example: `adaline`
* faker.course
   * This returns a fake course id. 
   * Return example: `AUTO 273 007 SP 2026`
  
### Redistribution, calculation methods. These recalculate fields often baesd on other fields
* redist.course_id
   * Grouping by the column (after the period) use [Kernel Density Estimation (KDE)](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gaussian_kde.html) to redistribute all of the numeric values within that course
   * The values should have a similar distribution as the source but will be completely new values
* mean.score__assignment_id
  * Calculate the mean value of the column after the period (in this case score) grouped by the column after __ (in this case assignment_id) and assign this value to all grouped columns

## Screenshots of various views
### Assignments
![Assignments View](assignments.png?raw=true "Assignments")
### Assignments as Student
![Assignments Student View](assignments_student.png?raw=true "Assignments as Student")
### Files
![Files View](files.png?raw=true "Files")
