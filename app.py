import boto3
import botocore
import requests
from boto3.session import Session
from chalice import Chalice, Response
import urllib



BUCKET_NAME = "priceworld-photodump"

AWS_ACCESS_KEY = "AKIAI4URWBR7OMSHMWBA"
AWS_SECRET_KEY = "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"
AWS_REGION = "us-east-2"

app = Chalice(app_name='priceworld')
app.debug = True


# Routing #

@app.route('/')
def index():
    s3 = boto3.resource('s3')

    with open('/tmp/hello.txt', 'rb') as data:
        s3.upload_fileobj(data, BUCKET_NAME, 'mykey')
    return {'hello':'world'}


@app.route('/hello/{name}')
def hello_name(name):
   return {'hello': name}



def upload_file(name):
    s3 = boto3.resource(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    urllib.urlretrieve(name, "/tmp/local-filename.jpg")

    f = open('/tmp/local-filename.jpg', 'rb')
    key = "beer.jpg"

    s3.Bucket(BUCKET_NAME).put_object(Key=key, Body=f)


@app.route('/brew/any')
def brewAny():

    r = requests.get("https://api.punkapi.com/v2/beers/random")

    return Response(body=prettyPrintData(r.json()[0]),
                    status_code=200,
                    headers={'Content-Type': 'text/plain'})

@app.route('/brew/id/{id}')
def brewId(id):

    r = requests.get("https://api.punkapi.com/v2/beers/" + str(id))

    return Response(body=prettyPrintData(r.json()[0]),
                    status_code=200,
                    headers={'Content-Type': 'text/plain'})


@app.route('/brew/name/{beer_name}')
def brewName(beer_name):

    r = requests.get("https://api.punkapi.com/v2/beers/?beer_name=" + str(beer_name))

    return Response(body=prettyPrintData(r.json()[0]),
                    status_code=200,
                    headers={'Content-Type': 'text/plain'})

@app.route('/brew/stronger/{than}')
def brewStrong(than):
    r = requests.get("https://api.punkapi.com/v2/beers/?abv_gt=" + than)

    return Response(body=prettyPrintData(r.json()[0]),
                    status_code=200,
                    headers={'Content-Type': 'text/plain'})


# JSON formatting functions #

def beerVerbose(json):
    name = json['name']
    since = json['first_brewed']
    tag = json['tagline']
    description = json['description']
    desc = "{} ({}): '{}' \n\n {}".format(name, since, tag, description)
    return desc

def productionDetails(json):
    header = "\nThese instructions produce {} {} of beer with the following specifications:\n".\
                                    format(json["volume"]["value"],json["volume"]["unit"])
    body = "\tABV: {}\n\tIBU: {}\n\tTarget FG: {}\n\tTarget OG: {}" \
          "\n\tEBC: {}\n\tSRM: {}\n\tPH: {}\n\tAttenuation Level: {}".\
        format(json['abv'], json['ibu'], json['target_fg'], json['target_og'], json['ebc'],
               json['srm'], json['ph'], json['attenuation_level'])

    production_details = "{} \n {}".format(header,body)
    return production_details

def ingredients(json):
    body = ""
    ingredients = json["ingredients"]
    ingredient_strings = []
    body += "\n\t\tHops:\n"
    for i in ingredients["hops"]:
        amount = i["amount"]
        body += "\n\t\tAdd {} {} of {} ({}) at {}".format(str(amount['value']), amount['unit'],
                                                 i['name'],i['attribute'],i['add'])

    body += "\n\n\t\tMalt:\n"
    for i in ingredients["malt"]:
        amount = i["amount"]
        body += "\n\t\tUse {} {} of {}".format(str(amount['value']),amount['unit'],i['name'])

    body += "\n\n\t\tYeast:\n\n\t\t" + ingredients["yeast"]

    return body

def cookingTemps(json):
    method = json["method"]
    mash_temp = str(method["mash_temp"][0]["temp"]["value"]) + \
                    " " + method["mash_temp"][0]["temp"]["unit"]
    fermentation_temp = str(method["fermentation"]["temp"]["value"]) + \
                " " + method["fermentation"]["temp"]["unit"]
    twist = method['twist']
    body = "\n\t\tMash Temperature: {}\n" \
           "\t\tFermentation Temperature: {}\n" \
           "\t\tAny twists?: {}".format(mash_temp, fermentation_temp, twist)

    return body

def additionalInfo(json):
    body =""
    body += "\n\t\tBrewers Tip:\n\n\t\t{}\n".format(str(json["brewers_tips"]))
    body += "\n\t\tFood Pairing: \n\t\t"
    for i in json['food_pairing']:
        body += "\n\t\t" + i

    body += "\n\nContributed by {}".format(json['contributed_by'])
    return body


def prettyPrintData(json):
    header = beerVerbose(json)
    production_details = productionDetails(json)
    ingredient_list = ingredients(json)
    brewing = cookingTemps(json)
    additional_info = additionalInfo(json)
    upload_file(json['image_url'])
    page_link = "See your beer at http://priceworld-photodump.s3-website.us-east-2.amazonaws.com/"

    console_buffer = "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
    formattedString = "{}" \
             "{}\n" \
             "{}\n" \
             "\nBrewing Instructions:\n" \
             "\n\tIngredients:\n" \
             "{}\n" \
             "\n" \
             "\tBrewing Temps:\n"\
             "{}\n"\
             "\n\tExtra brewing info:\n"\
             "{}"\
             "{}\n" \
             "{}\n".format(console_buffer, header, production_details,
                        ingredient_list,brewing, additional_info, console_buffer,
                         page_link)

    return formattedString