from cloudfront import Cloudfront

class Vendor:
    def __init__(self) -> None:
        self.vendor_class = None

    def create_vendor(self, vendor_name):
        if vendor_name.lower() == "cloudfront":
            self.vendor_class = Cloudfront()
        # elif vendor_name.lower() == "cloudflare":
        #     self.vendor_class = Cloudflare()
        else:
            print(f"Unknown vendor_name: {vendor_name}")
        return self.vendor_class