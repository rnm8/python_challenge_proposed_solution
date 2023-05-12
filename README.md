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

## Assumptions being made in my solution
- bag does not currently have dimension attributes, as per the context
- however, requirement states "bags of various colors and sizes"
- if required, further attributes can be added to the Bag model
- an input parser function can also be implemented to trigger a user input dialog for the bag attributes, with dimensions such as height, weight & width/depth also being recorded


