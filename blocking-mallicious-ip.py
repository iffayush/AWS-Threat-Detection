import boto3
import json

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    try:
        ip = event['detail']['service']['action']['networkConnectionAction']['remoteIpDetails']['ipAddressV4']
    except KeyError:
        print("No IP found in event.")
        return {"statusCode": 400, "body": "No IP in event."}

    sg_id = "sg-xxxxxxxx"

    try:
        ec2.revoke_security_group_ingress(
            GroupId=sg_id,
            IpProtocol='-1',
            CidrIp=f"{ip}/32"
        )
    except Exception as e:
        print(f"IP {ip} not present in SG, adding fresh rule.")

    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                'IpProtocol': '-1',
                'IpRanges': [
                    {
                        'CidrIp': f"{ip}/32",
                        'Description': 'Blocked by Lambda (GuardDuty AutoResponse)'
                    }
                ]
            }
        ]
    )

    print(f"Blocked IP {ip} successfully")
    return {"statusCode": 200, "body": f"Blocked IP {ip}"}
