#Created by Sridhar Gundumalla
#700734079

import boto3
from datetime import datetime

def create_cloudfront_distribution(s3_bucket_name,distribution_comment='srivisual'):
    cloudfront_client = boto3.client('cloudfront')
   
    existing_distributions = cloudfront_client.list_distributions()['DistributionList']['Items']
    existing_distribution = next((dist for dist in existing_distributions if dist.get('Comment') == distribution_comment), None)
    
    if existing_distribution:
        print(f"CloudFront Distribution with comment '{distribution_comment}' already exists. Distribution ID: {existing_distribution['Id']}")
        return existing_distribution['DomainName']

    # Using a timestamp as the CallerReference
    caller_reference = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    distribution_config = {
        'CallerReference': caller_reference,
        'Comment': 'srivisual',
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': 'S3Origin',
                    'DomainName': f"{s3_bucket_name}.s3.amazonaws.com",
                    'S3OriginConfig': {
                        'OriginAccessIdentity': ''
                    }
                },
            ]
        },
        'DefaultCacheBehavior': {
            'TargetOriginId': 'S3Origin',
            'ForwardedValues': {
                'QueryString': False,
                'Cookies': {
                    'Forward': 'none'
                }
            },
            'TrustedSigners': {
                'Enabled': False,
                'Quantity': 0
            },
            'ViewerProtocolPolicy': 'allow-all',
            'MinTTL': 0
        },
        'DefaultRootObject': '',
        'PriceClass': 'PriceClass_All',
        'Enabled': True,
    }

    response = cloudfront_client.create_distribution(DistributionConfig=distribution_config)

    distribution_id = response['Distribution']['Id']
    distribution_domain = response['Distribution']['DomainName']

    print(f"CloudFront Distribution created. Distribution ID: {distribution_id}, Domain: {distribution_domain}")

    return distribution_domain

