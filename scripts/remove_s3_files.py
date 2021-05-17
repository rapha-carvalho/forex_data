import boto3


def remove_s3_files():
    """
    """
    AWS_ACCESS_KEY_ID = ""
    AWS_SECRET_ACCESS_KEY = ""

    s3 = boto3.resource('s3',
                      region_name='us-east-1',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    bucket = s3.Bucket('udac-forex-project')
    bucket.objects.filter(Prefix="consolidated_data/").delete()
