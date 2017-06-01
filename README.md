Publishing service used to find new beers to brew. 

Templates contains index and error html's used in amazon s3 static site (http://priceworld-photodump.s3-website.us-east-2.amazonaws.com/)

routes are hosted on https://at6jw2dyo8.execute-api.us-east-2.amazonaws.com:

suffixes:

/brew/any:

	returns brewing instructions on a random beer

/brew/id/{id}:

	returns brewing instructions for a specific beer, by id

/brew/name/{name}:

	returns brewing instructions for a specific beer, by name

/brew/stronger/{than}:

	returns brewing instructions for a beer with an ABV greater than "than" variable


I addressed all the goals of the challenge in a single API call rather than 3. Each call transforms the information available from punk API into human readable brewable instructions. Each beer's json also includes an image link, which is downloaded to a /tmp/ file and then uploaded to an S3 bucket (http://priceworld-photodump.s3-website.us-east-2.amazonaws.com/). Each call includes a simple status code to let the user know the call was completed fine, and returns as the response the brewing instructions.

The app.py contains the routes and the json formatting. teh various functions included take a json object, grabbed from punkapi, and uses the info in it to format several strings, which detail ingredients in the beer, different brewing instructions, notes from the brewer, and some basic final product information (abv, ph, etc.) The prettyPrint function uses the various smaller functions to format each of these details, and then properly format each section. 

Using only 1 api to complete all 3 goals made the msot sense, since each json actually already includes a picture of the beer. Of course there are a few different calls, since the punkapi provides some fun query options to play with, like searching by beer strngth (ABV), but the general idea is one call whihc uploads a picture to my S3 bucket, which also acts as a static web site, formats and returns the punkapi json, and returns status for success and failure.


