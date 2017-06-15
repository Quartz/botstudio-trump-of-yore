import boto3
import json

client = boto3.client('lambda', region_name='us-east-1')

# sample tweet urls
new_tweet_url = "https://twitter.com/realDonaldTrump/status/875438639823675392" 
historic_tweet_url = "https://twitter.com/realDonaldTrump/status/240116141446537216"

# set up a json payload for sending to aws lambda
payload_setup = {}
payload_setup['urls'] = [new_tweet_url, historic_tweet_url]
payload_json = json.dumps(payload_setup)
    #=> {"urls": ["url_for_top_tweet", "url_for_bottom_tweet"]}
    
lambda_response = client.invoke(
    FunctionName='composite-bot',
    InvocationType='RequestResponse',
    Payload=payload_json
    )
    
print(lambda_response['Payload'])