import boto3

def create_waf_webacl(webacl_name, metric_name, rule_name, priority, action_type, block_action_rule_name):
    waf_client = boto3.client('waf-regional')

    # Get the latest ChangeToken
    response = waf_client.get_change_token()
    change_token = response['ChangeToken']

    # Create a WebACL
    response = waf_client.create_web_acl(
        Name=webacl_name,
        MetricName=metric_name,
        DefaultAction={
            'Type': action_type
        },
        ChangeToken=change_token
    )
    webacl_id = response['WebACL']['WebACLId']

    # Create a Rule
    response = waf_client.create_rule(
        Name=rule_name,
        MetricName=metric_name,
        ChangeToken=change_token
    )
    rule_id = response['Rule']['RuleId']

    # Update the Rule with Predicates
    response = waf_client.update_rule(
        RuleId=rule_id,
        Predicates=[
            {
                'DataId': '1',
                'Negated': False,
                'Type': 'IPMatch'
            }
        ],
        ChangeToken=change_token
    )

    # Create an Action for the Rule
    response = waf_client.create_web_acl(
        Name=webacl_name,
        MetricName=metric_name,
        DefaultAction={
            'Type': action_type
        },
        Rules=[
            {
                'Action': {
                    'Type': action_type
                },
                'Priority': priority,
                'RuleId': rule_id,
                'Type': 'REGULAR'
            },
        ],
        ChangeToken=change_token
    )

    # Associate the WebACL with CloudFront Distribution
    cloudfront_client = boto3.client('cloudfront')
    distribution_id = 'E4DNX18KSH64T'
    waf_association = {
        'WebACLId': webacl_id,
        'ResourceArn': f'arn:aws:cloudfront::{distribution_id}',
        'ChangeToken': change_token
    }
    cloudfront_client.create_web_acl_association(WebACLId=waf_association['WebACLId'], ResourceArn=waf_association['ResourceArn'], ChangeToken=waf_association['ChangeToken'])

    print(f"AWS WAF WebACL created with ID: {webacl_id} and associated with CloudFront Distribution.")

# Example usage:
webacl_name = 'YourWebACLName'
metric_name = 'YourMetricName'
rule_name = 'YourRuleName'
priority = 1
action_type = 'BLOCK'
block_action_rule_name = 'BlockActionRuleName'

create_waf_webacl(webacl_name, metric_name, rule_name, priority, action_type, block_action_rule_name)
