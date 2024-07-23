import json
import boto3
import random


def lambda_handler(event, context):
    print("RECEIVED event: ", json.dumps(event, indent=2))

    if event['triggerSource'] == 'CreateAuthChallenge_Authentication':
        handle_create_auth_challenge(event)
    elif event['triggerSource'] == 'DefineAuthChallenge_Authentication':
        handle_define_auth_challenge(event)
    elif event['triggerSource'] == 'VerifyAuthChallengeResponse_Authentication':
        handle_verify_auth_challenge(event)

    print("RETURNED event: ", json.dumps(event, indent=2))
    return event


def handle_create_auth_challenge(event):
    phone_number = event['request']['userAttributes'].get('phone_number')

    # Generate a new passcode if the session is new or the previous challenge was SRP_A
    if (not event['request']['session'] or
            (event['request']['session'] and event['request']['session'][-1]['challengeName'] == 'SRP_A') or
            len(event['request']['session']) == 0):

        pass_code = random.randint(100000, 999999)  # 6 digits passcode generation
        send_sms(phone_number, pass_code)
    else:
        previous_challenge = event['request']['session'][-1]
        pass_code = previous_challenge['challengeMetadata'].split('-')[1]

    event['response']['publicChallengeParameters'] = {
        'phone': phone_number,
    }
    event['response']['privateChallengeParameters'] = {
        'passCode': pass_code
    }
    event['response']['challengeMetadata'] = f'CODE-{pass_code}'


def handle_define_auth_challenge(event):
    if event['request'].get('userNotFound', False):
        print('User does not exist')
        event['response']['issueTokens'] = False
        event['response']['failAuthentication'] = True
        raise Exception('User does not exist')

    if (event['request']['session'] and
            len(event['request']['session']) and
            event['request']['session'][-1]['challengeName'] == 'SRP_A'):
        event['request']['session'] = []
        event['response']['issueTokens'] = False
        event['response']['failAuthentication'] = False
        event['response']['challengeName'] = 'CUSTOM_CHALLENGE'
    elif (event['request']['session'] and
          len(event['request']['session']) and
          event['request']['session'][-1]['challengeName'] == 'CUSTOM_CHALLENGE' and
          event['request']['session'][-1]['challengeResult']):
        print('The user provided the right answer to the challenge')
        event['response']['issueTokens'] = True
        event['response']['failAuthentication'] = False
    elif (event['request']['session'] and
          len(event['request']['session']) >= 3 and
          not event['request']['session'][-1]['challengeResult']):
        print('FAILED Authentication: The user provided a wrong answer 3 times')
        event['response']['issueTokens'] = False
        event['response']['failAuthentication'] = True
        raise Exception('Invalid OTP')
    else:
        event['response']['issueTokens'] = False
        event['response']['failAuthentication'] = False
        event['response']['challengeName'] = 'CUSTOM_CHALLENGE'


def handle_verify_auth_challenge(event):
    expected_answer = event['request']['privateChallengeParameters'].get('passCode')

    if event['request']['challengeAnswer'] == expected_answer:
        event['response']['answerCorrect'] = True
    else:
        event['response']['answerCorrect'] = False


def send_sms(phone_number, pass_code):
    sns = boto3.client('sns')
    message = f'Your secret code: {pass_code}'
    response = sns.publish(
        PhoneNumber=phone_number,
        Message=message,
    )
    print(f'SMS sent to {phone_number}, response: {response}')
