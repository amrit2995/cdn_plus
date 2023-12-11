import boto3
import random
import string
from vendors.vendor import VendorInterface

class Cloudfront(VendorInterface):
    def __init__ (self, aws_access_key, aws_secret_access_key, aws_region):
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_access_key
        self.aws_region = aws_region

    def create_boto3_client(self):
        client_object = boto3.client(
            'cloudfront',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
            )
        return client_object
    
    def create_distribution(self, origin_source=None, origin_name=None, origin_domain=None, **config_payload):
        """
        Creates a CloudFront Distribution with specified parameters.
        Args:
            ** Mandatory **
            origin_source (str) : Origin source [s3, custom, etc]
            origin_name (str) : Name for the Origin
            origin_domain (str) : Domain assigned with the origin
        Returns:
            create_flag (bool) : Create Flag (True)
            new_distribution_config (dict) : New Distribution Configuration
        Raises:
            create_flag (bool) : Create Flag (False)
            Client error message (str) : Client Error Message
        """
        allowed_http_methods = [method.upper() for method in config_payload.get("allowed_http_methods", ['GET', 'HEAD'])]
        supported_http_versions = [version.lower() for version in config_payload.get("supported_http_versions", ["HTTP2", "HTTP3"])]
        cdn_price_class = config_payload.get("price_class","PriceClass_All")
        distribution_config = {
            'CallerReference': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(14)),
            'Comment': f'CDN Creation for {str(origin_domain)}',
            'DefaultCacheBehavior': {
                'TargetOriginId': str(origin_name),
                'TrustedSigners': {'Enabled': False,'Quantity': 0},
                'ViewerProtocolPolicy': 'redirect-to-https',
                'AllowedMethods': {
                    'Quantity': len(allowed_http_methods),
                    'Items': allowed_http_methods,
                    'CachedMethods': {'Quantity': 2, 'Items': ['GET', 'HEAD']},
                }
            },   
            'Enabled': True,             
            'Origins': {
                'Quantity': 1,
                'Items': [
                    {
                        'DomainName': str(origin_domain),
                        'Id': str(origin_name)
                    }
                ],
            },       
            'PriceClass': cdn_price_class,
            # Defaults to the first supported HTTP version        
            'HttpVersion': supported_http_versions[0],                
            'ViewerCertificate': {'CloudFrontDefaultCertificate': True}
        }
        # Origin Source
        if str(origin_source).lower() == "s3":
            for origin_item in distribution_config["Origins"]["Items"]:
                origin_item['S3OriginConfig'] = {
                    'OriginAccessIdentity': ''
                    }
        else:
            for origin_item in distribution_config["Origins"]["Items"]:
                origin_item["CustomOriginConfig"] = {
                    'HTTPPort': 80, 
                    'HTTPSPort': 443, 
                    'OriginProtocolPolicy': 'https-only'
                    }  
        # Cache Policy 
        if config_payload.get("cache_policy"):
            cache_policy = config_payload.get("cache_policy")
            cache_policy_id_map = {
                "CachingOptimized":"658327ea-f89d-4fab-a63d-7e88639e58f6",
                "CachingDisabled":"4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
                "CachingOptimizedForUncompressedObjects":"b2884449-e4de-46a7-ac36-70bc7f1ddd6d",
                "Elemental-MediaPackage":"08627262-05a9-4f76-9ded-b50ca2e3a84f",
                "Amplify":"2e54312d-136d-493c-8eb9-b001f22f67d2"
                }
            distribution_config["DefaultCacheBehavior"]["CachePolicyId"] = cache_policy_id_map[str(cache_policy)]
        else:
            distribution_config["DefaultCacheBehavior"]["DefaultTTL"] = config_payload.get("default_ttl",3600)
            distribution_config["DefaultCacheBehavior"]["MinTTL"] = config_payload.get("min_ttl",60)
            distribution_config["DefaultCacheBehavior"]["MaxTTL"] = config_payload.get("max_ttl",86400)
            distribution_config["DefaultCacheBehavior"]["ForwardedValues"] = {
                'Cookies': {'Forward': 'none'},
                'Headers': {'Quantity': 0},
                'QueryString': False,
                'QueryStringCacheKeys': {'Quantity': 0}
                }        
     
        boto_client = self.create_boto3_client()
        try:
            client_response = boto_client.create_distribution(DistributionConfig=distribution_config)
            return True, client_response
        except Exception as sdk_error_msg:
            return False, sdk_error_msg
                
    def get_distributionId_by_domain(self, domain_name=None):
        """
        Fetches Distribution Id from Edge-location Domain Name.
        Args:
            ** Mandatory **
            domain_name (str) : Cache-server/edge-location domain name
        Returns:
            Fetch_Flag (Bool) : Fetch Status (True)
            distribution_id (str) : Distribution Id
        Raises:
            Fetch_Flag (Bool) : Fetch Status (False)
            error_msg (str) : Error message
        """        
        boto_client = self.create_boto3_client()
        try:
            response = boto_client.list_distributions()
            distributions = response.get('DistributionList', {}).get('Items', [])
            for distribution in distributions:
                if distribution['DomainName'] == str(domain_name):
                    return True, distribution['Id']
            return False, f"Failed to find distribution Id for the domain {str(domain_name)}"
        except Exception as sdk_error_msg:
            return False, sdk_error_msg
        
    def fetch_all_distributions(self):
        """
        Fetches All Available CloudFront Distributions.
        Returns:
            Distribution List (list of dicts) : Distribution Configuration List
        """                
        boto_client = self.create_boto3_client()
        distribution_response = boto_client.list_distributions()
        distribution_list = distribution_response['DistributionList']['Items']
        return distribution_list

    def fetch_distribution_details_by_domain(self, domain_name=None):
        """
        Fetches Distribution Details from Edge-location Domain Name.
        Args:
            ** Mandatory **
            domain_name (str) : Cache-server/edge-location domain name
        Returns:
            Distribution Detail dict (dict) : Distribution Details
        """            
        distribution_list = self.fetch_all_distributions()
        distribution_details = {}
        if distribution_list:
            for distribution in distribution_list:
                if distribution["DomainName"] == domain_name:
                    distribution_details = distribution
        else:
            print("No Distribution Onboarded.")
        return distribution_details    
                        
    def enable_distribution_by_domain(self, domain_name=None):
        """
        Enables Distribution Status from Edge-location Domain Name.
        Args:
            ** Mandatory **
            domain_name (str) : Cache-server/edge-location domain name
        Returns:
            True (if enabled successfully)
            False (if already enabled)
            False (if domain does not exist)
        Raises:
            False (any client conflict)
        """            
        distributionId_fetch_status, distribution_id_value = self.get_distributionId_by_domain(domain_name)
        if distributionId_fetch_status:
            boto_client = self.create_boto3_client()
            distribution_config = boto_client.get_distribution_config(Id=distribution_id_value)
            if distribution_config['DistributionConfig']['Enabled'] == True:
                print(f"Distribution with domain name {str(domain_name)} is already in enabled state.")
                return False
            distribution_config['DistributionConfig']['Enabled'] = True         
            try:
                boto_client.update_distribution(
                    DistributionConfig=distribution_config['DistributionConfig'],
                    Id = distribution_id_value,
                    IfMatch=distribution_config['ETag']
                )
                print(f"The distribution with Domain Name {str(domain_name)} has been enabled.")
                return True
            except Exception as sdk_error_msg:
                print(sdk_error_msg)
                return False    
        else:
            print("Non-existent Domain received.")
            return False

    def disable_distribution_by_domain(self, domain_name=None):
        """
        Disables Distribution Status from Edge-location Domain Name.
        Args:
            ** Mandatory **
            domain_name (str) : Cache-server/edge-location domain name
        Returns:
            True (if disabled successfully)
            False (if already disabled)
            False (if domain does not exist)
        Raises:
            False (any client conflict)
        """           
        distributionId_fetch_status, distribution_id_value = self.get_distributionId_by_domain(domain_name)
        if distributionId_fetch_status:
            boto_client = self.create_boto3_client()
            distribution_config = boto_client.get_distribution_config(Id=distribution_id_value)
            if distribution_config['DistributionConfig']['Enabled'] == False:
                print(f"Distribution with domain name {str(domain_name)} is already in disabled state.")
                return False            
            distribution_config['DistributionConfig']['Enabled'] = False
            try:
                boto_client.update_distribution(
                    DistributionConfig=distribution_config['DistributionConfig'],
                    Id = distribution_id_value,
                    IfMatch=distribution_config['ETag']
                )
                print(f"The distribution with Domain Name {str(domain_name)} has been disabled.")
                return True
            except Exception as sdk_error_msg:
                print(sdk_error_msg)
                return False    
        else:
            print("Non-existent Domain received.")
            return False    

    def delete_distribution_by_domain(self, domain_name=None):
        """
        Deletes Distribution from Edge-location Domain Name.
        Args:
            ** Mandatory **
            domain_name (str) : Cache-server/edge-location domain name
        Returns:
            True (if deleted successfully)
            False (if domain is enabled)
            False (if domain does not exist)
        Raises:
            False (any client conflict)
        """           
        distributionId_fetch_status, distribution_id_value = self.get_distributionId_by_domain(domain_name)
        if distributionId_fetch_status:
            boto_client = self.create_boto3_client()
            distribution_config = boto_client.get_distribution_config(Id=distribution_id_value)
            if distribution_config['DistributionConfig']['Enabled']:
                print(f"The distribution with Domain Name {str(domain_name)} is currently deployed and cannot be deleted. Please disable it first.")
                return False
            distribution_config = boto_client.get_distribution_config(Id=distribution_id_value)
            try:
                boto_client.delete_distribution(Id=distribution_id_value, IfMatch=distribution_config['ETag'])
                print(f"The distribution with Domain Name {str(domain_name)} has been deleted.")
                return True
            except Exception as sdk_error_msg:
                print(sdk_error_msg)
                return False   
        else:
            print("Non-existent Domain received.")
            return False     

    def update_distribution_by_domain(self, existing_domain_name=None, **config_payload):
        """
        Updates a CloudFront Distribution with specified parameters.
        Args:
            ** Mandatory **
            existing_domain_name (str) : Cache-server/edge-location domain name
        Returns:
            update_flag (bool) : Update Flag (True) // if updated successfully
            update_flag (bool) : Update Flag (False) // Domain does not exist
        Raises:
            update_flag (bool) : Create Flag (False) // Client Conflict
        """        
        distributionId_fetch_status, distribution_id_value = self.get_distributionId_by_domain(existing_domain_name)
        if distributionId_fetch_status:
            boto_client = self.create_boto3_client()
            distribution_config = boto_client.get_distribution_config(Id=distribution_id_value)
            distribution_config['DistributionConfig']['Origins']['Items'][0]['DomainName'] = config_payload.get("origin_domain_name", distribution_config['DistributionConfig']['Origins']['Items'][0]['DomainName'])
            distribution_config['DistributionConfig']['Origins']['Items'][0]['OriginPath'] = config_payload.get("origin_path", distribution_config['DistributionConfig']['Origins']['Items'][0]['OriginPath'])
            distribution_config['DistributionConfig']['HttpVersion'] = [version.lower() for version in config_payload.get("supported_http_versions", [distribution_config['DistributionConfig']['HttpVersion']])][0]
            distribution_config['DistributionConfig']['DefaultCacheBehavior']['AllowedMethods']['Items'] = [method.upper() for method in config_payload.get("allowed_http_methods", [distribution_config['DistributionConfig']['DefaultCacheBehavior']['AllowedMethods']['Items']])]
            distribution_config['DistributionConfig']['PriceClass'] = config_payload.get("price_class", distribution_config['DistributionConfig']['PriceClass'])
            if config_payload.get("cache_policy"):
                new_cache_policy = config_payload.get("cache_policy")
                cache_policy_id_map = {
                    "CachingOptimized":"658327ea-f89d-4fab-a63d-7e88639e58f6",
                    "CachingDisabled":"4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
                    "CachingOptimizedForUncompressedObjects":"b2884449-e4de-46a7-ac36-70bc7f1ddd6d",
                    "Elemental-MediaPackage":"08627262-05a9-4f76-9ded-b50ca2e3a84f",
                    "Amplify":"2e54312d-136d-493c-8eb9-b001f22f67d2"
                    }
                new_cache_policy_id = cache_policy_id_map[str(new_cache_policy)]
                # distribution is configured through cache-policy
                if (distribution_config['DistributionConfig']['DefaultCacheBehavior'].get("CachePolicyId")):
                    distribution_config['DistributionConfig']['DefaultCacheBehavior']['CachePolicyId'] = new_cache_policy_id
                # distribution is configured through TTLs
                else:
                    distribution_config['DistributionConfig']["DefaultCacheBehavior"].pop("DefaultTTL",None)
                    distribution_config['DistributionConfig']["DefaultCacheBehavior"].pop("MinTTL",None)
                    distribution_config['DistributionConfig']["DefaultCacheBehavior"].pop("MaxTTL",None)
                    distribution_config['DistributionConfig']["DefaultCacheBehavior"].pop("ForwardedValues",None)
                    distribution_config['DistributionConfig']['DefaultCacheBehavior']['CachePolicyId'] = new_cache_policy_id
            try:
                boto_client.update_distribution(
                    DistributionConfig=distribution_config['DistributionConfig'],
                    Id = distribution_id_value,
                    IfMatch=distribution_config['ETag']
                )      
                print(f"The distribution with Domain Name {str(existing_domain_name)} has been updated for the provided parameters.")
                return True   
            except Exception as sdk_error_msg:
                print(sdk_error_msg)
                return False  
        else:
            print("Non-existent Domain received.")
            return False