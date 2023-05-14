# Python Challenge
## Tasks
1. Read through the existing code and try to understand it
2. Implement the following Requirement by reusing patterns and code from the existing code
## Requirement
### Context
- a bag has the following attributes:
  - id
  - color
  - weight in grams
### Given
- bags of various colors and sizes
### When
- a user submits bag data
### Then
- the bag data (as defined in context) is saved to DynamoDB

## Hints
- please prepare to walk through your code
- we want to be able to verify your code works
- your code will run in a lambda function that is triggered by an API gateway (just like the getBookings example)

## Explanation on Solution
- BRANCH bag_solution_clean (has been set as the default branch now) is the final cleaned version, minus the renamed and duplicated folders. The successful insertion of data is using boto3 instead of pynamodb. After creating the Bag Model Class to define the attributes, I created both a test request and expected response JSON for bag, similar to the booking example, with the bag data to be inserted placed in the init_data.json. Test function is reusing the same pattern as the other tests, with the references changed to simulate the successful insertion of the bag data into DynamoDB.

- BRANCH bag_solution is my 2nd approach where I renamed duplicated the divaBLPGetBookings to rename the classes, functions & other references to test whether my test function could succesfully seed the mock DB as I was experiencing a number of errors with the tests and my IDE extensions. However, this approach resulted in a confusing folder structure. I tested this succesfully on my desktop, as my workstation IDE can no longer run the unit tests without crashing; I am unsure of what is causing this currently. 

- BRANCH main is my 1st approach for the solution where I initally overthought the requirements and expected solution, whereby the bags data should be inserted in a semi-realistic manner, where a given bag would be tied to a specific booking, and would exist as a key in a booking object. However, I encountered a number of errors as mentioned above, and re-read the requirements, so I decided to scrap my solution and quickly retest whether I could succesfully seed the mock DB with a basic bag object, as stated in the requirements.