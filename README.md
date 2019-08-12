# myla-depersonalizer
Test code to depersonalize database (MyLA)

See more information about this project on the Github Pages:
http://tl.ctools.org/myla-depersonalizer/

To use on your own project:

Develop a config.json file that's specific to your project. Look at the example of our database here.
- This json file is organized by table name and every column in the table that you'd want to run some method on. 
- Every column should be represented
- Not all methods are available for all column types. For example ffx.encrypt needs integers or strings. 

Note in the config.json there's a slightly special syntax to allow for table joining. Look at the example of 
`assignment@id|submission@id`

There it's joining the assignment and submission tables (with a primary key's id on each) together on the `where` clause. It creates a large dataframe and does all of the tranformations on this large table. Afterwards it writes all of the tables back. There may still be a few issues with this process.

Edit the .env.sample file to provide your 
- MYSQL credentials
- ID_ADDITION (if you have one) which is a prefix preserved on your integer ids
- FFX_SECRET which should be a sufficiently complex secret password
- FAKER_SEED_LENGTH which should be a long enough seed for faker

The other variables here are for testing. 
- You can specify TABLES to only test specific tables
- UPDATE_DATABASE to actually update the database
- DISABLE_FOREIGN_KEYS to disable keys which may be necessary to perform some updates

Then the main file to run (with python) is `mylasqlanon.py`
