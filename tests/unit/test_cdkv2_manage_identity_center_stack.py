import aws_cdk as core
import aws_cdk.assertions as assertions

from cdkv2_manage_identity_center.cdkv2_manage_identity_center_stack import Cdkv2ManageIdentityCenterStack

# example tests. To run these tests, uncomment this file along with the example
# resource in src/cdkv2_manage_identity_center_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = Cdkv2ManageIdentityCenterStack(app, "cdkv2-manage-identity-center")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
